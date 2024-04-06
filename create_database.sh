#!/bin/bash

# Create a database for bike parking data

# Check if the correct number of arguments is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <database>"
    exit 1
fi
database=$1

# Determine the path to the SQL script
script_dir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
sql_script="$script_dir/modules/create_tables.sql"

# Check if the database already exists
if [ -f "$database" ]; then
    echo "Error: Database '$database' already exists."
    exit 1
fi

# Check if the SQL script exists
if [ ! -f "$sql_script" ]; then
    echo "Error: SQL script '$sql_script' not found."
    exit 1
fi

# Create the SQLite database and run the SQL script to create tables
sqlite3 "$database" < "$sql_script"

echo "Done."
