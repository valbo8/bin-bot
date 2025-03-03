import requests
from bs4 import BeautifulSoup
from telegram import Bot
from datetime import datetime
import time
from requests.exceptions import RequestException

# Telegram bot details
BOT_TOKEN = '7998072445:AAHE_bQnqK8Rs0ZmwQ4O0Fh-tv-n3Js8JHE'
CHAT_ID = '6534394993'  # Replace with your Chat ID

# Your address details
POSTCODE = 'ML5 5JY'
ADDRESS = '10 CRAIGIE PLACE, COATBRIDGE, ML5 5JY'  # Replace with your actual house address

# URL of the bin collection page
BASE_URL = 'https://www.northlanarkshire.gov.uk/bin-collection-dates'

def send_telegram_message(message):
    bot = Bot(token=BOT_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=message)

def get_bin_collection_info():
    session = requests.Session()
    
    try:
        # Step 1: Open the bin collection page
        print(f"Attempting to access: {BASE_URL}")
        response = session.get(BASE_URL, timeout=10)
        print(f"Response status code: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to retrieve page.")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 2: Submit postcode
        postcode_data = {'postcode': POSTCODE}
        response = session.post(BASE_URL, data=postcode_data, timeout=10)
        print(f"Postcode response status code: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to submit postcode.")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 3: Select the correct address
        address_data = {'selected_address': ADDRESS}
        response = session.post(BASE_URL, data=address_data, timeout=10)
        print(f"Address response status code: {response.status_code}")
        
        if response.status_code != 200:
            print("Failed to submit address.")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Step 4: Extract bin collection dates
        collections = []
        for item in soup.find_all('div', class_='collection-item'):  # Adjust selector if necessary
            date_str = item.find('div', class_='date').text.strip()
            bin_type = item.find('div', class_='bin-type').text.strip()
            collection_date = datetime.strptime(date_str, '%d %B %Y')
            collections.append((collection_date.date(), bin_type))
        
        return collections
    
    except RequestException as e:
        print(f"Request failed: {e}")
        return []

def main():
    today = datetime.now().date()
    collections = get_bin_collection_info()
    
    if not collections:
        print("No collections found.")
        return

    # Check if today matches a collection date
    for collection_date, bin_type in collections:
        print(f"Checking collection date: {collection_date} for bin: {bin_type}")
        
        if collection_date == today:
            print(f"Today's collection: {bin_type} bin")
            message = f"Reminder: Put out your {bin_type} bin today."
            send_telegram_message(message)
            break
    else:
        # If it's not today, show the next Friday's bin collection
        next_friday = today + timedelta((4 - today.weekday()) % 7)
        for collection_date, bin_type in collections:
            if collection_date == next_friday:
                message = f"Next Friday's bin collection is {bin_type} on {next_friday.strftime('%A, %d %B')}."
                print(f"Sending next Friday's reminder: {message}")
                send_telegram_message(message)
                break

# Run script once per day
while True:
    main()
    time.sleep(86400)  # Wait for 24 hours
