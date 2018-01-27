import pandas as pd
import time
import os.path
import requests
import copy
import numpy as np

class bittrexStream(object):
    '''
    To stream the bittrex market data while trader is running
    '''
    def __init__(self, url='https://bittrex.com/api/v1.1/public/getmarketsummaries', limit=100):
        '''
        Get % change from bittrex
        '''
        self.url = url
        self.max_len = limit
        self.__shift = -1

        #get a json data file
        data = requests.get(self.url).json()['result']

        # checks out all BTC pairs at bittrex
        self.BTC_PAIRS = []
        for f in range(len(data)):
            if data[f]['MarketName'][0:3] == 'BTC':
                self.BTC_PAIRS.append(data[f]['MarketName'])

        #self.BTC_PAIRS.sort()
        self.columns = copy.copy(self.BTC_PAIRS)
        self.columns.insert(0,'Date')
        self.columns.insert(0,'Unixtime')

        price = []
        volume = []

        # write the first line for the histor
        for idx, pair in enumerate(self.BTC_PAIRS):
            data_coin = data[idx]
            price.append(float(data_coin['Last']))
            volume.append(float(data_coin['BaseVolume']))

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
        # get the Data from bittrex
        data = requests.get(self.url).json()['result']
        return data

    def updateHistory(self):
        # updates the market history
        data = self.getTicker()
        price = []
        volume = []
        for idx, pair in enumerate(self.BTC_PAIRS):
            data_coin = data[idx]
            price.append(float(data_coin['Last']))
            volume.append(float(data_coin['BaseVolume']))

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
            thislogRet[p] = np.log(self.priceHistory[p].iloc[-1]) - np.log(self.priceHistory[p].shift(self.__shift))

        thislogRet = thislogRet.fillna(0)
        self.logReturnHistory = self.logReturnHistory.append(thislogRet)

        # cut the data set if it gets to long
        if len(self.priceHistory) > self.max_len:
            self.volumeHistory = self.volumeHistory[-self.max_len:-1]
            self.priceHistory = self.priceHistory[-self.max_len:-1]
            self.logReturnHistory = self.logReturnHistory[-self.max_len:-1]

    def setShift(self,shift):
        try:
            assert shift < 0
            assert type(shift) == int
        except AssertionError:
            print('Value must be smaller 0 and INT')
        self.__shift = shift