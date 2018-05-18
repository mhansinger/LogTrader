'''
This is the main file to run the trading bot

@author: mhansinger
'''

from __init__ import *
from datetime import datetime

# set the input data with default values
BITTREX_input = set_input(asset1='ETH', asset2='BTC', fee=0.0025,  investment=100.0, minDrop=-0.03075, minGain=0.0135, exittime=400, minVolume=700,peak=0.01,emergency=0.97)
BITTREX_stream = bittrexStream(limit=200)
BITTREX_broker = Broker_virtual_Bittrex(BITTREX_input)

# check the stream history: Important!
BITTREX_stream.updateHistory()
for i in range(10):
    BITTREX_stream.updateHistory()

# compute the log return for a window of 10 min
BITTREX_stream.setShift(5)

BITTREX_trade = log_strategy(BITTREX_input,BITTREX_broker,BITTREX_stream)

# me sure to set correct interval according to minDrop and minGain
def run_trader(interval=60):
    try:
        BITTREX_trade.marketScanner()
        t = threading.Timer(interval, run_trader)
        t.start()
    except:
        print("Fehler: ")
        print('Wird erneut gestartet...\n')
        run_trader()


