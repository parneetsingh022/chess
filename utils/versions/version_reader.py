import json

def read_version_from_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data.get('version')

# Example usage
if __name__ == "__main__":
    version = read_version_from_file('release-info.json')
    print(f"Version: {version}")