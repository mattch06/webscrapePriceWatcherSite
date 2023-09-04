#!/bin/sh
set -e

# Wait for the Flask app to be up
while ! nc -z flask-app 5000; do
    echo "Waiting for the Flask app to start..."
    sleep 1
done

# Wait for the PostgreSQL database to be up
while ! nc -z postgres 5432; do
    echo "Waiting for the PostgreSQL database to start..."
    sleep 1
done

# Sleep for an additional delay if needed
sleep 20

# Run the specified command
echo "Executing command: $@"
exec "$@"
