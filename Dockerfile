# Use an official Python 3.10 runtime as a base image
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y netcat-traditional

# Copy the rest of the application code into the container
COPY . .

# Expose the port the app runs on
EXPOSE 5000

# Set the Flask app environment variable
ENV FLASK_APP=main.py

# Command to run the Flask app
ENTRYPOINT ["sh", "/app/App_entrypoint.sh", "flask", "run", "--host=0.0.0.0"]
