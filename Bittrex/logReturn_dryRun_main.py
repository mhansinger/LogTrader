'''
This is the main file to run the trading bot

@author: mhansinger
'''

from __init__ import *
from datetime import datetime

# set the input data with default values
# adjust the windows to our time series!!!
BITTREX_input = set_input(asset1='ETH', asset2='BTC', fee=0.002,  investment=100.0, minDrop=-0.001, minGain=0.00001, exittime=25, minVolume=150)
BITTREX_stream = bittrexStream(limit=200)
BITTREX_broker = Broker_virtual_Bittrex(BITTREX_input)
#POLO_broker.initialize()

# check the stream history: Important!
BITTREX_stream.updateHistory()
BITTREX_stream.updateHistory()

BITTREX_trade = log_strategy(BITTREX_input,BITTREX_broker,BITTREX_stream)

# me sure to set correct interval according to minDrop and minGain
def run_trader(interval=60):
    try:
        BITTREX_trade.marketScanner()
        t = threading.Timer(interval, run_trader)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('Wird erneut gestartet...\n')
        run_trader()



