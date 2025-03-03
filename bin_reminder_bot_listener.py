### https://www.doogal.co.uk/UPRN?postcode=ML5%205J Y###


import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Telegram bot details
BOT_TOKEN = '7998072445:AAHE_bQnqK8Rs0ZmwQ4O0Fh-tv-n3Js8JHE'
CHAT_ID = '6534394993'  # Replace with your Chat ID

# Bin Collection URL
BIN_COLLECTION_URL = "https://www.northlanarkshire.gov.uk/bin-collection-dates/000118110229/48409653"

# Bin Type Mapping
BIN_COLORS = {
    "Glass, Metals, Plastics and Cartons": "Green Bin",
    "Food and Garden": "Brown Bin",
    "Blue-lidded Recycling Bin": "Blue Bin",
    "General Waste": "Black Bin"
}

def get_bin_collection_info():
    """Fetches the bin collection dates from the website."""
    response = requests.get(BIN_COLLECTION_URL)
    if response.status_code != 200:
        return "Failed to retrieve bin collection data."
    
    soup = BeautifulSoup(response.text, 'html.parser')
    bin_collection_container = soup.find('div', class_='bin-collection-dates-container')
    
    if not bin_collection_container:
        return "No bin collection data found."
    
    collections = []
    for waste_type_container in bin_collection_container.find_all('div', class_='waste-type-container'):
        bin_type = waste_type_container.find('h3').get_text(strip=True)
        collection_dates = waste_type_container.find_all('p')
        
        for date_item in collection_dates:
            try:
                collection_date = datetime.strptime(date_item.get_text(strip=True), '%d %B %Y').date()
                collections.append((collection_date, bin_type, BIN_COLORS.get(bin_type, "Unknown Bin")))
            except ValueError:
                continue
    
    return collections

def get_next_bin():
    """Finds the next Saturday's bin collection."""
    today = datetime.now().date()
    next_saturday = today + timedelta((5 - today.weekday()) % 7)
    collections = get_bin_collection_info()
    
    if isinstance(collections, str):  # Handle error message if collections failed
        return collections
    
    upcoming_bins = [f"{bin_color} ({bin_type}) on {date.strftime('%d %B %Y')}" 
                     for date, bin_type, bin_color in collections if date == next_saturday]
    
    if upcoming_bins:
        return "\n".join(upcoming_bins)
    return f"No bin collection found for {next_saturday.strftime('%d %B %Y')}"

async def send_bin_update(update: Update, context: CallbackContext):
    """Handles /nextbin command and sends bin collection details."""
    bin_message = get_next_bin()
    await update.message.reply_text(bin_message)

def main():
    """Starts the Telegram bot."""
    application = Application.builder().token(BOT_TOKEN).build()  # Updated line

    # Add your handlers here
    application.add_handler(CommandHandler("nextbin", send_bin_update))

    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
