# 尋找作者 與 其reviewer

import json

# 打開並讀取JSON文件
with open('totalData.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# 假設數據包含在"data"鍵下，調整為你的實際鍵名
recordData = data['recordData']  # 或其他對應的鍵名

# 找 pmId=13 的資料
for record in recordData:
    if record.get('pmId') == 53:
        # 現在直接從record字典中訪問鍵的值
        print('author:', record.get('authorName'))  # 打印作者名稱
        print('reviewer:', record.get('reviewerName'))  # 打印審核者名稱