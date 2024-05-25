#!/bin/bash

# Variables
DB_NAME="db_name"
DB_OWNER="popanegra3"
PG_USER="postgres"

# Drop the database if it exists
psql -U $PG_USER -c "DROP DATABASE IF EXISTS $DB_NAME;"

# Create the database
psql -U $PG_USER -c "CREATE DATABASE $DB_NAME;"

# Change the owner of the database
psql -U $PG_USER -c "ALTER DATABASE $DB_NAME OWNER TO $DB_OWNER;"

# Grant all privileges to the specified user
psql -U $PG_USER -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_OWNER;"

echo "Database operations completed successfully."
