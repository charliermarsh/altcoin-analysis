import argparse
import csv
import pandas as pd
import psycopg2
import psycopg2.extras
from datetime import datetime

from block import Block
import utils
import plot
import config


class Coin(object):

    def __init__(self, ticker):
        self.ticker = ticker
        self.blocks = self._get_blocks()
        self.prices = self._get_prices()
        self._update_blocks_with_prices()

    def _get_blocks(self):
        if self.ticker.upper() == 'BTC':
            return self._get_btc_blocks()

        # Connect to database
        connect_params = 'dbname=abe-%s user=%s' % (self.ticker.lower(), config.USER)
        conn = psycopg2.connect(connect_params)
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

        # Get blocks
        fields = ['block_id', 'block_ntime', 'block_chain_work', 'block_num_tx']
        command = "SELECT {0} FROM block ORDER BY block_id".format(', '.join(fields))
        cur.execute(command)
        block_dicts = cur.fetchall()
        blocks = [Block(**b) for b in block_dicts]

        # Close connection
        cur.close()
        conn.close()

        # Make blocks track individual work and not cumulative
        for i in reversed(range(1, len(blocks))):
            blocks[i].block_chain_work -= blocks[i - 1].block_chain_work

        # Convert work to difficulty
        for b in blocks:
            b.block_chain_work = utils.work_to_difficulty(b.block_chain_work)

        return blocks

    def _get_btc_blocks(self):
        blocks = []
        with open(config.get_btc_block_filename(), 'rb') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Skip header
                if row[0] == 'height':
                    continue
                (height, timestamp, difficulty, num_txs) = row
                timestamp = int(float(timestamp))
                difficulty = int(float(difficulty))
                block = Block(height, timestamp, difficulty, num_txs, True)
                blocks.append(block)
        return blocks

    @staticmethod
    def _time_to_key(time):
        return time.strftime('%Y-%m-%d')

    @staticmethod
    def _normalize(df, method):
        transform = {
            'z_score': lambda df, f: (df[f] - df[f].mean()) / df[f].std(ddof=0),
            'min_max': lambda df, f: (df[f] - df[f].min()) / (df[f].max() - df[f].min()),
            None: lambda df, f: df[f]
        }[method]

        for field in df:
            df[field] = transform(df, field)

    def _get_prices(self, target='USD'):
        prices = {}
        filename = config.get_price_filename(self.ticker, target=target)
        for row in utils.get_csvreader(filename):
            # Skip header
            if row[0] == 'year':
                continue
            date = datetime.strptime(' '.join(row[:3]), '%Y %m %d')
            key = self._time_to_key(date)
            prices[key] = float(row[3])
        return prices

    def _update_blocks_with_prices(self):
        for b in self.blocks:
            key = self._time_to_key(b.time)
            b.price = self.prices.get(key)

    def get_frame(self, *fields, **kwargs):
        """
        Return the data frame that includes the given fields.
        Fields must be chosen from 'block_chain_work', 'block_num_tx', or 'price'.
        Min-max and Z-score normalization can be performed by passing in normalize='min_max' or
        normalize='z_score', respectively.
        """
        data = [b.__dict__ for b in self.blocks]
        times = [b.time for b in self.blocks]
        df = pd.DataFrame(data, index=times, columns=fields)

        # Normalize columns
        normalize = kwargs.get('normalize', None)
        self._normalize(df, normalize)

        return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Compute and plot timeseries correlation for all metrics in a given coin.')
    parser.add_argument('ticker', choices=config.TICKERS.values())
    args = parser.parse_args()

    coin = Coin(args.ticker)
    df = coin.get_frame('block_chain_work', 'block_num_tx', 'price')
    plot.plot_timeseries(args.ticker, df, window=100)
