#!/bin/sh
set -e

# Wait for the PostgreSQL database to be up
while ! nc -z postgres 5432; do
    echo "Waiting for the PostgreSQL database to start..."
    sleep 1
done

# Sleep for an additional delay
sleep 5

# Run the specified command
exec "$@"
