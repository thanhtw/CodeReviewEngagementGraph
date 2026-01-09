import json
from collections import defaultdict

def read_json_file(file_path):
    """Read and return the content of a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as file:
        print('read file success')
        return json.load(file)

def write_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def filter_and_organize_data(input_data, target_aId):
    filtered_data = [record for record in input_data if record['Reviewer_ID'] == target_aId]
    print(type(input_data))  # 確保是 list
    print(input_data[:2])    # 看前兩筆資料長什麼樣
    return {"recordData": filtered_data}

def organize_data(input_data):
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

        if not assignment_dict[assignment_name][key]["Assignment"]:
            assignment_dict[assignment_name][key]["Assignment"] = assignment_name
            assignment_dict[assignment_name][key]["Author_Name"] = author_name
            assignment_dict[assignment_name][key]["Reviewer_Name"] = reviewer_name

        # 將 Round 資料加入對應的 reviewer-author pair
        assignment_dict[assignment_name][key]["Round"].append({
            "Round": record["Round"],
            "Time": record["Time"],
            "Feedback": record["Feedback"],
            "Metrics": record["Metrics"],
            "Category": record["Category"],
            "Label": record["Label"],
        })
    return assignment_dict

def main():
    input_file = '../data/processing/1131test_64.json'
    input_data = read_json_file(input_file)
    organized_data = organize_data(input_data)

    for assignment, records in organized_data.items():
        output_file = f"{assignment}.json"

        # 轉換 defaultdict 為一般 list 儲存
        records_list = list(records.values())

        write_json_file(records_list, output_file)
        print(f"File written: {output_file}")
    

if __name__ == "__main__":
    main()
