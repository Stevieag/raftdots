import json
import requests
from packaging import version

def get_license(package_name, package_version):
    url = f"https://pypi.org/pypi/{package_name}/{package_version}/json"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['info'].get('license', 'License not specified')
    return None

def process_sbom(sbom_file):
    with open(sbom_file, 'r') as f:
        data = json.load(f)
    
    for component in data['components']:
        name = component['name']
        ver = component['version']
        
        license_info = get_license(name, ver)
        if license_info:
            component['license'] = license_info
        else:
            print(f"Failed to fetch license for {name} {ver}")

    return data

# Usage
updated_sbom = process_sbom('sbom.json')

# Save the updated SBOM
with open('updated_sbom.json', 'w') as f:
    json.dump(updated_sbom, f, indent=2)
