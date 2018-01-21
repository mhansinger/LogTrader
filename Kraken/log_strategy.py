
import numpy as np
import threading
import time
from datetime import datetime
import sys


# Überlegung die windows hier zu definieren??

'''
this ist the strategy class for the log return method

@author: mhansinger
'''

class log_strategy(object):
    def __init__(self, myinput, broker, stream):
        #threading.Thread.__init__(self)
        self.time_series = []
        self.stream = stream        # object, to be instantialized outside
        self.Broker = broker        # object, to be instantialized outside
        self.myinput = myinput      # object, to be instantialized outside
        self.buytime =0
        try:
            self.minDrop = myinput.minDrop
            self.minGain = myinput.minGain
            self.exittime = myinput.exittime
        except:
            print('Check your input parameters!')

        # IMPORTANT: Broker muss initialisiert werden!
        self.Broker.initialize()

    def marketScanner(self):

        # get last buy price
        # ... hier noch nicht!
        #lastbuy = self.Broker.lastbuy

        #######################################
        # get market data and log return!
        self.stream.updateHistory()
        thisLogReturn = self.stream.marketHistory['LogReturn'].iloc[-1]   # current log return
        thisMarketPrice = self.stream.marketHistory['Price'].iloc[-1]
        #######################################

        if thisLogReturn < self.minDrop and self.Broker.asset_status is False and self.Broker.get_broker_status() is False:
            # buys if we are short and criteria is fulfilled
            self.Broker.buy_order()
            self.buytime = int(time.time())
            print('go long')
            print('log Return: ', thisLogReturn)
            print('bought in at: ', self.Broker.lastbuy)
            print(' ')

        elif self.Broker.asset_status and self.Broker.get_broker_status() is False:
            thisTime = int(time.time())
            # we are now in the market and check if we should sell!
            # --> last buy has to be checked from csv maybe... !!
            if thisMarketPrice >= (1+self.minGain)*self.Broker.lastbuy:
                self.Broker.sell_order()
                print('go short')
                print('sold at: ', self.Broker.lastsell)
                print('Reward: ', (self.Broker.lastsell-self.Broker.lastbuy)/self.Broker.lastsell)
                print(' ')
            elif (thisTime-self.buytime)/60. > self.exittime:
                self.Broker.sell_order()
                print('Emergency exit!')
                print('sold at: ', self.Broker.lastsell)
                print('Reward: ', (self.Broker.lastsell - self.Broker.lastbuy) / self.Broker.lastsell)
                print(' ')
            else:
                self.Broker.idle()
        else:
            self.Broker.idle()



