# from inference import load_model, predict_with_threshold
# import torch
# import pandas as pd

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model_path = "../models/3label_finetuned_model"
# model, tokenizer = load_model(model_path, device)

# # data_path = "../data/processing/data64_inference.csv"
# json_input = {
#     "texts": [
#         "有 但可以把小數點縮成兩位",
#         "good",
#         "大致上沒有問題",
#         "是",
#         "整齊",
#         "沒完成。 若有完成作業，也許是最後修改的檔案你忘記再push一次",
#         "排版有符合作業要求",
#         "忘記打註解了",
#         "整齊但tab沒有照規定",
#         "連印出Hello World! 都沒辦法",
#         "印不出來喔，System.out.println的S要大寫",
#         "HelloWorld 下面要加一下註解 /****@param args (這裡加變數說明)*/",
#         "整齊，google checks檢查沒問題",
#         "有轉換成功，不過題目要求變數宣告要是 int (整數型態)，且不用再另外開一個 .java 檔，src 內已經有 Temperature.java"
#     ]
# }
# # 推論函數：包含閾值調整
# label_names = ["relevance", "concreteness", "constructive"]
# label_thresholds = {
#     "relevance": 0.5,
#     "concreteness": 0.5,
#     "constructive": 0.7
# }

# predictions, confidences = predict_with_threshold(
#     model, tokenizer, device, json_input, label_thresholds, label_names
# )
# #results = predict_with_threshold(model, tokenizer, device, json_input, threshold)

# results = []

# for text, pred_indices, conf_list in zip(json_input["texts"], predictions, confidences):
#     # 將二進制索引轉換為標籤名稱
#     labels = [label_names[i] for i, val in enumerate(pred_indices) if val == 1]
#     # 保留置信度（可選：只保留被激活標籤的置信度）
#     label_conf = {
#         label_names[i]: f"{conf:.2f}" 
#         for i, conf in enumerate(conf_list) 
#         if pred_indices[i] == 1
#     }
    
#     results.append({
#         "text": text,
#         "labels": labels,
#         "confidence": label_conf  # 或直接使用 conf_list 保留所有標籤置信度
#     })

# for result in results:
#     print(f"文本: {result['text']}")
#     print(f"預測標籤: {', '.join(result['labels']) if result['labels'] else '無標籤'}")
#     print(f"置信度: {result['confidence']}\n{'-'*30}")

import json
import torch
import pandas as pd
from inference import load_model, batch_predict, find_uncertain_predictions

