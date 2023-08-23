import smtplib
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import psycopg2
import os
import json

load_dotenv()

def main():
    # Load database URI from config.json
    config_path = '../config.json'  # Adjust the path to reach the config.json file
    env = os.environ.get('FLASK_ENV', 'development')

    with open(config_path, 'r') as config_file:
        config = json.load(config_file)

    db_uri = config[env]['DATABASE_URI']

    # Database connection setup
    conn = psycopg2.connect(db_uri)
    cursor = conn.cursor()

    # Establish SMTP connection
    smt = smtplib.SMTP('smtp.gmail.com', 587)
    smt.ehlo()
    smt.starttls()
    email = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('SENDER_PASSWORD')
    smt.login(email, password)

    # Get subscription data using raw SQL query
    query = """
        SELECT s.user_id, s.gpu_id, pr.price, u.email, g.model, g.url
        FROM Subscriptions s
        JOIN GPU g ON s.gpu_id = g.id
        JOIN Price pr ON pr.gpu_id = g.id
        JOIN Users u ON u.id = s.user_id
        WHERE s.desired_price >= pr.price
    """
    cursor.execute(query)
    subscriptions = cursor.fetchall()

    for subscription in subscriptions:
        user_id, gpu_id, price, user_email, gpu_model, gpu_url = subscription

        # Create email
        subject = "Price notification"
        message = f"Hey, the price of {gpu_model} has dropped to ${price:.2f}. Buy it!\nLink: {gpu_url}"

        msg = MIMEMultipart()
        msg['From'] = 'price-watcher@gmail.com'
        msg['To'] = user_email
        msg['Subject'] = Header(subject, 'utf-8')
        msg.attach(MIMEText(message, 'plain', 'utf-8'))

        # Print the email details for server log
        print(f"Sending email to: {user_email}")

        # Send email
        smt.sendmail('price-watcher@gmail.com', user_email, msg.as_string())

    # Clean up
    smt.quit()
    conn.close()

if __name__ == "__main__":
    main()
