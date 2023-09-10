import os
import scrape_tools.webscrape as webscrape
import json
import time
import boto3

BUCKET=os.environ.get('BUCKET')

def read_urls_from_s3(bucket_name, file_name):
    s3 = boto3.client('s3')
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_name)
        urls = [line.decode('utf-8').strip() for line in response['Body'].iter_lines()]
        return urls
    except Exception as e:
        print(f"Error reading URLs from S3: {e}")
        return []

def run_webscrape():
    config_path = 'config.json'  # Adjust the path to reach the config.json file
    env = os.environ.get('FLASK_ENV', 'development')

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    db_uri = config[env]['DATABASE_URI']
    bucket_name = BUCKET
    file_name = 'urls.txt'
    
    urls = read_urls_from_s3(bucket_name, file_name)
    
    if not urls:
        print(f"No URLs found in S3 bucket: {bucket_name}/{file_name}")
        return
    
    webscrape.scrape_and_update(urls, db_uri)
    
    time.sleep(86400)  # 1 day

if __name__ == "__main__":
    run_webscrape()
