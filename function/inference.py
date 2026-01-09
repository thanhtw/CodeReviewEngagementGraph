import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from typing import List, Dict

# 初始化模型和 tokenizer
def load_model(model_path: str, device: torch.device):
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_path,
        problem_type="multi_label_classification",  # 明確指定多標籤任務
        num_labels=3
    )
    model.to(device)
    model.eval()  # 切換到評估模式
    return model, tokenizer

def batch_predict(
        model, 
        tokenizer, 
        device: torch.device, 
        texts: List[str], 
        thresholds: List[float],
        batch_size: int = 32
) -> List[Dict[str, any]]:  # 批次預測文本 並返回0 1 + 信心分數
    if len(thresholds) != 3:
        raise ValueError("thresholds 必須是長度 3 的列表")
    
    results = []
     

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_size_current = len(batch_texts)
        # 初始化所有位置為預設值 0 和低信心分數
        batch_results = [
            {
                "relevance": 0, "concreteness": 0, "constructive": 0,
                "relevance_confidence": 0.0, "concreteness_confidence": 0.0, "constructive_confidence": 0.0
            }
            for _ in range(batch_size_current)
        ]

        valid_texts = []  # 提取有效的文本
        valid_indices = []

        for idx, text in enumerate(batch_texts):
            if isinstance(text, str) and text.strip():
                valid_texts.append(text)
                valid_indices.append(idx)

        # 若存在有效文本才進行推論
        if valid_texts:
            inputs = tokenizer(
                valid_texts,
                padding=True,
                truncation=True,
                max_length=350,
                return_tensors="pt"
            ).to(device)
            
            with torch.no_grad():
                outputs = model(**inputs)
            
            # 驗證輸出維度
            logits = outputs.logits
            if logits.shape[1] != 3:
                raise ValueError(f"模型輸出的 logits 維度應為 3，實際為 {logits.shape[1]}")
            
            # 計算預測結果和信心分數
            probs = torch.sigmoid(logits).cpu().numpy()
            binary_preds = (probs > thresholds).astype(int)
            
            # 更新有效位置的結果
            for valid_idx, (batch_idx, pred, prob) in enumerate(zip(valid_indices, binary_preds, probs)):
                text = valid_texts[valid_idx]
                
                # 關鍵字規則：如果評論中包含"建議"，將建設性標籤設為1
                constructive_label = int(pred[2])
                constructive_confidence = float(prob[2])
                if "建議" in text:
                    constructive_label = 1
                    # 如果原本信心分數低於閾值但因關鍵字設為1，調整信心分數
                    if constructive_confidence < thresholds[2]:
                        constructive_confidence = max(constructive_confidence, 0.6)  # 設定最低信心分數
                
                batch_results[batch_idx] = {
                    "relevance": int(pred[0]),
                    "concreteness": int(pred[1]),
                    "constructive": constructive_label,
                    "relevance_confidence": float(prob[0]),
                    "concreteness_confidence": float(prob[1]),
                    "constructive_confidence": constructive_confidence
                }
        
        results.extend(batch_results)
    
    return results


