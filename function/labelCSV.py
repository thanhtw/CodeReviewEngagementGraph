from inference import load_model, predict_with_threshold
import torch
import pandas as pd
from tqdm import tqdm  # 進度條

def main():
    # 模型初始化
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_path = "../models/roberta-smote-10fold-chinese_iteration_3"
    model, tokenizer = load_model(model_path, device)

    data_path = "../data/homework/1131_rr.csv"
    df = pd.read_csv(data_path, on_bad_lines="skip")
    print(df.head())

    if 'feedback' not in df.columns:
        raise ValueError("資料中缺少 'feedback' 欄位！")

    required_features = {'id', 'feedback'}
    if not required_features.issubset(df.columns):
        raise ValueError(f"缺少欄位 {required_features - set(df.columns)}")

    # 處理 NaN（空值設為 ""，以便推理）
    df['feedback'] = df['feedback'].fillna("").astype(str)

    # 加入 tqdm 進度條
    print("開始推論...")
    batch_size = 32  # 避免 OOM，改用 batch 處理
    predictions = []
    confidences = []

    for i in tqdm(range(0, len(df), batch_size), desc="推論中"):
        batch_feedbacks = df['feedback'].iloc[i:i+batch_size].tolist()
        batch_preds, batch_confs = predict_with_threshold(
            model, tokenizer, device, {"texts": batch_feedbacks}, threshold=0.8
        )
        predictions.extend(batch_preds)
        confidences.extend(batch_confs)

    # 存回
    df['prediction'] = predictions
    df['confidence'] = confidences
    output_path = "../data/homework/1131_Labelrr.csv"
    df[['id', 'feedback', 'prediction', 'confidence']].to_csv(output_path, index=False)
    
    print(f"推論結果已保存到 {output_path}")

if __name__ == "__main__":
    main()