import requests
import mysql.connector
from datetime import datetime

API_KEY = 'cbc8886e4335cce0ffcb10bd'
BASE_URL = 'https://v6.exchangerate-api.com/v6/{}/pair/'.format(API_KEY)

# MySQL Database connection details
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = ''
DB_NAME = 'currency_converter'

# Function to connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

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

# Function to save conversion history to MySQL database
def save_conversion_history(amount, from_currency, to_currency, converted_amount, rate):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            amount FLOAT,
            from_currency VARCHAR(10),
            to_currency VARCHAR(10),
            converted_amount FLOAT,
            rate FLOAT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        INSERT INTO conversions (amount, from_currency, to_currency, converted_amount, rate)
        VALUES (%s, %s, %s, %s, %s)
    ''', (amount, from_currency, to_currency, converted_amount, rate))
    conn.commit()
    conn.close()

# Function to view conversion history from MySQL database
def view_conversion_history():
    conn = connect_db()
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
