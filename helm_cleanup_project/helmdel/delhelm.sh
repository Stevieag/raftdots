#!/bin/bash

while IFS= read -r line; do
  # Extract the release name (in quotes) and date
  if [[ $line =~ \"([^\"]+)\".*\"([0-9-]+)$ ]]; then
    name="${BASH_REMATCH[1]}"
    date="${BASH_REMATCH[2]}"
    
    # Calculate age in days
    age=$(( ($(date +%s) - $(date -d "$date" +%s)) / 86400 ))
    
    echo "Name: $name, Age: $age days"
  fi
done << EOL
helm uninstall "workflow-builder-rfyap8-db-be","default","1","2024-09-06
helm uninstall "workflow-builder-rfyap8-fe","default","4","2024-09-16
helm uninstall "workflow-builder-rfyap8-rabbitmq","default","4","2024-09-16
helm uninstall "workflow-builder-rfyap8-redis","default","4","2024-09-16
helm uninstall "workflow-builder-venmdf-db-be","default","1","2024-09-18
EOL
