import json

def read_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file {file_path} does not contain valid JSON.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return None
    
def write_json(data, file_path):
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully written to {file_path}")
        return True
    except IOError:
        print(f"Error: Unable to write to file {file_path}")
        return False
    except TypeError as e:
        print(f"Error: Object of type {type(data)} is not JSON serializable")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        return False