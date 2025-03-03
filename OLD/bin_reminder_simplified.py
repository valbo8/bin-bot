import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Direct URL for bin collection details (modify if necessary)
BIN_COLLECTION_URL = 'https://www.northlanarkshire.gov.uk/bin-collection-dates/000118110229/48409653'

# Mapping bin types to colors
BIN_COLORS = {
    "Glass, Metals, Plastics and Cartons": "Green Bin",
    "Food and Garden": "Brown Bin",
    "Blue-lidded Recycling Bin": "Blue Bin",
    "General Waste": "Black Bin"
}

def get_bin_collection_info():
    # Step 1: Get the page content using requests
    response = requests.get(BIN_COLLECTION_URL)
    print("Attempting to access:", BIN_COLLECTION_URL)
    print("Response status code:", response.status_code)
    
    if response.status_code != 200:
        print("Failed to retrieve the page.")
        return []
    
    # Step 2: Parse the HTML using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the container for bin collection dates
    bin_collection_container = soup.find('div', class_='bin-collection-dates-container')
    
    if not bin_collection_container:
        print("No bin collection data found.")
        return []
    
    collections = []

    # Iterate through each waste type container
    for waste_type_container in bin_collection_container.find_all('div', class_='waste-type-container'):
        bin_type = waste_type_container.find('h3').get_text(strip=True)
        bin_color = BIN_COLORS.get(bin_type, "Unknown Bin")  # Get bin color from mapping

        # Extract all collection dates for this bin type
        collection_dates = waste_type_container.find_all('p')
        for date_item in collection_dates:
            date_str = date_item.get_text(strip=True)
            try:
                collection_date = datetime.strptime(date_str, '%d %B %Y').date()
                collections.append((collection_date, bin_type, bin_color))
            except ValueError:
                print(f"Skipping invalid date format: {date_str}")
    
    return collections

def main():
    today = datetime.now().date()
    
    # Find the next Saturday's bin collection
    next_saturday = today + timedelta((5 - today.weekday()) % 7)

    # Get the bin collection info
    collections = get_bin_collection_info()

    print(f"Next Saturday is: {next_saturday.strftime('%d %B %Y')}")

    found_collection = False
    for collection_date, bin_type, bin_color in collections:
        if collection_date == next_saturday:
            print(f"Upcoming Saturday ({next_saturday.strftime('%d %B %Y')}): {bin_type} ({bin_color}) collection")
            found_collection = True

    if not found_collection:
        print(f"No bin collection found for next Saturday ({next_saturday.strftime('%d %B %Y')})")

# Run the script
main()
