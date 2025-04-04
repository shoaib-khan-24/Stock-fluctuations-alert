import time
import requests
from datetime import datetime , timedelta
from twilio.rest import Client
import os

RECEIVER_MOBILE_NO = "+1234567890"      #Enter your verified mobile number here

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

stock_api_key = os.environ.get("STOCK_API_KEY")
stock_api_endpoint = os.environ.get("STOCK_API_ENDPOINT")

stock_parameters = {
    "function":"TIME_SERIES_DAILY",
    "symbol":STOCK,
    "apikey":stock_api_key
}

response = requests.get(url=stock_api_endpoint , params=stock_parameters)
response.raise_for_status()

one_day_before = str(datetime.today().date() - timedelta(days=1))
two_day_before = str(datetime.today().date() - timedelta(days=2))

price_before = float(response.json()["Time Series (Daily)"][two_day_before]["4. close"])
price_after = float(response.json()["Time Series (Daily)"][one_day_before]["4. close"])
price_difference = price_after - price_before
change_in_price = ((price_difference/price_before)*100) + 6

if abs(change_in_price) > 0:

    news_api_endpoint = os.environ.get("NEWS_API_ENDPOINT")
    news_api_key = os.environ.get("NEWS_API_KEY")

    news_parameters = {
        "q": COMPANY_NAME,
        "apikey": news_api_key
    }

    response = requests.get(url=news_api_endpoint, params=news_parameters)
    response.raise_for_status()
    data = response.json()["articles"][0:3]

    account_sid = os.environ.get("TWILIO_ACC_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")

    client = Client(account_sid, auth_token)

    for news in data:
        news_title = news["title"]
        news_description = news["description"]

        if change_in_price > 5:
            stock_condition = f"TSLA: 🔺{round(change_in_price,2)}%"
        else:
            stock_condition = f"TSLA: 🔻{round(change_in_price,2)}"
            
        message = client.messages.create(
            body= stock_condition + "\n" + "Headline: " + news_title,
            from_=os.environ.get("TWILIO_MOBILE_NO"),
            to= RECEIVER_MOBILE_NO
        )
        print(message.status)
        time.sleep(10)
