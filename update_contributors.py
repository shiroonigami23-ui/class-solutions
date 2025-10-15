import json
import sys
import os

def update_contributors_file(filename, username):
    """
    Adds a new contributor to the contributors.json file.
    """
    filepath = 'contributors.json'
    
    # Initialize with an empty JSON object if the file doesn't exist
    if not os.path.exists(filepath):
        contributors = {}
    else:
        with open(filepath, 'r') as f:
            try:
                contributors = json.load(f)
            except json.JSONDecodeError:
                contributors = {} # Handle case where file is empty or corrupt

    # Add the new entry
    contributors[filename] = username
    
    # Write the updated data back to the file
    with open(filepath, 'w') as f:
        json.dump(contributors, f, indent=2)
        
    print(f"Successfully added {username} as contributor for {filename}.")

if __name__ == "__main__":
    # The script expects two command-line arguments from the GitHub Action
    if len(sys.argv) != 3:
        print("Usage: python update_contributors.py <filename> <username>")
        sys.exit(1)
        
    file_to_add = sys.argv[1]
    user_to_add = sys.argv[2]
    
    update_contributors_file(file_to_add, user_to_add)
