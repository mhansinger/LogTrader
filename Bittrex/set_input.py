# Object container for all input relevant data
import pandas as pd

class set_input():
    ''' 
        Input data-object

        @author: mhansinger
    '''
    def __init__(self, asset1='ETH', asset2='BTC',investment=100.0, fee=0.002, minDrop=-0.06, minGain=0.03, exittime=200, minVolume =150):
        '''

        :param asset1:      Check which exchange you are using
        :param asset2:
        :param investment:  For dry run, the initial investment
        :param fee:         Trading fee, for dry run
        :param minDrop:     drop of log return in time series, as criteria to issue an order
        :param minGain:     expected minimum gain per order
        :param exittime:    if minGain cannot be achieved the market will be left after xy minutes
        :param minVolume:   required minimum trading volume
        '''

        self.fee = fee
        #self.reinvest = reinvest
        self.asset1 = asset1
        self.asset2 = asset2
        self.investment = investment
        self.minDrop = minDrop
        self.minGain = minGain
        self.exittime = exittime
        self.minVolume = minVolume
        try:
            assert self.minDrop < 0.
        except AssertionError:
            print('Your drop parameter should be below 0!')

        try:
            assert self.minGain < 0.5
        except AssertionError:
            print('Dont be greedy! "minGain" is not in percent; e.g., 0.015')


