import subprocess
import datetime
import json
import pytz

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    return output.decode('utf-8')

def get_helm_releases():
    output = run_command("helm list -A -o json")
    return json.loads(output)

def parse_helm_date(date_string):
    # Remove the fractional seconds and UTC indicator
    date_string = date_string.split('.')[0] + ' UTC'
    return datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S %Z").replace(tzinfo=pytz.UTC)

def should_delete(release):
    # Example: Delete releases older than 30 days
    release_date = parse_helm_date(release['updated'])
    age = datetime.datetime.now(pytz.UTC) - release_date
    return age.days > 30

def delete_release(release):
    namespace = release['namespace']
    name = release['name']
    #run_command(f"nstall {name} -n {namespace}")
    print(f"Deleted release: {name} in namespace: {namespace}")

def main():
    releases = get_helm_releases()
    for release in releases:
        if should_delete(release):
            delete_release(release)

if __name__ == "__main__":
    main()
