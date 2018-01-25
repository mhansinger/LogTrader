import pandas as pd
import time
import os.path
import requests
import copy
import numpy as np

class poloStream(object):
    def __init__(self, url='https://poloniex.com/public?command=returnTicker', limit=100):
        '''
        Get % change from Poloniex
        '''

        self.url = url
        self.max_len = limit
        #get a json data file
        data = requests.get(self.url).json()

        # checks out all BTC pairs at poloniex
        self.BTC_PAIRS = []
        for f in data:
            if f[0:3] == 'BTC':
                self.BTC_PAIRS.append(f)

        self.BTC_PAIRS.sort()
        self.columns = copy.copy(self.BTC_PAIRS)
        self.columns.insert(0,'Date')
        self.columns.insert(0,'Unixtime')

        price = []
        volume = []

        for idx, pair in enumerate(self.BTC_PAIRS):
            data_coin = data[pair]
            price.append(float(data_coin['last']))
            volume.append(float(data_coin['baseVolume']))

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        price.insert(0,date)
        volume.insert(0,date)
        price.insert(0,unixtime)
        volume.insert(0,unixtime)
        self.priceHistory = pd.DataFrame([price], columns=self.columns)
        self.volumeHistory = pd.DataFrame([volume], columns=self.columns)
        self.logReturnHistory = pd.DataFrame([np.zeros(len(volume))], columns=self.columns)

    def getTicker(self):
        # get the Data from poloniex
        data = requests.get(self.url).json()
        return data

    def updateHistory(self):
        # updates the market history
        data = self.getTicker()
        price = []
        volume = []
        for idx, pair in enumerate(self.BTC_PAIRS):
            data_coin = data[pair]
            price.append(float(data_coin['last']))
            volume.append(float(data_coin['baseVolume']))

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        price.insert(0,date)
        volume.insert(0,date)
        price.insert(0,unixtime)
        volume.insert(0,unixtime)
        thisPrice = pd.DataFrame([price], columns=self.columns)
        thisVolume = pd.DataFrame([volume], columns=self.columns)

        self.priceHistory=self.priceHistory.append(thisPrice,ignore_index=True)
        self.volumeHistory=self.volumeHistory.append(thisVolume,ignore_index=True)

        #dummy
        thislogRet = pd.DataFrame([volume], columns=self.columns)
        for p in self.BTC_PAIRS:
            # ptc_change[p] = price[p].ptc_change()
            thislogRet[p] = np.log(self.priceHistory[p].iloc[-1]) - np.log(self.priceHistory[p].shift(-2))

        thislogRet = thislogRet.fillna(0)
        self.logReturnHistory = self.logReturnHistory.append(thislogRet)

        # cut the data set if it gets to long
        if len(self.priceHistory) > self.max_len:
            self.volumeHistory = self.volumeHistory[-self.max_len:-1]
            self.priceHistory = self.priceHistory[-self.max_len:-1]
            self.logReturnHistory = self.logReturnHistory[-self.max_len:-1]

