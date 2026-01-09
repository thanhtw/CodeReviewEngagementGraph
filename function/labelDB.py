import pymysql
import mysql.connector
import pandas as pd
import torch
from inference import load_model, predict_with_threshold
from mysql.connector import Error

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "../models/roberta-smote-10fold-chinese_iteration_3"
model, tokenizer = load_model(model_path, device)

def db_connection():
    try:
        connection = mysql.connector.connect(
            host="140.134.25.64",  # 替換為你的 MySQL 主機名稱或 IP 地址
            port=33541,            # 替換為你的 MySQL 連接埠號
            user="root",           # 替換為你的 MySQL 使用者名稱
            password="Asdfghjk3839",  # 替換為你的 MySQL 密碼
            database="ProgEdu64"   # 替換為你想連接的資料庫名稱
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"連接資料庫時發生錯誤：{e}")
        return None

def read_feedback():
    connection = db_connection()
    feedbacks = []
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT feedback FROM Review_Record;")
        feedbacks = [row[0] for row in cursor.fetchall()]
        print(f"成功讀取 {len(feedbacks)} 條 feedback 資料")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return feedbacks

# 預測函式
def predict_feedback(feedbacks, batch_size=64):
    predictions = []

    # 將每條 feedback 編碼並送入模型
    predictions = []
    for i in range(0, len(feedbacks), batch_size):
        batch_feedbacks = feedbacks[i:i+batch_size]
        
        # Tokenize 批次
        inputs = tokenizer(
            batch_feedbacks,
            padding="max_length",
            truncation=True,
            max_length=128,  # 調整為模型的最大長度
            return_tensors="pt"  # 返回 PyTorch tensors
        )
        
        # 模型推論
        model.eval()
        with torch.no_grad():
            outputs = model(**inputs)

        # 批次分類結果
        logits = outputs.logits
        batch_predictions = torch.argmax(logits, dim=1).tolist()
        predictions.extend(zip(batch_feedbacks, batch_predictions))
        
        # 日誌：追蹤進度
        print(f"已處理 {i+len(batch_feedbacks)}/{len(feedbacks)} 條資料")
    
    return predictions

# 將label結果寫入資料庫
def write_predictions_to_db(predictions):
    connection = db_connection()
    try:
        cursor = connection.cursor()
        
        # 確保 Review_Record 表有 predicted_label 欄位
        cursor.execute("SHOW COLUMNS FROM Review_Record LIKE 'predicted_label';")
        result = cursor.fetchone()

        # 如果欄位不存在，則新增欄位
        if result is None:
            cursor.execute("ALTER TABLE Review_Record ADD COLUMN predicted_label INT;")
            print("新增 predicted_label 欄位成功。")
        
        # 更新資料庫中的預測結果
        for feedback, predicted_label in predictions:
            cursor.execute("""
                UPDATE Review_Record 
                SET predicted_label = %s 
                WHERE feedback = %s
            """, (predicted_label, feedback))
        
        connection.commit()
        print(f"成功將預測結果寫入資料庫！")
    
    except mysql.connector.Error as e:
        print(f"寫入資料庫時發生錯誤：{e}")
    finally:
        cursor.close()
        connection.close()
        print("資料庫連線已關閉。")

if __name__ == "__main__":
    # 1. 讀取資料庫資料
    feedbacks = read_feedback()

    # 2. 使用模型進行分類
    results = predict_feedback(feedbacks)

    # 3. 選擇輸出或寫入資料庫
    print("推論結果（前 5 筆）：")
    for feedback, label in results[:5]:  # 僅輸出前 5 筆
        print(f"Feedback: {feedback}\nPredicted Label: {label}\n")

    # 如果需要，將結果寫入資料庫
    write_predictions_to_db(results)