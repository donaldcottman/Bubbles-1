from flask import Flask
import requests
import time
import math
import json

app = Flask(__name__)

@app.route('/run_python_script')
def run_script():
    # Download the list of all NASDAQ-traded stocks
    url = 'https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqtraded.txt'
    response = requests.get(url)
    lines = response.text.split('\n')

    # Extract the names of all stocks
    nasdaq_stocks = [line.split('|')[1] for line in lines if "Common Stock" in line]

    # API endpoint for historical data
    hist_endpoint = 'https://finnhub.io/api/v1/stock/candle'

    # API endpoint for current data
    current_endpoint = 'https://finnhub.io/api/v1/quote'

    # API key
    api_key = 'cfpbm11r01qq927hfap0cfpbm11r01qq927hfapg'

    # How many API requests can be made
    api_rateLimit = 30

    # Amount of stocks to be rendered
    rankingAmount = 200
    topStockPicks = False

    # Update bubble stock on interval (in seconds) for smooth bubble animation
    bubblesUpdateInterval = 1/0.25

    # Amount a bubbles stock will need to update before the script comes back to the stock
    bubblesUpdateAmount = math.ceil((rankingAmount/api_rateLimit)*bubblesUpdateInterval)

    # To bubbles format
    bubbles_JSON = []
    bubbles_JSONString = ""

    def bubblesUpdate(stock):
        # Stock symbol
        symbol = stock

        # Chosen interval (in minutes)
        chosenInterval = 5

        # Interval (in seconds)
        interval = chosenInterval * 60

        # Set the current time
        current_time = int(time.time())

        # Set the start and end times for the historical data request
        start_time = current_time - interval
        end_time = current_time

        # Set the resolution to 1 minute
        resolution = '1'

        # Set the number of data points to retrieve to 1
        limit = '1'
        print("here6")

        # Set the data format to JSON
        format = 'json'

        # Set the parameters for the historical data API request
        hist_params = {
            'symbol': symbol,
            'resolution': resolution,
            'from': start_time,
            'to': end_time,
            'limit': limit,
            'format': format,
            'token': api_key
        }

        # Send the historical data API request and get the response
        hist_response = requests.get(hist_endpoint, params=hist_params)
        print("here4")

        try:
            # Parse the response as JSON
            hist_data = hist_response.json()
        except json.JSONDecodeError as e:
            # Handle any JSON syntax errors
            print(f"JSON syntax error: {e}")
            return

        print("here5")
        # Get the price and volume from 5 minutes ago
        price_interval_ago = 10 #hist_data['c'][0]
        volume_interval_ago = 5 #hist_data['v'][0]
        current_price = 20 #hist_data['c'][-1]
        current_volume = 15 #hist_data['v'][-1]
        deltaP = ((current_price/price_interval_ago)*100)-100
        deltaV = ((current_volume/volume_interval_ago)*100)-100

        # Print the results
        # print(f'Price {chosenInterval} minutes ago: {price_interval_ago:.2f}')
        # print(f'Volume {chosenInterval} minutes ago: {volume_interval_ago:,}')
        # print(f'Current price: {current_price:.2f}')
        # print(f'Current volume: {current_volume:,}')
        # print(f'{chosenInterval} minute P change: {deltaP}')
        # print(f'{chosenInterval} minute V change: {deltaV}')

        # To bubbles format
        stock_JSON = {
            'symbol': symbol,
            'price': current_price,
            'volume': current_volume,
            'delta_p': deltaP,
            'delta_t': "",
            'delta_v': deltaV
        }
        print("here1")
        global bubbles_JSON
        global bubbles_JSONString
        # stock_JSONString = json.dumps(stock_JSON)
        # bubbles_JSONString = bubbles_JSONString + stock_JSONString + ','

        if topStockPicks == True:
            for i in range(math.ceil(bubblesUpdateAmount)):
                print(i+1)
                print(bubblesUpdateAmount)
                bubbles_JSONUpdate = {
                    'symbol': symbol,
                    'price': current_price+((current_price*deltaP/100)*((i+1)/bubblesUpdateAmount)),
                    'volume': current_volume+((current_volume*deltaV/100)*((i+1)/bubblesUpdateAmount)),
                    'delta_p': deltaP+((deltaP*deltaP/100)*((i+1)/bubblesUpdateAmount)),
                    'delta_t': "",
                    'delta_v': deltaV+((deltaV*deltaV/100)*((i+1)/bubblesUpdateAmount))
                }
                bubbles_JSON.append(bubbles_JSONUpdate)
        else:
            bubbles_JSON.append(stock_JSON)

        print("here2")

    # bubblesUpdate()

    # Names of all stocks
    for stock in nasdaq_stocks:
        print(stock)
        bubblesUpdate(stock)
    #bubblesUpdate('APPL')


    print("here3")
    # with open('bubbles.txt', 'w') as file:
    #     # Write a string to the file
    #     file.write(bubbles_JSONString)

    bubbles_JSONString = bubbles_JSONString[:-1]

    # Load the JSON data into a Python object
    # bubbles_JSON = json.loads(bubbles_JSONString)

    # Sort the Python object by the ABSdelta_p data value in descending order
    #sorted_obj = sorted(python_bubbleObj, key=lambda x: x['delta_p'], reverse=True)

    sorted_data = sorted(bubbles_JSON, key=lambda x: abs(x["delta_p"]), reverse=True)
    sorted_data = sorted_data[:200]
    print("len")
    print(len(sorted_data))
    topStockPicks = True
    print("here8")

    bubbles_JSON = []
    for i in range(len(sorted_data)):
        bubblesUpdate(sorted_data[i]['symbol'])
        

    # Open the file in write mode
    with open('bubbles.txt', 'w') as file:
        # Write a string to the file
        file.write(json.dumps(bubbles_JSON))

    print(json.dumps(bubbles_JSON))

    result = "Script finished running."
    return result