def process_json_with_predictions(input_path, output_path, model_path, device):
    print(f"開始處理 JSON 資料...")
    print(f"輸入檔案: {input_path}")
    print(f"輸出檔案: {output_path}")
    print(f"模型路徑: {model_path}")
    print(f"使用'建議'關鍵字規則強化建設性標籤")
    
    model, tokenizer = load_model(model_path, device)

    label_thresholds = {
        "relevance": 0.5,
        "concreteness": 0.5,
        "constructive": 0.7
    }

    thresholds_list = [
        label_thresholds["relevance"],
        label_thresholds["concreteness"],
        label_thresholds["constructive"]
    ]

    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"讀取到 {len(data)} 個作業")
    
    total_assignments = sum(len(assignments) for assignments in data.values())
    print(f"總計 {total_assignments} 個 assignment")
    
    processed_count = 0
    
    # 用於儲存所有推論結果的列表
    all_results = []
    all_texts = []
    all_predictions = []

    for hw_key in data:  # e.g., "HW1"
        assignments = data[hw_key]
        print(f"處理 {hw_key}: {len(assignments)} 個 assignment")
        
        for assignment in assignments:
            feedbacks = [r.get('Feedback', '') for r in assignment.get('Round', [])]
            predictions = batch_predict(
                model, 
                tokenizer, 
                device, 
                feedbacks,
                thresholds=thresholds_list,
                batch_size=32
            )
            
            # 收集所有文本和預測結果用於分析
            all_texts.extend(feedbacks)
            all_predictions.extend(predictions)
            
            for round_entry, pred in zip(assignment.get('Round', []), predictions):
                # 更新原始資料結構
                round_entry.update({
                    "Relevance": int(pred["relevance"]),
                    "Concreteness": int(pred["concreteness"]),
                    "Constructive": int(pred["constructive"])
                })
                
                # 收集詳細結果用於CSV
                result_record = {
                    "homework": hw_key,
                    "assignment_id": assignment.get('AssignmentID', ''),
                    "feedback": round_entry.get('Feedback', ''),
                    "relevance": int(pred["relevance"]),
                    "concreteness": int(pred["concreteness"]),
                    "constructive": int(pred["constructive"]),
                    "relevance_confidence": float(pred["relevance_confidence"]),
                    "concreteness_confidence": float(pred["concreteness_confidence"]),
                    "constructive_confidence": float(pred["constructive_confidence"])
                }
                all_results.append(result_record)
            
            processed_count += 1
            if processed_count % 50 == 0:
                print(f"已處理 {processed_count}/{total_assignments} 個 assignment")
    
    # 保存原始JSON結果
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 生成CSV檔案
    csv_output_path = output_path.replace('.json', '_detailed_results.csv')
    try:
        df = pd.DataFrame(all_results)
        df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
        print(f"詳細結果已保存到CSV: {csv_output_path}")
    except NameError:
        print("警告: pandas 未安裝，跳過CSV生成")
        # 手動生成CSV
        import csv
        with open(csv_output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
            if all_results:
                fieldnames = all_results[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(all_results)
        print(f"詳細結果已保存到CSV: {csv_output_path}")
    
    # 找出檢測錯誤的範例
    print("\n=== 尋找可疑的檢測結果 ===")
    uncertain_cases = find_uncertain_predictions(all_texts, all_predictions)
    
    # 輸出各類型的前5個範例
    for case_type, cases in uncertain_cases.items():
        print(f"\n--- {case_type.upper()} (前5個範例) ---")
        for i, case in enumerate(cases[:5]):
            print(f"{i+1}. 文本: {case['text'][:100]}{'...' if len(case['text']) > 100 else ''}")
            pred = case['predictions']
            print(f"   預測: R={pred['relevance']}({pred['relevance_confidence']:.3f}), "
                  f"C={pred['concreteness']}({pred['concreteness_confidence']:.3f}), "
                  f"Co={pred['constructive']}({pred['constructive_confidence']:.3f})")
            
            if case_type == "low_confidence":
                print(f"   最低信心分數: {case['min_confidence']:.3f}")
            elif case_type == "conflicting_labels":
                print(f"   信心分數範圍: {case['confidence_range']:.3f}")
            elif case_type == "keyword_override":
                print(f"   原始建設性信心分數: {case['original_confidence']:.3f}")
            elif case_type == "high_confidence_negative":
                print(f"   {case['label_type']} 高信心負預測: {case['confidence']:.3f}")
            print()
        
        if len(cases) > 5:
            print(f"   ... 還有 {len(cases) - 5} 個類似案例")
        print(f"總計 {len(cases)} 個 {case_type} 案例")
    
    print(f"\n處理完成！共處理 {processed_count} 個 assignment")
    print(f"JSON結果已保存到: {output_path}")
    print(f"CSV詳細結果已保存到: {csv_output_path}")

def generate_error_analysis_report(all_texts, all_predictions, output_prefix="error_analysis"):
    """
    生成詳細的檢測錯誤分析報告
    """
    uncertain_cases = find_uncertain_predictions(all_texts, all_predictions)
    
    # 生成錯誤分析CSV
    error_analysis_data = []
    
    for case_type, cases in uncertain_cases.items():
        for case in cases:
            pred = case['predictions']
            record = {
                'error_type': case_type,
                'text': case['text'],
                'relevance': pred['relevance'],
                'concreteness': pred['concreteness'],
                'constructive': pred['constructive'],
                'relevance_confidence': pred['relevance_confidence'],
                'concreteness_confidence': pred['concreteness_confidence'],
                'constructive_confidence': pred['constructive_confidence'],
                'text_length': len(case['text']),
                'contains_suggestion': '建議' in case['text']
            }
            
            # 添加特定分析字段
            if case_type == "low_confidence":
                record['min_confidence'] = case['min_confidence']
            elif case_type == "conflicting_labels":
                record['confidence_range'] = case['confidence_range']
            elif case_type == "keyword_override":
                record['original_constructive_confidence'] = case['original_confidence']
            elif case_type == "high_confidence_negative":
                record['negative_label_type'] = case['label_type']
                record['negative_confidence'] = case['confidence']
            
            error_analysis_data.append(record)
    
    # 保存錯誤分析CSV
    error_csv_path = f"{output_prefix}_error_cases.csv"
    try:
        df_errors = pd.DataFrame(error_analysis_data)
        df_errors.to_csv(error_csv_path, index=False, encoding='utf-8-sig')
        print(f"錯誤分析報告已保存到: {error_csv_path}")
    except NameError:
        # 手動生成CSV
        import csv
        if error_analysis_data:
            with open(error_csv_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = error_analysis_data[0].keys()
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(error_analysis_data)
            print(f"錯誤分析報告已保存到: {error_csv_path}")
    
    # 生成統計摘要
    summary_path = f"{output_prefix}_summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=== 檢測錯誤分析摘要 ===\n\n")
        
        total_predictions = len(all_predictions)
        f.write(f"總預測數量: {total_predictions}\n\n")
        
        for case_type, cases in uncertain_cases.items():
            f.write(f"{case_type.upper()}: {len(cases)} 個案例 ({len(cases)/total_predictions*100:.1f}%)\n")
            
            if cases:
                f.write("範例:\n")
                for i, case in enumerate(cases[:3]):  # 前3個範例
                    pred = case['predictions']
                    f.write(f"{i+1}. {case['text'][:80]}{'...' if len(case['text']) > 80 else ''}\n")
                    f.write(f"   R={pred['relevance']}({pred['relevance_confidence']:.3f}), "
                           f"C={pred['concreteness']}({pred['concreteness_confidence']:.3f}), "
                           f"Co={pred['constructive']}({pred['constructive_confidence']:.3f})\n")
                f.write("\n")
        
        # 整體統計
        all_confidences = []
        for pred in all_predictions:
            all_confidences.extend([
                pred['relevance_confidence'],
                pred['concreteness_confidence'], 
                pred['constructive_confidence']
            ])
        
        avg_confidence = sum(all_confidences) / len(all_confidences)
        low_confidence_count = sum(1 for c in all_confidences if c < 0.6)
        
        f.write(f"平均信心分數: {avg_confidence:.3f}\n")
        f.write(f"低信心分數(<0.6)比例: {low_confidence_count}/{len(all_confidences)} ({low_confidence_count/len(all_confidences)*100:.1f}%)\n")
    
    print(f"統計摘要已保存到: {summary_path}")
    return uncertain_cases

if __name__ == "__main__":
    input_json = "../utils/processed_data/selected_assignments_addscore.json"
    output_json = "3labeled_processed_totalData11.json"
    model_path = "../models/3label_finetuned_model"
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    print("=== 開始執行推論和分析 ===")
    process_json_with_predictions(input_json, output_json, model_path, device)
    
    print("\n=== 生成詳細錯誤分析報告 ===")
    # 重新讀取結果進行詳細分析
    try:
        # 如果需要更詳細的錯誤分析，可以重新載入數據
        print("錯誤分析已在主處理過程中完成")
        print("請查看生成的CSV檔案和終端輸出的錯誤範例")
    except Exception as e:
        print(f"生成錯誤分析時發生錯誤: {e}")
    
    print("\n=== 執行完成 ===")
    print("生成的檔案:")
    print("1. JSON結果檔案 (含標籤預測)")
    print("2. CSV詳細結果檔案 (含信心分數)")
    print("3. 終端輸出的錯誤檢測範例")
