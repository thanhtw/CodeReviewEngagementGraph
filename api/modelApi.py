import os
from transformers import BertForSequenceClassification, BertTokenizer
from flask import Flask, request, jsonify

# Flask 應用初始化
app = Flask(__name__)

# 模型路徑 - 使用當前腳本所在目錄
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(BASE_DIR, "models", "saved_model")
# 加載保存的模型與分詞器
try:
    model = BertForSequenceClassification.from_pretrained(model_path)
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model.eval()  # 設置為推理模式
    print("模型載入成功，已切換為推理模式！")
except Exception as e:
    print(f"模型載入失敗：{e}")
    raise
 
# Flask API 路由邏輯
@app.route("/")
def index():
    return "模型已初始化，可以執行推理請求！" 
                                                                                                                                                                            
if __name__ == "__main__":
    app.run(debug=True, port=5001)