import os
import sys
import time
import threading
import scrape_tools.webscrape as webscrape
import json

# Add the path to the root directory to sys.path
sys.path.append(os.path.abspath('.'))

def read_urls_from_file(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file]
    return urls

def run_webscrape():
    config_path = 'config.json'  # Adjust the path to reach the config.json file
    env = os.environ.get('FLASK_ENV', 'development')

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    db_uri = config[env]['DATABASE_URI']
    urls = read_urls_from_file('urls.txt')
    webscrape.scrape_and_update(urls, db_uri)
        
    time.sleep(86400)  # 1 day

if __name__ == "__main__":
    thread = threading.Thread(target=run_webscrape)
    thread.start()
