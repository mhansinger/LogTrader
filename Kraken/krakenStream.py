
import pandas as pd
import numpy as np
import krakenex
import time
import os

class krakenStream(object):
    def __init__(self, input, limit=600):
        '''
        Object streamt über krakenex.API die aktuellen Marktpreise
        :param asset1: 'XETH'
        :param asset2: 'XXBT'
        '''

        self.__asset1 = input.asset1
        self.__asset2 = input.asset2
        self.limit = int(limit)
        self.__k = krakenex.API()
        self.__pair = self.__asset1 + self.__asset2
        self.__columns = ['UnixTime','Time','Price','LogReturn']
        self.marketHistory = pd.DataFrame([np.zeros(len(self.__columns))], columns=self.__columns)

        print('Your pairs are:')
        print(self.__asset1)
        print(self.__asset2)

    def market_price(self):
        market = self.__k.query_public('Ticker', {'pair': self.__pair})['result'][self.__pair]['c']
        return float(market[0])

    def getLogReturn(self,X1,X0):
        # computes the log returns
        logRet = np.log(X1)-np.log(X0)
        return logRet

    def updateHistory(self):
        # write the current market price into the history
        __thisPrice = self.market_price()
        __time = time.strftime("%m.%d.%y_%H:%M:%S", time.localtime())
        __unix = int(time.time())

        # get the current log return
        __logRet = self.getLogReturn(X1=__thisPrice, X0=self.marketHistory['Price'].iloc[-1])

        temp = [[__unix,__time, __thisPrice,__logRet]]
        temp_df = pd.DataFrame(temp, columns=self.__columns)

        # now update the history with append
        self.marketHistory = self.marketHistory.append(temp_df,ignore_index=True)
        # limit the series to max. length
        if len(self.marketHistory)>self.limit:
            self.marketHistory = self.marketHistory.iloc[-self.limit:-1]
        print('\n Market history is updated:\n',temp_df)

    def writeHist(self):
        pd.DataFrame.to_csv(self.marketHistory, self.__pair + '_history.csv')







