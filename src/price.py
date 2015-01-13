from datetime import datetime
import pandas as pd

from coin import Coin
from crosscoin import create_price_frame
import config
import plot


class Price(Coin):

    def __init__(self, ticker, target='USD'):
        self.ticker = ticker
        self.prices = self._get_prices(target=target)

    def get_frame(self, normalize=None):
        """Return the price data frame, with the same normalization options as in Coin."""
        # Get datetime-indexed timeseries data
        times = []
        data = []
        for t in sorted(self.prices.keys()):
            times.append(datetime.strptime(t, '%Y-%m-%d'))
            data.append(self.prices[t])

        df = pd.DataFrame(data, index=times, columns=['price'])

        # Normalize columns
        self._normalize(df, normalize)

        return df

if __name__ == '__main__':
    prices = [Price(ticker) for ticker in config.ALL_TICKERS]

    # Compute JOIN over price frames
    df = create_price_frame(prices, normalize='z_score')

    # `df` can be replaced with `df.pct_change()` or `pd.rolling_var(df, 7)` to track volatility
    plot.plot_timeseries('Prices', df)
    print df.corr()
