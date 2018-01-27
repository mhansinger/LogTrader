
import numpy as np

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
            self.minVolume = myinput.minVolume
        except:
            print('Check your input parameters!')

        # IMPORTANT: Broker muss initialisiert werden!
        self.Broker.initialize()

    def marketScanner(self):
        # this is the core module of the trader
        #######################################
        # get market data and log return!
        self.stream.updateHistory()

        # NEW!!!
        # find first relevant Coins which fulfil VOL criteria, then check for drop in log return
        volList = []
        for loc, coin in enumerate(self.stream.BTC_PAIRS):
            if self.stream.volumeHistory[coin].iloc[-1] > self.minVolume:
                volList.append(coin)

        thisMaxDrop = self.stream.logReturnHistory[volList].iloc[-1].min()
        thisMaxDropCoin = self.stream.logReturnHistory[volList].iloc[-1].idxmin()
        thisMaxVolume = self.stream.volumeHistory[thisMaxDropCoin].iloc[-1]

        print('MaxDrop:', thisMaxDrop)
        print('Coin: ',thisMaxDropCoin)
        print('Volume: ',thisMaxVolume)
        print('\n')

        #######################################
        # check the criteria required to buy
        if thisMaxDrop < self.minDrop and thisMaxVolume>self.minVolume and self.Broker.asset_status is False \
                and self.Broker.get_broker_status() is False:
            # buys if we are short and criteria is fulfilled

            # hand over the coin pair
            self.Broker.setPair(thisMaxDropCoin)

            self.Broker.buy_order()
            self.buytime = int(time.time())
            # store the coin we bought
            print('go long')
            print('Buy: ',self.Broker.pair)
            print('log Return: ', thisMaxDrop)
            print('bought in at: ', self.Broker.lastbuy)
            print(' ')

        elif self.Broker.asset_status and self.Broker.get_broker_status() is False:
            thisTime = int(time.time())
            # we are now in the market and check if we should sell!
            # --> last buy has to be checked from csv maybe... !!
            thisMarketPrice = self.stream.priceHistory[self.Broker.pair].iloc[-1]

            if thisMarketPrice >= (1.0+self.minGain)*self.Broker.lastbuy:
                # hand over the coin pair
                self.Broker.sell_order()
                print('go short')
                print('Sell: ', self.Broker.pair)
                print('sold at: ', self.Broker.lastsell)
                print('Gain: ', (self.Broker.lastsell-self.Broker.lastbuy)/self.Broker.lastsell)
                print(' ')
            elif (thisTime-self.buytime)/60. > self.exittime:
                # hand over the coin pair
                self.Broker.sell_order()
                print('Emergency exit!')
                print('sold at: ', self.Broker.lastsell)
                print('Gain: ', (self.Broker.lastsell - self.Broker.lastbuy) / self.Broker.lastsell)
                print(' ')
            else:
                self.Broker.idle()
        else:
            self.Broker.idle()



