import argparse

import config
import plot
from coin import Coin


def create_coin_frame(coins, metric, normalize=None):
    df = coins[0].get_frame(metric, normalize=normalize)
    df.columns = [coins[0].ticker]
    for i in range(1, len(coins)):
        df2 = coins[i].get_frame(metric, normalize=normalize)
        df2.columns = [coins[i].ticker]
        df = df.join(df2, how='outer')

    return df


def create_price_frame(prices, normalize=None):
    df = prices[0].get_frame(normalize=normalize)
    df.columns = [prices[0].ticker]
    for i in range(1, len(prices)):
        df2 = prices[i].get_frame(normalize=normalize)
        df2.columns = [prices[i].ticker]
        df = df.join(df2, how='outer')

    return df


if __name__ == '__main__':
    valid_metrics = ['block_chain_work', 'block_num_tx']
    parser = argparse.ArgumentParser(
        description='Compute timeseries correlation for a given metric across coins.')
    parser.add_argument('metrics', nargs='?', choices=valid_metrics, default=valid_metrics)
    args = parser.parse_args()

    if type(args.metrics) != list:
        args.metrics = [args.metrics]

    # Create coins
    coins = [Coin(ticker) for ticker in config.TICKERS]
    for metric in args.metrics:
        df = create_coin_frame(coins, metric, normalize='min_max')
        plot.plot_timeseries(metric, df)
        print df.corr()
