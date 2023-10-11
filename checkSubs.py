from website.models import Subscriptions, GPU, Price, Users
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import boto3
from botocore.exceptions import ClientError
import psycopg2
import os
import json
import time

def get_aws_secret(secret_name):
    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name='us-east-1')

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise e

    return get_secret_value_response['SecretString']

def main():

    while True:

        print("Starting checkSubs.py script loop")

        # Load database URI from config.json
        config_path = 'config.json'  # Adjust path to reach the config.json file
        env = os.environ.get('FLASK_ENV', 'development')

        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        db_uri = config[env]['DATABASE_URI']

        # Database connection setup
        engine = create_engine(db_uri)
        Session = sessionmaker(bind=engine)
        session = Session()

        # Establish SMTP connection
        smt = smtplib.SMTP('smtp.gmail.com', 587)
        smt.ehlo()
        smt.starttls()
        
        # Retrieve SENDER_EMAIL and SENDER_PASSWORD secrets
        try:
            secret_data = get_aws_secret("gpuscrapesite/sender_email")
            email = secret_data.get("SENDER_EMAIL")
            password = secret_data.get("SENDER_PASSWORD")
        except KeyError as e:
            print(f"KeyError: {e}. Please ensure the secrets in AWS Secrets Manager have the correct keys.")
            return

        smt.login(email, password)

        smt.login(email, password)

        # Get subscription data using SQLAlchemy query
        latest_price_subquery = (
            session.query(Price.gpu_id, func.max(Price.date).label("latest_date"))
            .group_by(Price.gpu_id)
            .subquery()
        )

        subscriptions = (
            session.query(
                Subscriptions.user_id,
                Subscriptions.gpu_id,
                Price.price,
                Users.email,
                GPU.model,
                GPU.url
            )
            .join(GPU, Subscriptions.gpu_id == GPU.id)
            .join(Price, GPU.id == Price.gpu_id)
            .join(Users, Subscriptions.user_id == Users.id)
            .join(latest_price_subquery, Price.gpu_id == latest_price_subquery.c.gpu_id)
            .filter(Subscriptions.desired_price >= Price.price)
            .filter(Price.date == latest_price_subquery.c.latest_date)
            .all()
        )

        print(f"Number of subscriptions: {len(subscriptions)}")

        for subscription in subscriptions:
            user_id, gpu_id, price, user_email, gpu_model, gpu_url = subscription

            # Create email
            subject = "Price notification"
            message = f"Hey, the price of {gpu_model} has dropped to ${price:.2f}. Buy it!\nLink: {gpu_url}"

            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = user_email
            msg['Subject'] = Header(subject, 'utf-8')
            msg.attach(MIMEText(message, 'plain', 'utf-8'))

            # Print the email details for server log
            print(f"Sending email to: {user_email}")

            # Send email
            smt.sendmail(email, user_email, msg.as_string())

        # Clean up
        smt.quit()
        session.close()
        print("sleeping 5 minutes")
        time.sleep(300)  # 300 seconds (5 minutes) for testing, 86400 seconds for 1 day

if __name__ == "__main__":
    main()
