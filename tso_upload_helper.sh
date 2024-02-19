#!/bin/bash

# Check if a project name is provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <project_name>"
    exit 1
fi

# Assign the first argument to a variable
project_name="$1"

# Capture the output from dx find into a variable
table_output=$(dx find data --name "*.zip" --json --path "${project_name}":results | jq -r '
  ["ID", "Name", "State", "Folder", "Modified", "Size"] as $headers
  | ["---", "---", "---", "---", "---", "---"] as $separator
  | [$headers, $separator] + 
    (map([.id, .describe.name, .describe.state, .describe.folder, (.describe.modified / 1000 | todate), .describe.size]))
  | .[] 
  | @tsv' | column -t)

# Define APP_ID and MOKAGUYS_AUTH_TOKEN
APP_ID="APP_ID"
MOKAGUYS_AUTH_TOKEN="MOKAGUYS_AUTH_TOKEN"

# Now you can manipulate $table_output with awk or any other tool.
# Iterate over the table row by row
while IFS= read -r line; do
  # Skip the header and separator lines
  if [[ "$line" == ID* ]] || [[ "$line" == "---"* ]]; then
    continue
  fi

  # Extract the Name, Folder, and ID using awk
  FILE_NAME=$(echo "$line" | awk '{print $2}')
  FOLDER=$(echo "$line" | awk '{print $4}')
  ID=$(echo "$line" | awk '{print $1}')

  FILE_ID="${FOLDER}/${FILE_NAME}"
  SAMPLE_NAME="${FILE_NAME%.zip}"

  # Print the dx run command
  echo "dx run project-ByfFPz00jy1fk6PjpZ95F27J:$APP_ID --priority high -y --name=$SAMPLE_NAME -isample_name=$SAMPLE_NAME -isample_zip_folder=$project_name:$FILE_ID --project=$project_name --auth $MOKAGUYS_AUTH_TOKEN"

 done <<< "$table_output"