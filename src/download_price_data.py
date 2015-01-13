"""
    Downloads Altcoin-USD and Altcoin-BTC CSV price data to ../price-data.
"""

import datetime
import json
import urllib2
import csv
import os

import config


def fetch_prices(altcoin_code, target):
    """
        Returns JSON of prices
    """
    url = 'http://coinplorer.com/Charts/GetData?fromCurrency=%s&toCurrency=%s&fromDate=null&toDate=null' % (
        altcoin_code, target)
    req = urllib2.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    f = urllib2.urlopen(req)
    date_prices = json.loads(f.read())['data']

    return_data = []

    for date_price in date_prices:
        date = datetime.datetime.fromtimestamp(date_price[0])
        price = date_price[1]
        return_data.append((date.year, date.month, date.day, price))

    return return_data

if __name__ == '__main__':
    def dir_for_target(target):
        return '../price-data2/%s/' % target
    targets = ['USD', 'BTC']
    for target in targets:
        if not os.path.exists(dir_for_target(target)):
            os.makedirs(dir_for_target(target))

    altcoin_codes = config.ALL_TICKERS
    for altcoin_code in altcoin_codes:
        for target in targets:
            price_data = fetch_prices(altcoin_code, target)
            with open(dir_for_target(target) + '/%s-%s.csv' % (altcoin_code, target), 'w') as out:
                csv_out = csv.writer(out)
                csv_out.writerow(['year', 'month', 'day', 'price'])
                for row in price_data:
                    csv_out.writerow(row)
