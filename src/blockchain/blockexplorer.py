from bs4 import BeautifulSoup
from datetime import datetime
import csv
import grequests
import sys

FILENAME = '../../btc-data/BTC-data.csv'

def get_timestamp(s):
    dt = datetime.strptime(s, '%Y-%m-%d %H:%M:%S')
    epoch = datetime(1970,1,1)
    secs_since_epoch = (dt - epoch).total_seconds()
    return secs_since_epoch

def get_block_from_html(html):
    soup = BeautifulSoup(html)
    block = dict()
    block['height'] = str(soup.h1.contents[0].split()[1])
    for li in soup.find_all('li'):
        attr = str(li.contents[0])
        if attr == 'Difficulty':
            value = str(li.contents[2])
            index = value.find(' (')
            value = value[2:index]
            value = value.replace(' ', '')
        else:
            value = str(li.contents[-1])
            if value[0] == ':':
                value = value[2:]
        if attr == 'Time':
            block['timestamp'] = get_timestamp(value)
        if attr == 'Difficulty':
            block['difficulty'] = value
        if attr == 'Transactions':
            block['num_txs'] = value
    return block

def get_latest_saved_height():
    with open(FILENAME, 'r') as f:
        reader = csv.reader(f)
        largest_height = 0
        for row in reader:
            if row[0] == 'height':
                continue
            height = int(row[0])
            if height > largest_height:
                largest_height = height
        return largest_height

def get_url(height):
    url = 'http://blockexplorer.com/b/%s' % height
    return url

def write_block(response, *args, **kwargs):
    if response.status_code == 200:
        html = response.text
        b = get_block_from_html(html)
        writer.writerow([b['height'], b['timestamp'], b['difficulty'], b['num_txs']])
        print b['height']
    response.close()

def construct_request(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    hooks = {'response': write_block}
    return grequests.get(url, headers=headers, hooks=hooks)

if __name__ == "__main__":
    start_new = False
    end_height = 338276
    if start_new:
        start_height = 0
        mode = 'w'
    else:
        start_height = get_latest_saved_height() + 1
        mode = 'a'

    f = open(FILENAME, mode)
    writer = csv.writer(f)
    if start_new:
        writer.writerow(['height', 'timestamp', 'difficulty', 'num_txs'])

    REQUESTS_PER_ROUND = 1000
    round_start = start_height
    while round_start < end_height:
        round_end = round_start + REQUESTS_PER_ROUND
        if round_end > end_height:
            round_end = end_height
        rs = (construct_request(get_url(height)) for height in range(round_start, round_end))
        try:
            grequests.map(rs, size=200)
        except KeyboardInterrupt:
            f.close()
            sys.exit(1)
        round_start = round_end
