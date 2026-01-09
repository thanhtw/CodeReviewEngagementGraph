from inference import load_model, batch_predict
import torch
import pandas as pd
from tqdm import tqdm  # 進度條

def main():
    # 模型初始化
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "../models/3label_finetuned_model"
    model, tokenizer = load_model(model_path, device)

    data_path = "../data/homework/1131_rr.csv"
    df = pd.read_csv(data_path, on_bad_lines="skip")
    print(df.head())

    label_names = ["relevance", "concreteness", "constructive"]


    if 'feedback' not in df.columns:
        raise ValueError("資料中缺少 'feedback' 欄位！")

    required_features = {'id', 'feedback'}
    if not required_features.issubset(df.columns):
        raise ValueError(f"缺少欄位 {required_features - set(df.columns)}")

    # 處理 NaN（空值設為 ""，以便推理）
    df['feedback'] = df['feedback'].fillna("").astype(str)

    # 加入 tqdm 進度條
    print("開始推論...")
    print("注意：如果評論中包含'建議'關鍵字，建設性標籤將自動設為1")
    
    batch_size = 32  # 避免 OOM，改用 batch 處理
    all_predictions = []
    
    # 閾值設定
    thresholds = [0.5, 0.5, 0.7]  # relevance, concreteness, constructive
    
    for i in tqdm(range(0, len(df), batch_size), desc="推論中"):
        batch_feedbacks = df['feedback'].iloc[i:i+batch_size].tolist()
        
        # 使用新的 batch_predict 函數
        batch_results = batch_predict(
            model, tokenizer, device, batch_feedbacks, thresholds, batch_size
        )
        all_predictions.extend(batch_results)

    # 將預測結果轉換為 DataFrame 欄位
    for label in label_names:
        df[label] = [pred[label] for pred in all_predictions]


    output_path = "../data/homework/1131_3Labelrr11.csv"
    
    # 輸出欄位：id, feedback, 三個標籤欄位
    cols = ['id', 'feedback'] + label_names
    df_out = df[cols]
    df_out.to_csv(output_path, index=False)
    
    # 統計結果
    total_feedbacks = len(df)
    total_with_suggestion = sum(1 for feedback in df['feedback'] if '建議' in str(feedback))
    
    print(f"推論結果已保存到 {output_path}")
    print(f"總計處理 {total_feedbacks} 筆評論")
    print(f"其中包含'建議'關鍵字的評論: {total_with_suggestion} 筆")
    
    # 顯示標籤統計
    for label in label_names:
        count = df[label].sum()
        percentage = (count / total_feedbacks) * 100
        print(f"{label}: {count} 筆 ({percentage:.1f}%)")

if __name__ == "__main__":
    main()