#!/bin/bash

# Create a database for bike parking data

# Check if the correct number of arguments is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <database>"
    exit 1
fi
database=$1

# Check if the database already exists
if [ -f "$database" ]; then
    echo "Error: Database '$database' already exists."
    exit 1
fi

# Create the SQLite database and run the SQL script to create tables
sqlite3 "$database" < create_tables.sql

echo "Done."
