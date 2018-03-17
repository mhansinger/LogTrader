import pandas as pd
import time
import os.path
import requests
import copy
import numpy as np
import time

class bittrexStream(object):
    '''
    To stream the bittrex market data while trader is running
    '''
    def __init__(self, url='https://bittrex.com/api/v1.1/public/getmarketsummaries', limit=40):
        '''
        Get % change from bittrex
        '''
        self.url = url
        self.max_len = int(limit)
        self.__shift = int(1)

        # small constant to add for log to be not 0
        self.SMALL = 1e-15

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
        bid = []
        ask = []

        # write the first line for the histor
        for idx, pairs in enumerate(self.BTC_PAIRS):
            data_coin = data[idx]
            price.append(float(data_coin['Last']))
            volume.append(float(data_coin['BaseVolume']))
            bid.append(float(data_coin['Bid']))
            ask.append(float(data_coin['Ask']))

        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        price.insert(0,date)
        volume.insert(0,date)
        bid.insert(0,date)
        ask.insert(0,date)
        price.insert(0,unixtime)
        volume.insert(0,unixtime)
        bid.insert(0,unixtime)
        ask.insert(0,unixtime)
        self.priceHistory = pd.DataFrame([price], columns=self.columns)
        self.volumeHistory = pd.DataFrame([volume], columns=self.columns)
        self.bidHistory = pd.DataFrame([bid], columns=self.columns).fillna(0)
        self.askHistory = pd.DataFrame([ask], columns=self.columns).fillna(0)
        self.logReturnHistory = pd.DataFrame([np.zeros(len(volume))], columns=self.columns)

    def getTicker(self):
        # get the Data from bittrex
        try:
            data = requests.get(self.url).json()['result']
        except ValueError:
            print('There was a ValueError in getTicker')
            time.sleep(60)
            return self.getTicker()
        return data

    def updateHistory(self):
        ''' updates the market history '''
        bittrex_data = self.getTicker()
        price = []
        volume = []
        bid = []
        ask = []
        bittrex_coinlist = []
        index_list = []
        id_count = 0

        # create a data dictionary and fill it with the current market data
        coins_dict = {key: [0, 0, 0, 0] for (key) in self.BTC_PAIRS}
        for idx, coin in enumerate(self.BTC_PAIRS):
            for i in range(0, len(bittrex_data)):
                coins_passed = 0
                if coin == bittrex_data[i]['MarketName']:
                    coins_dict[coin][0] = bittrex_data[i]['Last']
                    coins_dict[coin][1] = bittrex_data[i]['BaseVolume']
                    coins_dict[coin][2] = bittrex_data[i]['Ask']
                    coins_dict[coin][3] = bittrex_data[i]['Bid']

        # fill up the individual lists
        for coin in self.BTC_PAIRS:
            price.append(float(coins_dict[coin][0]))
            volume.append(float(coins_dict[coin][1]))
            bid.append(float(coins_dict[coin][2]))
            ask.append(float(coins_dict[coin][3]))


        date = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        unixtime = int(time.time())

        price.insert(0,date)
        volume.insert(0,date)
        bid.insert(0,date)
        ask.insert(0,date)
        price.insert(0,unixtime)
        volume.insert(0,unixtime)
        bid.insert(0,unixtime)
        ask.insert(0,unixtime)

        thisPrice = pd.DataFrame([price], columns=self.columns)
        thisVolume = pd.DataFrame([volume], columns=self.columns)
        thisBid = pd.DataFrame([bid], columns=self.columns)
        thisAsk = pd.DataFrame([ask], columns=self.columns)

        self.priceHistory = self.priceHistory.append(thisPrice, ignore_index=True)
        self.volumeHistory = self.volumeHistory.append(thisVolume,ignore_index=True)
        self.bidHistory = self.bidHistory.append(thisBid, ignore_index=True)
        self.askHistory = self.askHistory.append(thisAsk, ignore_index=True)

        # compute the log return of market price for every coin pair.
        self.logReturnHistory= np.log(self.askHistory[self.BTC_PAIRS] + self.SMALL) - \
                     np.log(self.askHistory[self.BTC_PAIRS].shift(self.__shift) + self.SMALL)
        self.logReturnHistory.insert(0,'Date', self.askHistory['Date'].values)
        self.logReturnHistory.insert(0,'Unixtime', self.askHistory['Unixtime'].values)
        self.logReturnHistory.fillna(0)

        # cut the data set if it gets to long
        if len(self.priceHistory) > self.max_len:
            self.volumeHistory = self.volumeHistory[-self.max_len:-1]
            self.priceHistory = self.priceHistory[-self.max_len:-1]
            self.logReturnHistory = self.logReturnHistory[-self.max_len:-1]
            self.bidHistory = self.bidHistory[-self.max_len:-1]
            self.askHistory = self.askHistory[-self.max_len:-1]

    def setShift(self,shift):
        try:
            assert shift > 0
            assert type(shift) == int
        except AssertionError:
            print('Value must be bigger 0 and INT')
        self.__shift = shift