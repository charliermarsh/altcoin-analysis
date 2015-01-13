import subprocess
import argparse
import psycopg2

import config

address_version = {
    'anc': '17',
    'dgc': '1e',
    'drk': '4c',
    'ftc': '0e',
    'ltc': '30',
    'mec': '32',
    'mnc': '32',
    'nmc': '34',
    'nvc': '08',
    'ppc': '37'
}


def _run_decode_address(address):
    return subprocess.check_output(
        'cd ../bitcoin-abe && python -m Abe.abe --query /q/decode_address/%s' % address,
        shell=True
    )


def _run_hashtoaddress(address_hash, ticker):
    return subprocess.check_output(
        'cd ../bitcoin-abe && python -m Abe.abe --query /q/hashtoaddress/%s/%s' % (
            address_hash, address_version[ticker.lower()]),
        shell=True
    )


def _fetch_first(command, ticker):
    # Connect to database
    connect_params = 'dbname=abe-%s user=%s' % (ticker.lower(), config.USER)
    conn = psycopg2.connect(connect_params)
    cur = conn.cursor()

    # Execute query
    cur.execute(command)
    result = cur.fetchone()[0]

    # Close connection
    cur.close()
    conn.close()
    return result


def pubkey_id_to_hash(pubkey_id, ticker):
    command = "SELECT pubkey_hash FROM pubkey WHERE pubkey_id = {0}".format(pubkey_id)
    return _fetch_first(command, ticker)


def hash_to_pubkey_id(pubkey_hash, ticker):
    command = "SELECT pubkey_id FROM pubkey WHERE pubkey_hash = '{0}'".format(pubkey_hash)
    return _fetch_first(command, ticker)


def encode_address(address, ticker):
    output = _run_decode_address(address)
    pubkey_hash = output.split(':')[-1].strip()
    return hash_to_pubkey_id(pubkey_hash, ticker)


def decode_address(pubkey_id, ticker):
    pubkey_hash = pubkey_id_to_hash(pubkey_id, ticker)
    output = _run_hashtoaddress(pubkey_hash, ticker)
    return output.strip()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert addresses to Abe pubkey_ids and vice versa.')
    parser.add_argument('mode', choices=['encode', 'decode'])
    parser.add_argument('address_or_id')
    parser.add_argument('ticker', choices=address_version.keys())
    args = parser.parse_args()

    if args.mode == 'decode':
        print decode_address(args.address_or_id, args.ticker)
    elif args.mode == 'encode':
        print encode_address(args.address_or_id, args.ticker)
