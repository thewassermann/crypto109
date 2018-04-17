import numpy as np
import pandas as pd

class Coin():
	"""
	Class to store all data related to a particular
	cryptocurrency

	Parameters
	----------

		name : str
			name of coin object

		data_path : str
			file path for data object 
	"""


	def __init__(self, name, data_path):
		self.name = name
		self.full_data = pd.read_csv(data_path, parse_dates=['Date'])
		self.full_data['Pct Returns'] = self.pct_returns()


	def pct_returns(self):
		"""
		Function to add percent returns to the data
		of the crypto object
		"""
		closes = self.full_data['Close'].values
		N_days = len(closes)

		# create vector to store values
		pct_ret = np.empty((N_days,))

		for i in np.arange(N_days-1):
			pct_ret[i] = (closes[i] - closes[i+1]) / closes[i+1]

		pct_ret[-1] = np.nan
		return pct_ret

