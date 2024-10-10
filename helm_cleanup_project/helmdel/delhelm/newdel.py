import csv
import sys
import subprocess
from collections import defaultdict
from datetime import datetime, timezone

# Get the current date in YYYYMMDD format
current_date = datetime.now().strftime("%Y%m%d")

# Construct the filename
filename = f"helmoutput{current_date}.csv"

# Construct the command
command = """
helm list -n default -o json | jq -r '(["name","namespace","revision","updated","status","chart","app_version"] | @csv), (.[] | [.name, .namespace, .revision, .updated, .status, .chart, .app_version] | @csv)'
"""

# Run the command and capture the output
result = subprocess.run(command, shell=True, capture_output=True, text=True)

# Check if the command was successful
if result.returncode == 0:
    # Write the output to the file
    with open(filename, 'w') as f:
        f.write(result.stdout)
    print(f"CSV file created: {filename}")
else:
    print("Error running the command:")
    print(result.stderr)

def group_deployments(file_path):
    deployments = defaultdict(lambda: defaultdict(list))
    current_time = datetime.now(timezone.utc)
    failed_deployments = []
    
    with open(file_path, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            name = row['name']
            name_parts = name.split('-')
            
            if len(name_parts) >= 3:
                main_group = '-'.join(name_parts[:2])
                sub_group = '-'.join(name_parts[:3])
            else:
                main_group = sub_group = name
            
            updated_time = datetime.strptime(row['updated'].split()[0], '%Y-%m-%d').replace(tzinfo=timezone.utc)
            age = (current_time - updated_time).days
            
            if row['status'] == 'failed':
                failed_deployments.append((name, row['namespace']))
            elif age > 8 and sub_group != main_group and sub_group != "vector-email-processing" and main_group != "vector-address" and main_group != "raft-ship":
                deployments[main_group][sub_group].append((row['name'], row['namespace'], row['status'], age))
    
    # Sort deployments by age and remove the latest from each subgroup
    for main_group in deployments:
        for sub_group in deployments[main_group]:
            deployments[main_group][sub_group].sort(key=lambda x: x[3], reverse=True)
            if deployments[main_group][sub_group]:
                deployments[main_group][sub_group] = deployments[main_group][sub_group][1:]
    
    # Remove empty groups and subgroups
    return {k: {sk: sv for sk, sv in v.items() if sv} for k, v in deployments.items() if len(v) > 1 and any(sv for sv in v.values())}, failed_deployments

def print_grouped_deployments(grouped_deployments, failed_deployments):
    for main_group, subgroups in grouped_deployments.items():
        print(f"\n## {main_group}")
        for sub_group, deployments in subgroups.items():
            if deployments:  # Only print non-empty subgroups
                print(f"\n\t### {sub_group}")
                for name, namespace, status, age in deployments:
                    print(f"\t- {name} (Namespace: {namespace}, Status: {status}, Age: {age} days)")
                    print(f"\thel uninstall {name} -n {namespace}")
    
    if failed_deployments:
        print("\n## Failed Deployments to Uninstall")
        for name, namespace in failed_deployments:
            print(f"hel uninstall {name} -n {namespace}")

if __name__ == "__main__":
    file_path = filename
    
    grouped_deployments, failed_deployments = group_deployments(file_path)
    print_grouped_deployments(grouped_deployments, failed_deployments)
    # After processing the CSV file
    print(f"Would you like to retain the CSV file: {filename}")
    user_input = input("Enter 'n' to delete the file, any other key to retain: ")
    if user_input.lower() == 'n':
        subprocess.run(["rm", filename])
        print(f"File {filename} has been deleted.")
    else:
        print(f"File {filename} has been retained.")
