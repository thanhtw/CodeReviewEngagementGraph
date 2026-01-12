# Find author and their reviewer

import json

# Open and read JSON file
with open('totalData.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Assuming data is contained under "data" key, adjust to your actual key name
recordData = data['recordData']  # or other corresponding key name

# Find data where pmId=13
for record in recordData:
    if record.get('pmId') == 53:
        # Now access key values directly from record dict
        print('author:', record.get('authorName'))  # Print author name
        print('reviewer:', record.get('reviewerName'))  # Print reviewer name