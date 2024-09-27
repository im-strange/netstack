import csv
import json

# Function to convert CSV to JSON
def csv_to_json(csv_file_path, json_file_path):
    data = {}

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as csvfile:
        csv_reader = csv.reader(csvfile)
        
        # Skip the header if there is one
        next(csv_reader)

        # Iterate through rows in the CSV
        for row in csv_reader:
            if len(row) >= 3:  # Ensure there are at least 3 columns
                key = row[1]  # 2nd column
                value = row[2]  # 3rd column
                data[key] = value

    # Write the data to a JSON file
    with open(json_file_path, 'w', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

# Example usage
if __name__ == "__main__":
    csv_file_path = input("Enter the path to the CSV file: ")
    json_file_path = input("Enter the path to save the JSON file: ")
    csv_to_json(csv_file_path, json_file_path)
