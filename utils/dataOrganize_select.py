import json
import os
from collections import defaultdict

def read_json_file(file_path):
    """讀取 JSON 檔案並回傳內容。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(data, file_path):
    """寫入 JSON 檔案，確保格式美觀。"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def organize_data(input_data):
    """整理所有作業 (HW1~HW7) 為標準格式。"""
    assignment_dict = defaultdict(lambda: defaultdict(lambda: {   
        "Assignment": "",
        "Author_Name": "",
        "Reviewer_Name": "",
        "Round": []
    }))

    for record in input_data:
        assignment_name = record.get("Assignment", "Unknown")
        author_name = record["Author_Name"]
        reviewer_name = record["Reviewer_Name"]

        key = (author_name, reviewer_name)

        # 初始化基本結構
        if not assignment_dict[assignment_name][key]["Assignment"]:
            assignment_dict[assignment_name][key]["Assignment"] = assignment_name
            assignment_dict[assignment_name][key]["Author_Name"] = author_name
            assignment_dict[assignment_name][key]["Reviewer_Name"] = reviewer_name

        # 將 Round 資料加入對應的 reviewer-author pair
        assignment_dict[assignment_name][key]["Round"].append({
            "Round": record["Round"],
            "Time": record["Time"],
            "Feedback": record["Feedback"],
            "Score": record["Score"],
            "Metrics": record["Metrics"],
            "Category": record["Category"],
            "Label": record["Label"],
        })

    return {assignment: list(records.values()) for assignment, records in assignment_dict.items()}

def filter_assignments(organized_data, start_hw, end_hw):
    """根據範圍篩選 HW 資料 (例如 HW1 ~ HW3)。"""
    filtered_data = {}
    
    for hw in range(start_hw, end_hw + 1):
        key = f"HW{hw}"
        if key in organized_data:
            filtered_data[key] = organized_data[key]
    
    return filtered_data

def main():
    input_file = '../data/processing/1111test_64_addscore.json'
    input_data = read_json_file(input_file)
    organized_data = organize_data(input_data)

    # **使用者輸入範圍 (範例: HW1~HW3 或 HW2~HW7)**
    #user_input = input("請輸入 HW 範圍 (格式: HW1~HW3): ").strip()
    start_hw, end_hw = 1, 7

    selected_data = filter_assignments(organized_data, start_hw, end_hw)

    # 確保輸出資料夾存在
    output_dir = "./processed_data"
    os.makedirs(output_dir, exist_ok=True)

    # 存成單一 JSON
    output_file = os.path.join(output_dir, "selected_assignments_addscore.json")
    write_json_file(selected_data, output_file)
    print(f"✅ 已儲存: {output_file}")

if __name__ == "__main__":
    main()