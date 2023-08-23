# webscrapedPriceWatcherSite 

## Setup & Installation

```bash
git clone <repo-url>
```

```bash
pip install -r requirements.txt
```

## Running The App

create config.json in project root:
{
    "development": {
      "DATABASE_URI": "postgresql://user:password@localhost/db",
      "SECRET_KEY": "key"
    },
    "testing": {
      "DATABASE_URI": "postgresql://testuser:testpassword@localhost/testdb",
      "SECRET_KEY": "testdbkey"
    }
  }

to set db uri and secret keys

```bash
export FLASK_APP=main.py && flask run
```

## Viewing The App

Go to `http://127.0.0.1:5000`

## Running scrape_tools
for webscrape.py and run_webscrape.py:
-the urls.txt list of urls is up to you. obviously the list needs all be pages with same html schema. and you will then need to adjust the soup parsed values to get the correct model and price values.

-once formatted correctly for your urls, you can 'python run_webscrape.py' to webscrape the urls one by one and then sleep 24 hrs before it scrapes again.

for checkSubs.py and run_checkSubs.py:
-requires a email account with app password set. To setup with gmail for example:https://support.google.com/accounts/answer/185833?hl=en
then store email and password in a .env file in project root like (no quotes):
"
SENDER_EMAIL=yourappemail@noreply.com
SENDER_PASSWORD=yourapppasswrd

"
-it will check the price of a model vs your desired price. if <= it will send an email then sleep 24hr and send again if price <= desired price. 
