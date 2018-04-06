"""
Option pricing functions
"""

import numpy as np
import pandas as pd
import crypto_object as co
import sys
from datetime import timedelta

def random_paths(coin, current_date, expiry_date, lookback=90, N=100):
	"""
	Function that produces random crypto price curves based on a lookback window
	of historical values

	
	Parameters
	----------

		coin : crypto_object.Coin


		current_date : Datetime
			t = 0 for the operation
	
		expiry_date : Datetime
			expiry date of the option

		lookback : int
			number of previous days to draw returns from

		N : int
			number of streams to create
	"""

	# create data frame to store values
	N_days = (expiry_date - current_date).days 
	paths = np.empty((N_days, N))

	# ensure that lookback window is possible
	longest_lookback = current_date - timedelta(days=lookback)
	if longest_lookback not in set(coin.full_data['Date']):
		print('ERROR: lookback window not possible with current start date')
		sys.exit(1)

	starting_index = np.argwhere(coin.full_data['Date'] == current_date)[0][0]
	starting_price = coin.full_data['Close'][starting_index]

	for path_num in np.arange(N):

		# select a random return within lookback
		px = starting_price

		for offset in np.arange(N_days):

			# pct returns to select from
			lb_start = starting_index + offset
			lb_end = lb_start + lookback
			possible_returns = coin.full_data.loc[lb_start:(lb_end + 1), 'Pct Returns'].values
			px = px * (1 + np.random.choice(possible_returns))
			paths[N_days - offset - 1, path_num] = px

	paths = pd.DataFrame(paths)
	paths.index = [current_date + timedelta(days=int(x)) for x in np.arange(N_days)]
	return(paths)


def empirical_method(coin, current_date, expiry_date, r, K, call_or_put, lookback=90, N=100):
	"""
	Function that uses the empirical distribution
	of crypto prices to calculate option prices. 

	
	Parameters
	----------

		coin : crypto_object.Coin


		current_date : Datetime
			t = 0 for the operation
	
		expiry_date : Datetime
			expiry date of the option

		r : float
			risk-free interest rate

		K : float
			exercise price

		call_or_put : str
			option type

		lookback : int
			number of previous days to draw returns from

		N : int
			number of streams to create
	"""

	rps = random_paths(coin, current_date, expiry_date, lookback=lookback, N=N)

	# final value for paths
	final_values = rps.iloc[0, :]

	# payout given final values
	if call_or_put == 'call':
		payout = [np.clip(x - K, 0, None) for x in final_values]
	elif call_or_put == 'put':
		payout = [np.clip(K - x, 0, None) for x in final_values]


	N_days = (expiry_date - current_date).days
	discount_factor = (1 + ((N_days/365) * r))**-1

	# get empirical price
	emp_price = np.nanmean(payout) * discount_factor

	# ensure that these prices obey the call /put inequalities
	# TODO

	return emp_price



