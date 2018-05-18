
import time
import copy
import pandas as pd
try:
    from Telegram_Bot.Telepot_engine import Telepot_engine
except:
    pass

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
        self.buytime = 0

        # this is the list where all temporary BAD coins are stored for temporary blockage
        self.block_coin = pd.DataFrame(columns=['UNIX', 'Pair'])
        self.block_coin = self.block_coin.append({'UNIX': time.time()//1, 'Coin': '-'}, ignore_index=True)

        # blocking time in hours
        #!!!!!!!!!!!!
        # this is yet hard coded
        self.blockingTime = 10

        try:
            self.Telepot_engine = Telepot_engine()
            self.Telepot_engine.alive()
            self.active_engine = True
            print('Telegram engine is activated!')
        except:
            print('No Telegram engine activated')
            self.active_engine = False

        try:
            self.minDrop = myinput.minDrop
            self.minGain = myinput.minGain
            self.exittime = myinput.exittime
            self.minVolume = myinput.minVolume
            self.peak = myinput.peak

        except:
            print('Check your input parameters!')

        # IMPORTANT: Broker muss initialisiert werden!
        self.Broker.initialize()

    #######################################
    # this is the core module of the trader
    #######################################
    def marketScanner(self):

        # get market data and log return!
        self.stream.updateHistory()

        # find first relevant Coins which fulfil VOL criteria, then check for drop in log return
        volList = []
        for loc, coin in enumerate(self.stream.BTC_PAIRS):
            if self.stream.volumeHistory[coin].iloc[-1] > self.minVolume and self.stream.priceHistory[coin].iloc[-1] > 0.0:
                volList.append(coin)

        # check for recent peaks in the history
        thisMaxDrop, thisMaxDropCoin ,thisMaxVolume = self.peak_check(thisList=volList)

        print('MaxDrop:', thisMaxDrop)
        print('Coin: ',thisMaxDropCoin)
        print('Volume: ',thisMaxVolume)
        print('\n')


        # this is a new approach
        if self.Broker.asset_status is False and self.Broker.get_broker_status() is False and \
                self.isNotNull(thisCoin=thisMaxDropCoin):

            # update the block_coin list and remove all the expired coins
            delta = time.time() - 60*self.blockingTime
            self.block_coin = self.block_coin[self.block_coin.UNIX > delta]

            # check for bad coins and run again the peak check
            if thisMaxDropCoin in self.block_coin:
                thisMaxDrop, thisMaxDropCoin, thisMaxVolume = self.removeBadCoin(thisMaxDropCoin, volList)


            #######################################
            # check the criteria required to buy, these are:
            # drop is bigger than criteria, base volume, broker is not working, price did not drop to 0 (e.g. database error)
            if thisMaxDrop < self.minDrop and thisMaxVolume > self.minVolume:
                # buys if we are short and criteria is fulfilled

                # hand over the coin pair
                self.Broker.setPair(thisMaxDropCoin)

                # Order set
                self.Broker.buy_order()

                self.buytime = int(time.time())
                # store the coin we bought
                print('go long')
                print('Buy: ', self.Broker.pair)
                print('log Return: ', thisMaxDrop)
                print('bought in at: ', self.Broker.lastbuy)
                print(' ')

                # sends a telegram message
                if self.active_engine:
                    invest = self.Broker.balance_df['BTC'].iloc[-2]
                    self.Telepot_engine.sendMsg(coin=self.Broker.pair, investment=str(round(invest, 5)),
                                                price=str(round(self.Broker.lastbuy, 6)), kind='BUY')


        elif self.Broker.asset_status and self.Broker.get_broker_status() is False:
            thisTime = int(time.time())
            # we are now in the market and check if we should sell!
            # --> the bid price is here important as it should be sold
            thisBidPrice = self.stream.bidHistory[self.Broker.pair].iloc[-1]

            # checks for an emergency exit
            if thisBidPrice < (self.Broker.lastbuy * self.myinput.emergency):
                emergencyExit = True
            else:
                emergencyExit = False


            if thisBidPrice >= (1.0+self.minGain)*self.Broker.lastbuy:
                # Order set
                self.Broker.sell_order()

                print('go short')
                print('Sell: ', self.Broker.pair)
                print('sold at: ', self.Broker.lastsell)
                print('Gain: ', (self.Broker.lastsell-self.Broker.lastbuy)/self.Broker.lastsell)
                print(' ')

                # sends a telegram message
                if self.active_engine:
                    invest = self.Broker.balance_df['BTC'].iloc[-1]
                    self.Telepot_engine.sendMsg(coin=self.Broker.pair, investment=str(round(invest,5)),
                                                price=str(round(self.Broker.lastsell,6)), kind='SELL')

            elif (thisTime-self.buytime)/60. > self.exittime or emergencyExit:
                # hand over the coin pair
                self.Broker.sell_order()
                print('Stop Loss')
                print('sold at: ', self.Broker.lastsell)
                print('Gain: ', (self.Broker.lastsell - self.Broker.lastbuy) / self.Broker.lastsell)
                print(' ')

                # sends a telegram message if active
                if self.active_engine:
                    invest = self.Broker.balance_df['BTC'].iloc[-1]
                    self.Telepot_engine.sendMsg(coin=self.Broker.pair, investment=str(round(invest,6)),
                                                price=str(round(self.Broker.lastsell,6)), kind='EXIT')

            else:
                self.Broker.idle()
        else:
            self.Broker.idle()

    def peak_check(self, thisList):
        # checks for the peaks in the history of coin data
        if thisList == []:
            print('List is empty, no coinvolume is over: ',self.peak)
            print('Return default')
            return 0.0, 'BTC-ETH', 100
        else:
            try:
                thisMaxDrop = self.stream.logReturnHistory[thisList].iloc[-1].min()
                thisMaxDropCoin = self.stream.logReturnHistory[thisList].iloc[-1].idxmin()
                thisMaxVolume = self.stream.volumeHistory[thisMaxDropCoin].iloc[-1]
                if self.stream.logReturnHistory[thisMaxDropCoin].iloc[-10:-1].max() > self.peak \
                        and thisMaxDrop < self.minDrop:
                    # remove the 'bad' coin and run again the check (recursive)
                    newList = copy.copy(thisList)
                    newList.remove(thisMaxDropCoin)
                    return self.peak_check(thisList=newList)
                else:
                    return thisMaxDrop, thisMaxDropCoin, thisMaxVolume

            except ValueError:
                # in case of an error return sth. which will not cause a buy order:
                print('ValueError in peak check ...')
                return 0.0, 'BTC-ETH', 100


    def isNotNull(self,thisCoin):
        # checks if the current price is not = 0
        # e.g., due to a bug in the database...
        if self.stream.volumeHistory[thisCoin].iloc[-1] > 0:
            return True
        else:
            return False

    def setblockingTime(self,time):
        # set the blocking time
        self.blockingTime = abs(time)

    def getblockingTime(self):
        # return the blocking time
        print(self.blockingTime)

    def removeBadCoin(self,thisList,thisMaxDropCoin):
        thisList.remove(thisMaxDropCoin)
        thisMaxDrop, thisMaxDropCoin, thisMaxVolume = self.peak_check(thisList=thisList)
        if thisMaxDropCoin in thisList:
            self.removeBadCoin(thisList, thisMaxDropCoin)
        else:
            return thisMaxDrop, thisMaxDropCoin, thisMaxVolume

    # should contain a method to check for open orders... e.g.:
    #def orderCheck(self):
    #    orders = self.Broker.openOrders()
    #    ....


