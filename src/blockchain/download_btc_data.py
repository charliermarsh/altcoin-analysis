import ssl
import time
import csv

from blockchain import exceptions
from blockchain import blockexplorer
from blockchain import util

util.TIMEOUT = 30

FILENAME = '../../btc-data/BTC.csv'
API_CODE = '5d50c584-9a3f-4d72-8da8-857d0f139b37'

def get_difficulty(block):
    """
    Return the difficulty for the block.
    References:
    - https://bitcoin.org/en/developer-reference#target-nbits
    - https://en.bitcoin.it/wiki/Difficulty
    """
    target = get_target(block.bits)
    return get_highest_target() * 1.0 / target

def get_highest_target():
    bits = hex_to_int('0x1d00ffff')
    return get_target(bits)

def get_target(bits):
    bits = int_to_hex(bits)
    exp = hex_to_int(bits[:2])
    mult = hex_to_int(bits[2:])
    target = mult * (2 ** (8 * (exp - 3)))
    return target

def int_to_hex(n):
    hex_str = hex(n)[2:] # get rid of '0x'
    if hex_str[-1] == "L":
        hex_str = hex_str[:-1]
    return hex_str

def hex_to_int(n):
    return int(n, 16)

def get_latest_block():
    """
    Return the latest block in the blockchain.
    """
    latest_block_index = blockexplorer.get_latest_block(api_code = API_CODE).block_index
    return blockexplorer.get_block(str(latest_block_index), api_code = API_CODE)

def get_previous_block(block):
    """
    Return the parent of the given block.
    """
    if block.height == 0:
        return None
    else:
        return blockexplorer.get_block(block.previous_block, api_code = API_CODE)

def get_latest_saved_block():
    with open(FILENAME, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            pass
        # row has contents of the last line
        latest_block_height = row[0]
        blocks = blockexplorer.get_block_height(latest_block_height, api_code = API_CODE)
        for block in blocks:
            if block.main_chain:
                return block
    return None

if __name__ == "__main__":
    start_new = False
    if start_new:
        block = get_latest_block()
        mode = 'w'
    else:
        block = get_previous_block(get_latest_saved_block())
        mode = 'a'

    with open(FILENAME, mode) as f:
        writer = csv.writer(f)
        if start_new:
            writer.writerow(['height', 'timestamp', 'difficulty', 'num_txs'])
        while block and True:
            try:
                print block.height
                height = block.height
                timestamp = block.time
                difficulty = get_difficulty(block)
                num_txs = len(block.transactions)
                writer.writerow([height, timestamp, difficulty, num_txs])
                block = get_previous_block(block)
            except (ssl.SSLError, exceptions.APIException) as e:
                print e
                print "Sleeping for 30 seconds..."
                time.sleep(30)
