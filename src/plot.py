import matplotlib.pyplot as plt
import pandas as pd

def plot_timeseries(title, df, window=None, legend=True):
    fig, ax = plt.subplots()
    kwargs = {
        'title': title,
        'ax': ax,
        'legend': legend
    }
    if window:
        pd.rolling_mean(df, window).plot(**kwargs)
    else:
        df.plot(**kwargs)
    ax.xaxis_date()
    fig.autofmt_xdate()
    plt.show()
