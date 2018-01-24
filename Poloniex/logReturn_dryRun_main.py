'''
This is the main file to run the trading bot

@author: mhansinger
'''

from __init__ import *
from datetime import datetime


# set the input data with default values
# adjust the windows to our time series!!!
XETH_input = set_input(asset1='XETH', asset2='XXBT', fee=0.0016,  investment=100.0,minDrop=-0.016, minGain=0.016, exittime=200)
XETH_stream = krakenStream(XETH_input, limit=600)
XETH_broker = Broker_virtual(XETH_input)s

# check the stream history: Important!
XETH_stream.updateHistory()
XETH_stream.updateHistory()


XETH_trade = log_strategy(XETH_input,XETH_broker,XETH_stream)

def run_trader(interval=60):
    try:
        XETH_trade.marketScanner()
        t=threading.Timer(interval, run_trader)
        t.start()
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('Wird erneut gestartet...\n')
        run_trader()


