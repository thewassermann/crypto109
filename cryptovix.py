import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import importlib
import crypto_object

import tqdm


def get_options_strip(coin, current_date, r, N_iter):
    
    # near and far dates
    near_term = current_date + datetime.timedelta(days=5)
    next_term = current_date + datetime.timedelta(days=30)
    
    starting_index = np.argwhere(coin.full_data['Date'] == current_date)[0][0]
    starting_price = coin.full_data['Close'][starting_index]
    
    # produces ks to search over
    ks_near = np.linspace(starting_price * .9, starting_price * 1.1, 10)
    ks_next = np.linspace(starting_price * .8, starting_price * 1.2, 20)
    
    # near term options
    near_term_calls = np.empty((10, ))
    near_term_puts = np.empty((10, ))
    
    # next term options
    next_term_calls = np.empty((20, ))
    next_term_puts = np.empty((20, ))
    
    for i, k in enumerate(ks_near):
        near_term_calls[i] = op.empirical_method(coin, current_date, near_term, 0, k, 'call', lookback=5, N=N_iter)
        near_term_puts[i] = op.empirical_method(coin, current_date, near_term, 0, k, 'put', lookback=5, N=N_iter)
        
    for i, k in enumerate(ks_next):
        next_term_calls[i] = op.empirical_method(coin, current_date, near_term, 0, k, 'call', lookback=30, N=N_iter)
        next_term_puts[i] = op.empirical_method(coin, current_date, near_term, 0, k, 'put', lookback=30, N=N_iter)
        
    near_term_df = pd.DataFrame([near_term_calls, near_term_puts]).T
    near_term_df.columns = ['Calls', 'Puts']
    near_term_df.index = ks_near
    next_term_df = pd.DataFrame([next_term_calls, next_term_puts]).T
    next_term_df.columns = ['Calls', 'Puts']
    next_term_df.index = ks_next
    
    return (near_term_df, next_term_df)


# SHOULD NOT BE NECESSARY, BUT : from __future__ import division

def closest_call_or_put(val, array, call_or_put):
    
    try:
        # loop through array and return propery idx
        if call_or_put == 'call':
            return min(array[array - val > 0])
        else:
            return max(array[val - array > 0])
    except:
        # to prevent wackiness, this bug is not particularly
        # substantial but should fix if we have time
        return val
        
        

def cryptoVix(coin, current_date, r, N_iter, N_paths):
    
    vix = np.empty((N_iter,))
    for i in np.arange(N_iter):
    
        # near and next options strip
        near_strip, next_strip = get_options_strip(coin, current_date, r, N_paths)

        # get idx where calls and puts differ the least
        near_closest_idx = near_strip.mean(axis=1).idxmin()
        next_closest_idx = next_strip.mean(axis=1).idxmin()

        T_1 = 5/365
        T_2 = 30/365

        # near and next forward prices
        F_near = near_closest_idx + (np.exp(r * T_1) * \
                    (near_strip.loc[near_closest_idx, 'Calls'] - \
                     near_strip.loc[near_closest_idx, 'Puts']))

        F_next = next_closest_idx + (np.exp(r * T_2) * \
                    (next_strip.loc[next_closest_idx, 'Calls'] - \
                     next_strip.loc[next_closest_idx, 'Puts']))

        # near/next strikes to find K_0s
        ks_near = near_strip.index.values
        ks_next = next_strip.index.values
        
        

        k_0_near_call = closest_call_or_put(near_closest_idx, ks_near, 'call')
        k_0_near_put = closest_call_or_put(near_closest_idx, ks_near, 'put')

        k_0_next_call = closest_call_or_put(next_closest_idx, ks_next, 'call')
        k_0_next_put = closest_call_or_put(next_closest_idx, ks_next, 'put')

        # strikes given by np.linspace so the delta for strikes is constant
        # therefore sufficient to calc one delta
        delta_near = np.abs((ks_near[1] - ks_near[0]) / 2)
        delta_next = np.abs((ks_next[1] - ks_next[0]) / 2)

        # near and next strikes for calls and puts to be calculated
        ks_near_puts = ks_near[ks_near < k_0_near_put]
        ks_near_calls = ks_near[ks_near > k_0_near_call]
        ks_next_puts = ks_next[ks_next < k_0_next_put]
        ks_next_calls = ks_next[ks_next > k_0_next_call]

        # calculate near vol
        near_sum = 0
        for k in ks_near_puts:
            near_sum = near_sum + near_strip.loc[k, 'Puts'] / (k**2)
        for k in ks_near_calls:
            near_sum = near_sum + near_strip.loc[k, 'Calls'] / (k**2)

        sigma_2_near = (np.exp(r * T_1) * delta_near * (2 / T_1) * near_sum) - \
            ((1 / T_1) * (((F_near / near_closest_idx - 1)**2)))

        # calculate next vol
        next_sum = 0
        for k in ks_next_puts:
            next_sum += next_strip.loc[k, 'Puts'] / (k**2)
        for k in ks_next_calls:
            next_sum += next_strip.loc[k, 'Calls'] / (k**2)


        sigma_2_next = (np.exp(r * T_2) * delta_next * (2 / T_2) * next_sum) - \
            ((1 / T_2) * (((F_next / near_closest_idx - 1)**2)))

        vix[i] = 100 * np.sqrt(((T_1 * sigma_2_near) + (T_2 * sigma_2_next)))
        
    return(np.nanmean(vix))


def coin_vix(coin):
    # create vix for a given coin
    
    # for replicability
    np.random.seed(109)
    dates = coin.full_data['Date'][:-31]
    vix = np.empty((len(dates,)))
    
    # create vix for each date
    for i in tqdm.trange(len(dates,)):
        
        vix[i] = cryptoVix(coin, dates[i], 0, 4, 100)

    out_series = pd.Series(vix)
    out_series.index = dates
    return out_series