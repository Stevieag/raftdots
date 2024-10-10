import json
import time
import subprocess
from datetime import datetime

def date_to_seconds(date_string):
    """
    Given a date string in the format '%Y-%m-%d %H:%M:%S %Z', return the corresponding
    timestamp in seconds since the epoch. If the input string is not in this format,
    return 0.
    """
    date_string = date_string.split('.')[0].replace(' UTC', '')
    try:
        dt = datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return int(dt.timestamp())
    except ValueError:
        return 0

def get_base_name(name):
    """
    Given a Helm release name, return its "base name" (i.e. the part before the
    incrementing number). For example, if the release name is "myapp-123", the
    base name is "myapp". If the release name does not end with a number, the
    base name is the same as the release name.
    """
    parts = name.split('-')
    if len(parts) > 4:
        parts = parts[:-1]
    return '-'.join(parts)

def uninstall_release(name, namespace):
    """
    Uninstall a Helm release.

    This function prints a message indicating that the release is being
    uninstalled, and then runs the `helm uninstall` command with the
    appropriate arguments. By default, the command is not actually run,
    since the line is commented out. To actually uninstall the release,
    uncomment the line.
    """
    #print(f"Uninstalling release {name} in namespace {namespace}")
    ## Uncomment the following line to actually uninstall
    #subprocess.run(['helm', 'uninstall', name, '-n', namespace], check=True)

def get_helm_releases():
    """
    Return a list of all Helm releases in the default namespace, as a JSON blob.

    This function runs the command `helm list --namespace default --all --output json` and
    returns the result as a JSON object.
    """
    result = subprocess.run(['helm', 'list', '--namespace', 'default', '--all', '--output', 'json'], 
                            capture_output=True, text=True, check=True)
    return json.loads(result.stdout)

current_time = int(time.time())

releases = get_helm_releases()

oldest_releases = {}
release_counts = {}

# First pass: identify the latest release for each base name and namespace and count releases
for release in releases:
    name = release['name']
    namespace = release['namespace']
    updated = release['updated']
    base_name = get_base_name(name)
    key = f"{base_name}__{namespace}"
    current_oldest = oldest_releases.get(key)
    release_time = date_to_seconds(updated)
    if release_time == 0:
        print(f"Warning: Could not parse date for release {name}. Skipping.")
        continue
    if current_oldest is None or release_time > date_to_seconds(current_oldest['updated']):
        oldest_releases[key] = release
    release_counts[key] = release_counts.get(key, 0) + 1

# Second pass: process and delete releases
for release in releases:
    name = release['name']
    namespace = release['namespace']
    release_status = release['status']
    updated = release['updated']
    base_name = get_base_name(name)
    release_time = date_to_seconds(updated)
    if release_time == 0:
        print(f"Warning: Could not parse date for release {name}. Skipping.")
        continue
    age_days = (current_time - release_time) // 86400

    key = f"{base_name}__{namespace}"

    if release_counts[key] == 1:
        print(f"Retaining sole instance of {name} (base: {base_name}) in namespace {namespace}")
        continue

    if release_status == 'failed':
        print(f"Found failed release {name} in namespace {namespace}")
        uninstall_release(name, namespace)
        continue

    if age_days <= 7:
        print(f"Retaining release {name} (base: {base_name}) in namespace {namespace} (age: {age_days} days)")
        continue

    oldest_release = oldest_releases.get(key)
    if oldest_release and release_time == date_to_seconds(oldest_release['updated']):
        print(f"Retaining latest release {name} (base: {base_name}) in namespace {namespace}")
        continue

    print(f"Uninstalling release {name} (base: {base_name}) in namespace {namespace} (age: {age_days} days)")
    uninstall_release(name, namespace)

# Uncomment the following lines if you want to generate a CSV output
# import csv
# with open('outputnow.csv', 'w', newline='') as f:
#     writer = csv.writer(f)
#     writer.writerow(["name", "namespace", "revision", "updated", "status", "chart", "app_version"])
#     for release in releases:
#         writer.writerow([release['name'], release['namespace'], release['revision'], 
#                          release['updated'], release['status'], release['chart'], release['app_version']])