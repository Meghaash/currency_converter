import requests
import sqlite3
from datetime import datetime


API_KEY = 'cbc8886e4335cce0ffcb10bd'
BASE_URL = 'https://v6.exchangerate-api.com/v6/{}/pair/'.format(API_KEY)

# Function to fetch live exchange rates
def fetch_exchange_rate(from_currency, to_currency):
    url = BASE_URL + f"{from_currency}/{to_currency}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data['conversion_rate']
    else:
        raise Exception("Error fetching exchange rates.")

# Function to perform currency conversion
def convert_currency(amount, from_currency, to_currency):
    rate = fetch_exchange_rate(from_currency, to_currency)
    converted_amount = amount * rate
    return converted_amount, rate

# Function to save conversion history to local SQLite database
def save_conversion_history(amount, from_currency, to_currency, converted_amount, rate):
    conn = sqlite3.connect('currency_conversions.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INTEGER PRIMARY KEY,
            amount REAL,
            from_currency TEXT,
            to_currency TEXT,
            converted_amount REAL,
            rate REAL,
            timestamp TEXT
        )
    ''')
    cursor.execute('''
        INSERT INTO conversions (amount, from_currency, to_currency, converted_amount, rate, timestamp)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (amount, from_currency, to_currency, converted_amount, rate, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
    conn.commit()
    conn.close()

# Function to view conversion history
def view_conversion_history():
    conn = sqlite3.connect('currency_conversions.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM conversions ORDER BY timestamp DESC LIMIT 5')
    records = cursor.fetchall()
    conn.close()
    return records

# Main function to run the script
def main():
    print("Welcome to Currency Converter!")
    amount = float(input("Enter the amount: "))
    from_currency = input("Enter the source currency (e.g., USD, INR): ").upper()
    to_currency = input("Enter the target currency (e.g., EUR, INR): ").upper()

    try:
        converted_amount, rate = convert_currency(amount, from_currency, to_currency)
        print(f"{amount} {from_currency} = {converted_amount:.2f} {to_currency} (Rate: {rate})")

        # Save the conversion history
        save_conversion_history(amount, from_currency, to_currency, converted_amount, rate)
        print("Conversion saved successfully!")
    except Exception as e:
        print(e)

    # Option to view recent history
    view_history = input("Do you want to view your last 5 conversions? (y/n): ")
    if view_history.lower() == 'y':
        history = view_conversion_history()
        for record in history:
            print(record)

if __name__ == '__main__':
    main()
