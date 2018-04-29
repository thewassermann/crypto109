# crypto109
cs109 crypto data science project

## Calculated Vix indicies 

The vix indexes of 15 coins (all except Monero, which had some corrupted data) are in the 100_paths folder. These were parameterized at 4 iterations of 100 paths.

To load the pickled file run:

```
import pickle

coin_vixes = {}
for coin_name in coin_names:
    filename = '100_paths/4_iter_'+coin_name+'.pkl'
    with open(filename, 'rb') as f:
        coin_vixes[coin_name] = pickle.load(f)
```
