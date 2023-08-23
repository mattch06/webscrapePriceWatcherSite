import requests
from bs4 import BeautifulSoup
import random
import time
from sqlalchemy.orm import sessionmaker
from website.models import GPU, Price
from sqlalchemy import create_engine


user_agents = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36',
    'Mozilla/5.0 (Linux; Android 11; Pixel 4a) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.105 Mobile Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Mobile/15E148 Safari/604.1'
]

def scrape_single_url(url):
    headers = {
        'user-agent': random.choice(user_agents),
        'accept-language': 'en-US,en;q=0.9'
    }

    response = requests.get(url, headers=headers)
    data = response.content

    soup = BeautifulSoup(data, 'html.parser')

    model = soup.find('div', class_="product-header").text.strip()
    text_price = soup.find('p', class_="big-price").text[2:].strip()
    price = float(text_price.replace(',', ''))

    return model, price

def scrape_and_update(urls, db_uri):
    engine = create_engine(db_uri)
    Session = sessionmaker(bind=engine)
    session = Session()

    for url in urls:
        model, price = scrape_single_url(url)

        existing_gpu = session.query(GPU).filter_by(url=url).first()

        if existing_gpu:
            existing_gpu.price.append(Price(price=price))
        else:
            new_gpu = GPU(model=model, url=url, price=[Price(price=price)])
            session.add(new_gpu)

        session.commit()

        print(f"{model}  {price}  {url}")

        delay = random.randint(5, 20)
        time.sleep(delay)

    session.close()

if __name__ == "__main__":
    pass