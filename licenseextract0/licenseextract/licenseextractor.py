import requests
import json
import sys

def get_package_info(package, version=None):
    if version:
        url = f"https://pypi.org/pypi/{package}/{version}/json"
    else:
        url = f"https://pypi.org/pypi/{package}/json"
    
    headers = {"Accept": "application/json"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        info = data['info']
        
        extracted_info = {
            "Name": info.get('name'),
            "Version": info.get('version'),
            "Author": info.get('author'),
            "Author_Email": info.get('author_email'),
            "Licence": info.get('license'),
            "Maintainer": info.get('maintainer'),
            "Maintainer_Email": info.get('maintainer_email'),
            "Package_Url": info.get('package_url'),
            "Project_Url": info.get('project_url')
        }
        
        return extracted_info
    else:
        return f"Error: {response.status_code}"

def process_requirements(input_file, output_file):
    with open(requirements_file, 'r') as infile, open(output_file, 'w') as outfile:
        for line in infile:
            requirement = line.split()[0]
            parts = requirement.strip().split('==')
            package = parts[0]
            version = parts[1] if len(parts) > 1 else None
            info = get_package_info(package, version)
            print(f"\nPackage: {package}")
            print(json.dumps(info, indent=2))
            outfile.write(f"\nPackage: {package}\n")
            json.dump(info, outfile, indent=2)
            outfile.write("\n")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python script.py <input_requirements.txt> <output_file.txt>")
    else:
        requirements_file = sys.argv[1]
        output_file = sys.argv[2]
        process_requirements(requirements_file, output_file)
        print(f"Package information has been written to {output_file}")