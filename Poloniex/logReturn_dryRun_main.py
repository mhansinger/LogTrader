'''
This is the main file to run the trading bot

@author: mhansinger
'''

from __init__ import *
from datetime import datetime

# set the input data with default values
# adjust the windows to our time series!!!
POLO_input = set_input(asset1='ETH', asset2='BTC', fee=0.002,  investment=100.0, minDrop=-0.04, minGain=0.02, exittime=200, minVolume=150)
POLO_stream = poloStream(limit=100)
POLO_broker = Broker_virtual_Poloniex(POLO_input)
#POLO_broker.initialize()

# check the stream history: Important!
POLO_stream.updateHistory()
POLO_stream.updateHistory()

POLO_trade = log_strategy(POLO_input,POLO_broker,POLO_stream)

def run_trader(interval=600):
    try:
        POLO_trade.marketScanner()
        t=threading.Timer(interval, run_trader)
        t.start()
    except KeyboardInterrupt:
        pass
    except:
        print("Fehler: ", sys.exc_info()[0])
        print('Wird erneut gestartet...\n')
        run_trader()



