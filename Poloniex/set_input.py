# Object container for all input relevant data
import pandas as pd

class set_input():
    ''' 
        Input data-object

        @author: mhansinger
    '''
    def __init__(self, asset1='XETH', asset2='XXBT',investment=100.0, fee=0.0016, minDrop=-0.016, minGain=0.016, exittime=200):
        '''

        :param asset1:
        :param asset2:
        :param investment:  For dry run, the initial investment
        :param fee:         Trading fee, for dry run
        :param minDrop:     drop of log return in time series, as criteria to issue an order
        :param minGain:     expected minimum gain per order
        :param exittime:    if minGain cannot be achieved the market will be left after xy minutes
        '''

        self.fee = fee
        #self.reinvest = reinvest
        self.asset1 = asset1
        self.asset2 = asset2
        self.investment = investment
        self.minDrop = minDrop
        self.minGain = minGain
        self.exittime = exittime
        try:
            assert self.minDrop < 0.
        except AssertionError:
            print('Your drop parameter should be below 0!')

        try:
            assert self.minGain < 0.5
        except AssertionError:
            print('Dont be greedy! "minGain" is not in percent; e.g., 0.015')


