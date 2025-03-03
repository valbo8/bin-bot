import requests
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime, timedelta
import time

# Telegram bot details
BOT_TOKEN = '7998072445:AAHE_bQnqK8Rs0ZmwQ4O0Fh-tv-n3Js8JHE'
CHAT_ID = '6534394993'  # Replace with your Chat ID

# Your address details
POSTCODE = 'ML5 5JY'
ADDRESS = '10 CRAIGIE PLACE, COATBRIDGE, ML5 5JY'

# URL of the bin collection page
BASE_URL = 'https://www.northlanarkshire.gov.uk/bin-collection-dates'

def get_bin_collection_info():
    session = requests.Session()
    
    # Step 1: Open the bin collection page
    response = session.get(BASE_URL)
    print("Attempting to access:", BASE_URL)
    print("Response status code:", response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 2: Submit postcode (adjust if necessary)
    postcode_data = {'postcode': POSTCODE}
    response = session.post(BASE_URL, data=postcode_data)
    print("Postcode response status code:", response.status_code)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 3: Select the correct address
    address_data = {'selected_address': ADDRESS}
    response = session.post(BASE_URL, data=address_data)
    print("Address response status code:", response.status_code)
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Step 4: Extract bin collection dates
    collections = []
    for item in soup.find_all('div', class_='collection-item'):  # Adjust selector if necessary
        date_str = item.find('div', class_='date').text.strip()
        bin_type = item.find('div', class_='bin-type').text.strip()
        collection_date = datetime.strptime(date_str, '%d %B %Y')
        collections.append((collection_date.date(), bin_type))
    
    return collections

def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    today = datetime.now().date()
    collections = get_bin_collection_info()
    
    # Find the next bin collection for Saturday
    for collection_date, bin_type in collections:
        if collection_date == today + timedelta(days=1):  # Check for tomorrow (Saturday)
            message = f"Reminder: Put out your {bin_type} bin today, it's collected tomorrow."
            send_telegram_message(message)
            break
    else:
        # If no collection found for tomorrow, look for the next Friday's reminder
        next_friday = today + timedelta((4 - today.weekday()) % 7)  # Next Friday
        for collection_date, bin_type in collections:
            if collection_date == next_friday:
                message = f"Next Friday's bin collection is {bin_type} on {next_friday.strftime('%A, %d %B')}."
                send_telegram_message(message)
                break

# Run script once per day
while True:
    main()
    time.sleep(86400)  # Wait for 24 hours
