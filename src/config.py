import os

USER = 'crmarsh'

_TICKERS_TO_COINS = {
    'anc': 'anoncoin',
    'dgc': 'digitalcoin',
    # 'doge': 'dogecoin',
    'drk': 'darkcoin',
    'gld': 'goldcoin',
    'ftc': 'feathercoin',
    'lky': 'luckycoin',
    'ltc': 'litecoin',
    'mec': 'megacoin',
    'mnc': 'mincoin',
    'nmc': 'namecoin',
    'nvc': 'novacoin',
    'ppc': 'peercoin'
}

TICKERS = _TICKERS_TO_COINS.keys()

ALL_TICKERS = [
    # 'ALB',
    'ANC',
    'BQC',
    'BTB',
    'BTC',
    'BC',
    'BTE',
    'CNC',
    'COL',
    'CGB',
    'DRK',
    'DGC',
    'DOGE',
    'FTC',
    'FLO',
    'FRK',
    'FRC',
    'GLD',
    'IFC',
    'JKC',
    'LTC',
    'LKY',
    'MEC',
    'MMC',
    'MNC',
    'NMC',
    'NET',
    'NVC',
    'PPC',
    'PXC',
    'XPM',
    'PTS',
    'QRK',
    'TRC',
    'VTC',
    'WDC',
    'YAC',
    'ZET'
]

data_dir = os.path.expanduser('/path/to/data_dir/')
COINGEN_ADDRESS = ''


def get_price_filename(ticker, target='USD'):
    return '../price-data/%s/%s-%s.csv' % (target.upper(), ticker.upper(), target.upper())


def get_btc_block_filename():
    return '../btc-data/BTC-data.csv'