def find_uncertain_predictions(
    texts: List[str], 
    predictions: List[Dict[str, any]], 
    low_confidence_threshold: float = 0.6,
    high_confidence_threshold: float = 0.9
) -> Dict[str, List[Dict]]:
    """
    找出可能檢測錯誤的評論範例
    
    Args:
        texts: 原始文本列表
        predictions: 預測結果列表（包含信心分數）
        low_confidence_threshold: 低信心分數閾值
        high_confidence_threshold: 高信心分數閾值
    
    Returns:
        字典包含不同類型的可疑預測範例
    """
    uncertain_cases = {
        "low_confidence": [],      # 信心分數低的案例
        "conflicting_labels": [],  # 標籤衝突的案例（某些標籤高信心，某些低信心）
        "keyword_override": [],    # 被關鍵字規則覆蓋的案例
        "high_confidence_negative": []  # 高信心但預測為負的案例
    }
    
    for i, (text, pred) in enumerate(zip(texts, predictions)):
        if not isinstance(text, str) or not text.strip():
            continue
            
        confidences = [
            pred["relevance_confidence"],
            pred["concreteness_confidence"], 
            pred["constructive_confidence"]
        ]
        labels = [
            pred["relevance"],
            pred["concreteness"],
            pred["constructive"]
        ]
        
        # 檢查低信心分數案例
        min_confidence = min(confidences)
        if min_confidence < low_confidence_threshold:
            uncertain_cases["low_confidence"].append({
                "text": text,
                "predictions": pred,
                "min_confidence": min_confidence,
                "index": i
            })
        
        # 檢查標籤衝突案例（某些標籤高信心，某些低信心）
        max_confidence = max(confidences)
        if max_confidence > high_confidence_threshold and min_confidence < low_confidence_threshold:
            uncertain_cases["conflicting_labels"].append({
                "text": text,
                "predictions": pred,
                "confidence_range": max_confidence - min_confidence,
                "index": i
            })
        
        # 檢查關鍵字覆蓋案例
        if "建議" in text and pred["constructive"] == 1:
            # 如果原始模型信心分數低但被關鍵字規則設為1
            original_confidence = pred["constructive_confidence"]
            if original_confidence < 0.6:  # 假設我們在關鍵字規則中設定的最低信心分數
                uncertain_cases["keyword_override"].append({
                    "text": text,
                    "predictions": pred,
                    "original_confidence": original_confidence,
                    "index": i
                })
        
        # 檢查高信心但預測為負的案例
        for j, (label, confidence) in enumerate(zip(labels, confidences)):
            if label == 0 and confidence > high_confidence_threshold:
                label_names = ["relevance", "concreteness", "constructive"]
                uncertain_cases["high_confidence_negative"].append({
                    "text": text,
                    "predictions": pred,
                    "label_type": label_names[j],
                    "confidence": confidence,
                    "index": i
                })
    
    return uncertain_cases


# 以下是為假資料進行推論
# def predict_with_threshold(model, tokenizer, device, json_input, label_thresholds, label_names):
#     texts = json_input.get("texts", [])
#     if not texts:
#         raise ValueError("JSON input must contain 'texts' key with a list of sentences.")

#     # 處理 NaN（如果有空字串，直接設 label = 0, confidence = 0）
#     results = []
#     valid_texts = []
#     valid_indices = []
#      # 初始化 predictions 和 confidence_scores 為空列表
#     predictions = []
#     confidence_scores = []

#     threshold_list = [label_thresholds[name] for name in label_names]

#     for i, text in enumerate(texts):
#         if text.strip() == "":
#             results.append(([0]*len(label_names), [0.0]*len(label_names)))  # 空文本 -> label 0, confidence 0.0
#         else:
#             valid_texts.append(text)
#             valid_indices.append(i)

#     # 如果沒有有效的文本，不進行模型推論
#     if valid_texts:
#         # 文本轉模型輸入
#         inputs = tokenizer(
#             valid_texts,
#             padding=True,
#             truncation=True,
#             max_length=350,
#             return_tensors="pt"
#         ).to(device)

#         with torch.no_grad():
#             outputs = model(**inputs)

#         # 取得預測結果和信心分數（logits轉為機率）
#         logits = outputs.logits
#         probs = torch.nn.functional.sigmoid(logits)

#         binary_preds = [] 
#         for sample_probs in probs:
#             preds = [
#                 1 if prob > threshold_list[i] else 0 
#                 for i, prob in enumerate(sample_probs)
#             ]
#             binary_preds.append(preds)
            
#         confidence_scores = probs.tolist()  # 每個標籤的置信度列表
#         predictions = binary_preds

#         for idx, (prediction, confidence) in zip(valid_indices, zip(predictions, confidence_scores)):
#             results.insert(idx, (prediction, confidence))

#     # 拆解成兩個 list 回傳
#     final_predictions, final_confidences = zip(*results) if results else ([], [])
#     return list(final_predictions), list(final_confidences)