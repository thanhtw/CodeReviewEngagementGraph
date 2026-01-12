import json
import os
from collections import defaultdict

def read_json_file(file_path):
    """Read JSON file and return content."""
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json_file(data, file_path):
    """Write JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def organize_data(input_data):
    """Organize all assignments (HW1~HW7) into standard format."""
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

        # Initialize basic structure
        if not assignment_dict[assignment_name][key]["Assignment"]:
            assignment_dict[assignment_name][key]["Assignment"] = assignment_name
            assignment_dict[assignment_name][key]["Author_Name"] = author_name
            assignment_dict[assignment_name][key]["Reviewer_Name"] = reviewer_name

        # Add Round data to corresponding reviewer-author pair
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
    """Filter HW data based on range (e.g., HW1 ~ HW3)."""
    filtered_data = {}
    
    for hw in range(start_hw, end_hw + 1):
        key = f"HW{hw}"
        if key in organized_data:
            filtered_data[key] = organized_data[key]
    
    return filtered_data

def main():
    input_file = '../data/processing/22data64_inference_converted.json'
    input_data = read_json_file(input_file)
    organized_data = organize_data(input_data)

    # **User input range (example: HW1~HW3 or HW2~HW7)**
    #user_input = input("Enter HW range (format: HW1~HW3): ").strip()
    start_hw, end_hw = 1, 7

    selected_data = filter_assignments(organized_data, start_hw, end_hw)

    # Ensure output folder exists
    output_dir = "./processed_data"
    os.makedirs(output_dir, exist_ok=True)

    # Save as single JSON
    output_file = os.path.join(output_dir, "22selected_assignments_addscore.json")
    write_json_file(selected_data, output_file)
    print(f"✅ Saved: {output_file}")

if __name__ == "__main__":
    main()