import numpy as np
import pandas as pd
import crypto_object as co
import sys
from datetime import timedelta
import matplotlib.pyplot as plt

def plot_random_paths(rp, true_path, coin):
    """
    Plot a collection of random paths (e.g. output of option_pricing.random_paths)
    """
    
    f, ax = plt.subplots(1,1, figsize=(12,8))
    
    dates = rp.index
    
    rp = rp.sort_index(axis=0 ,ascending=False).values
    true_path = true_path.sort_index(ascending=False).values
    
    N = rp.shape[1]
    
    for i in np.arange(N):
        ax.plot(dates, rp[:, i], color='blue', alpha=.2)
        
    ax.plot(dates, true_path, color='red')
    
    ax.set_xlabel('Date')
    ax.set_ylabel('{} Price'.format(coin.name))
    ax.set_title(coin.name)