'''
These are the Broker classes, all inherited from abstract base class Brocker_base
The Broker connects, e.g., with the Kraken account and issues the orders

@author: mhansinger 

'''

import numpy as np
import pandas as pd
import krakenex
import time
from abc import ABC, abstractmethod
import requests
import os

try:
    from Twitter_Bot.twitterEngine import twitterEngine
except:
    print('No Twitter engine available!')

class Broker_base(ABC):
    #this is the abstract base class for the Broker object!
    def __init__(self, myinput):
        super().__init__()
        self.asset1 = myinput.asset1
        self.asset2 = myinput.asset2
        self.pair = myinput.asset1+myinput.asset2

        self.asset_status = False
        self.broker_status = False
        self.asset1_funds = []
        self.asset2_funds = []
        self.balance_all = []
        self.balance_df = []
        self.column_names = []
        self.lastbuy = 0
        self.lastsell = 0
        super(Broker_base,self).__init__()

    ##############################
    # Broker Methods for all
    ##############################
    # returns the broker status
    def get_broker_status(self):
        return self.broker_status

    def set_broker_status(self, status):
        self.broker_status = status

    def get_asset_status(self):
        return self.asset_status

    def set_asset_status(self,status):
        self.asset_status = status

    def getTime(self):
        #return int(time.time())
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

    def getUNIX(self):
        return int(time.time())

    def writeCSV(self,df):
        # write data to csv
        filename = self.pair+'_balance.csv'
        pd.DataFrame.to_csv(df,filename)

    ####################
    # Abstract methods to be defined
    ####################
    @abstractmethod
    def initialize(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def buy_order(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def sell_order(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def idle(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def asset_balance(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def asset_market_bid(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def asset_market_ask(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def market_price(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_asset1_balance(self):
        raise NotImplementedError("Please Implement this method")

    @abstractmethod
    def get_asset2_balance(self):
        raise NotImplementedError("Please Implement this method")

    #@abstractmethod
    def asset_check(self):
        # checks the assets on our account and sets the asset_status
        asset1 = self.get_asset1_balance()
        asset2 = self.get_asset2_balance()
        marketP = self.market_price()
        # normalize the price
        asset2_norm = asset2 / marketP
        # 95% off total volume on asset1 side
        if asset1 > (asset2_norm + asset1) * 0.95:
            self.asset_status = True
        else:
            self.asset_status = False

    @abstractmethod
    def check_order(self,id):
        raise NotImplementedError("Please Implement this method")




##############################################
class Broker_virtual_kraken(Broker_base):
    # this class is for dry run without conection to the exchange
    def __init__(self, myinput):
        super().__init__(myinput)

        self.k = krakenex.API()
        #self.k.load_key('kraken.key')
        self.balance_all = []
        self.fee = myinput.fee
        self.invest = myinput.investment


    def initialize(self):
        self.column_names = ['Time stamp', self.asset1, self.asset2, self.asset1+' shares', 'costs', self.asset1+' price']
        self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns= self.column_names)
        self.balance_df['Time stamp'] = self.getTime()
        self.balance_df[self.asset2] = self.invest
        self.balance_df[self.asset1+' price'] = self.asset_market_bid()

    def buy_order(self):
        self.broker_status = True

        if self.asset_status is False:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            current_eur_funds = balance_np[-1, 2] * 0.999999
            current_costs = current_eur_funds * self.fee

            asset_ask = self.asset_market_ask()

            new_shares = (current_eur_funds - current_costs) / asset_ask
            new_XETH = new_shares * asset_ask
            new_eur_fund = balance_np[-1, 2] - current_eur_funds

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares, current_costs, asset_ask ]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(' ')
            print(balance_update_df)
            print(' ')

            self.lastbuy=asset_ask

            self.asset_status = True

        else:
            print('No money to buy coins')

        self.broker_status = False


    def sell_order(self):
        self.broker_status = True

        if self.asset_status is True:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            asset_bid = self.asset_market_bid()
            current_shares = balance_np[-1, 3] * 0.999999
            current_costs = current_shares * asset_bid * self.fee

            new_eur_fund = current_shares * asset_bid - current_costs

            new_shares = balance_np[-1, 3] - current_shares  # --> sollte gegen null gehen
            new_XETH = new_shares * asset_bid

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares, current_costs, asset_bid]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(balance_update_df)
            print(' ')

            self.lastsell = asset_bid
            self.asset_status = False

        else:
            print('Nothing to sell')

        self.broker_status = False


    def idle(self):
        self.broker_status = True
        try:
            balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!')
        #
        if self.asset_status is True:
            market_price = self.asset_market_ask()
        elif self.asset_status is False:
            market_price = self.asset_market_bid()
        #
        new_shares = balance_np[-1,3]
        new_assets = new_shares*market_price
        new_eur_fund = balance_np[-1,2]
        current_costs = 0
        #
        # update time
        time = self.getTime()
        #
        # old is same as new
        balance_update_vec = [[time, new_assets, new_eur_fund, new_shares, current_costs, market_price]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)

        self.broker_status = False

    #def get_broker_status(self):
    #    return self.broker_status

    def asset_balance(self):
        #from abstract one
        print(self.balance_df.tail())

    def asset_market_bid(self):
        # from abstract one
        market_bid = self.k.query_public('Ticker', {'pair': self.pair})['result'][self.pair]['b']
        return float(market_bid[0])

    def asset_market_ask(self):
        # from abstract one
        market_ask = self.k.query_public('Ticker', {'pair': self.pair})['result'][self.pair]['a']
        return float(market_ask[0])

    def market_price(self):
        # from abstract one
        market = self.k.query_public('Ticker', {'pair': self.pair})['result'][self.pair]['c']
        return float(market[0])

    def get_asset2_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def get_asset1_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def asset_check(self):
        # from abstract one
        print('Not implemented in virtual...')

    def check_order(self,id):
        # from abstract one
        print('Not implemented in virtual...')


#################################################
class Broker_kraken(Broker_base):
    def __init__(self, myinput):
        super().__init__(myinput)
        self.k = krakenex.API()
        self.k.load_key('kraken.key')
        self.balance_all = []
        #self.balance_df = []
        self.lastbuy = 0
        self.order_id_sell = self.order_id_buy = []
        self.twitter=False
        try:
            self.twitterEngine = twitterEngine()
        except:
            print('No Twitter module enabled\n')

        #self.column_names = []

    def initialize(self):
        # initialisiert den Broker: stellt das dataFrame auf und holt die ersten Werte

        # check den asset_status von asset1 und stellt fest ob wir im Markt sind :
        self.asset_check()

        # checks if there aready exists a balance sheet as .csv
        if (os.path.exists(self.pair+'_balance.csv')):
            print(self.pair+'_balance.csv exists \n')
            old_df = pd.read_csv(self.pair+'_balance.csv')
            old_df = old_df.drop('Unnamed: 0',1)
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = old_df
        else:
            #sets up a new, empty data frame for the balance
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns=self.column_names)
            self.balance_df['Time stamp'] = self.getTime()
            self.balance_df[self.asset2] = self.get_asset2_balance()
            self.balance_df[self.asset1] = self.get_asset1_balance()
            self.balance_df['Buy/Sell'] = '-'
            self.balance_df['Market Price'] = self.market_price()
            self.balance_df['Order Id'] = '-'

        print(self.balance_df.tail())

    def buy_order(self):
        # executes a buy order

        self.set_broker_status(True)
        self.asset_check()
        # check den XBT balance
        current_asset2_funds = self.get_asset2_balance()

        # diese if abfrage ist ein double check
        if self.asset_status is False:
            #######################
            # kraken query
            # wir können keine Verkaufsorder auf XBT-basis setzen, sondern nur ETH kaufen.
            # Deshalb: Limit order auf Basis des aktuellen Kurses und Berechnung des zu kaufenden ETH Volumens.
            volume2 = current_asset2_funds
            ask = self.asset_market_ask()
            volume1 = round(((volume2 / ask) *0.9999 ),5)
            vol_str = str(round(volume1,5))     #round -> kraken requirement
            ask_str = str(ask)

            # limit order in test phase
            api_params = {'pair': self.pair,
                            'type':'buy',
                            'ordertype':'limit',    #'market',
                            'price': ask_str,
                            'volume': vol_str,
                            'trading_agreement':'agree'}
            # order wird rausgeschickt!
            self.order = self.k.query_private('AddOrder',api_params)

            try:
                self.order_id_buy = self.order['result']['txid'][0]
                #print(self.order_id_buy)
                #######################
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_buy)
                #######################
            except KeyError:
                isfilled=False
                print('Probably not enough funding...')

            if isfilled is True:
                # store the last buy price, to compare with sell price
                # noch checken
                closed = self.k.query_private('ClosedOrders')['result']['closed']
                self.lastbuy = float(closed[self.order_id_buy]['price'])

                # update the balance sheet with buy/sell price
                self.update_balance(self.lastbuy,self.order_id_buy)
            else:
                self.update_balance('-','-')

            # change the asset status ! redundant
            self.asset_check()

        self.set_broker_status(False)


    def sell_order(self):
        # executes a sell order for asset1

        self.set_broker_status(True)
        bid = str(self.asset_market_bid())
        current_asset1_funds = self.get_asset1_balance()
        self.asset_check()
        # diese if abfrage ist ein double check
        if self.asset_status is True:
            #######################
            # kraken query: what's our stock?
            volume = str(round((current_asset1_funds*0.9999),5))

            api_params = {'pair': self.pair,
                            'type':'sell',
                            'ordertype':'limit', #'market',
                            'price': bid,
                            'volume': volume,
                            'trading_agreement': 'agree'}
            # order wird rausgeschickt!
            self.order = self.k.query_private('AddOrder', api_params)

            try:
                self.order_id_sell = self.order['result']['txid'][0]
                # check
                #print(self.order_id_sell)
                #######################s
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_sell)
                #######################
            except KeyError:
                isfilled = False
                print('Probably not enough funding...')

            if isfilled is True:
                # update the balance sheet with transaction costs
                closed = self.k.query_private('ClosedOrders')['result']['closed']
                price = float(closed[self.order_id_sell]['price'])
                self.update_balance(price, self.order_id_sell)

                #######################
                # DAS SOLLTE IN EINE METHODE GEBAUT WERDEN
                # checkt ob niedriger verkauft wird als gekauft
                if self.lastbuy > price:
                    print('Bad Deal!\n SELL < BUY\n')
                elif self.lastbuy < price:
                    print('GREAT Deal!\n SELL > BUY\n')

                # twitters, if enabled: setTwitter(True)
                if self.twitter:
                    self.setTweet(self.lastbuy,price)
                #######################
            else:
                self.update_balance('-', '-')

            # change the asset status!
            self.asset_check()

        self.set_broker_status(False)


    def idle(self):
        self.set_broker_status(True)
        try:
            balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!\n')
        #
        # update the balance sheet
        self.update_balance('-','-')

        self.set_broker_status(False)

###################################
# Weitere member functions:

    def asset_balance(self):
        self.balance_all = self.k.query_private('Balance')
        balance_str = self.balance_all['result'][self.asset1]
        balance = float(balance_str)
        print(balance)

    def asset_market_bid(self):
        market_bid = self.k.query_public('Ticker', {'pair': self.pair})['result'][self.pair]['b']
        return round(float(market_bid[0]), 5)

    def asset_market_ask(self):
        market_ask = self.k.query_public('Ticker',{'pair': self.pair})['result'][self.pair]['a']
        return round(float(market_ask[0]), 5)

    def market_price(self):
        market = self.k.query_public('Ticker', {'pair': self.pair})['result'][self.pair]['c']
        return round(float(market[0]), 5)

    def get_asset2_balance(self):
        # unsere XBT
        asset2_funds = self.k.query_private('Balance')['result'][self.asset2]
        return round(float(asset2_funds), 5)

    def get_asset1_balance(self):
        # unsere ETH
        asset1_funds = self.k.query_private('Balance')['result'][self.asset1]
        return round(float(asset1_funds), 5)

    def update_balance(self, price, id):
        # update time
        time = self.getTime()
        new_asset1 = self.get_asset1_balance()
        new_asset2 = self.get_asset2_balance()
        market_price = self.market_price()

        balance_update_vec = [[time, new_asset1, new_asset2, price, market_price, id]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)
        print(balance_update_df)

        # schreibt die beiden .txt für den online upload
        self.writeTXT(new_asset1, new_asset2)


    def check_order(self,order_id):
        #IMPORTANT: checks if your order was filled after some time! If not -> cancel
        print('Checking the Order')
        count = 0
        cancel_flag = False
        open_orders = self.k.query_private('OpenOrders')['result']['open']

        # check if the order id appears in the OpenOrders list

        # BOOLEAN check
        while bool(order_id in open_orders) is True:
            print('Order is still open ... ')
            open_orders = self.k.query_private('OpenOrders')['result']['open']
            count += 1
            #cancel the order if not filled after 10 checks
            if count > 10:
                cancel_flag = True
                break
            # repeat check after 30 seconds
            time.sleep(30)

        if cancel_flag is True:
            # cancle the order
            self.k.query_private('CancelOrder', {'txid': order_id})
            print('Order was not filled and canceled!\n')
            isfilled=False
        else:
            print('Success: Order was filled!\n')
            isfilled=True

        return isfilled

    def our_balance(self):
        print(self.balance_df.tail())

    def writeTXT(self,asset1,asset2):
        # this is for further upload
        asset_balance_1 = round(asset1,3)
        asset_balance_2 = round(asset2,3)
        filename1 = self.asset1+'.txt'
        filename2 = self.asset2+'.txt'
        with open(filename1, "w") as text_file:
            text_file.write('%s' % asset_balance_1)
        with open(filename2, "w") as text_file:
            text_file.write('%s' % asset_balance_2)

    def setTwitter(self,on=False):
        try:
            if type(on) != bool:
                raise TypeError
        except TypeError:
            print('Either True or False!')
        self.twitter=on
        print('Twitter is enabled!\n')

    def getTwitter(self):
        return self.twitter

    def setTweet(self,old,current):
        # checks for old and current prices and sends twitter msgs
        # and sends good or bad tweets
        if old < current:
            self.twitterEngine.good_tweet()
        elif old >= current:
            self.twitterEngine.bad_tweet()



class Broker_HitBTC(Broker_base):
    '''
    IMPORTANT: HitBTC has different pairs than kraken!
    '''
    def __init__(self, myinput,url= 'https://api.hitbtc.com/api/2/public/ticker/'):
        super().__init__(myinput)
        self.url = url
        try:
            api_key = os.environ.get('HITBTC_API.key')
            api_secret = os.environ.get('HITBTC_SECRET.key')
            self.session = requests.session()
            self.session.auth = (api_key, api_secret)
        except:
            print('Provide the API Key and secret as:\n HITBTC_API.key and HITBTC_SECRET.key')

        self.balance_all = []
        self.balance_df = []
        self.lastbuy = 0
        self.order_id_sell = self.order_id_buy = []
        self.twitter = False
        try:
            self.twitterEngine = twitterEngine()
        except:
            print('No Twitter module enabled\n')

        #self.column_names = []

    def initialize(self):
        # initialisiert den Broker: stellt das dataFrame auf und holt die ersten Werte

        # check den asset_status von asset1 und stellt fest ob wir im Markt sind :
        self.asset_check()

        # checks if there aready exists a balance sheet as .csv
        if (os.path.exists(self.pair + '_balance.csv')):
            print(self.pair + '_balance.csv exists \n')
            old_df = pd.read_csv(self.pair + '_balance.csv')
            old_df = old_df.drop('Unnamed: 0', 1)
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = old_df
        else:
            # sets up a new, empty data frame for the balance
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns=self.column_names)
            self.balance_df['Time stamp'] = self.getTime()
            self.balance_df[self.asset2] = self.get_asset2_balance()
            self.balance_df[self.asset1] = self.get_asset1_balance()
            self.balance_df['Buy/Sell'] = '-'
            self.balance_df['Market Price'] = self.market_price()
            self.balance_df['Order Id'] = '-'

        print(self.balance_df.tail())

    def buy_order(self):
        # executes a buy order

        self.set_broker_status(True)
        self.asset_check()
        # check den XBT balance
        current_asset2_funds = self.get_asset2_balance()

        # diese if abfrage ist ein double check
        if self.asset_status is False:
            #######################
            # hitbtc querry query
            # wir können keine Verkaufsorder auf XBT-basis setzen, sondern nur ETH kaufen.
            # Deshalb: Limit order auf Basis des aktuellen Kurses und Berechnung des zu kaufenden ETH volumens.
            volume2 = current_asset2_funds
            ask = self.asset_market_ask()
            volume1 = round(((volume2 / ask) * 0.9999), 7)
            vol_str = str(round(volume1, 5))  # round -> kraken requirement
            ask_str = str(ask)

            # submit the order!
            orderData = {'symbol': self.pair, 'side': 'buy', 'quantity': vol_str, 'price': ask_str}
            self.order = self.session.post('https://api.hitbtc.com/api/2/order', data=orderData)
            self.order = self.order.json()

            try:
                self.order_id_buy = self.order['clientOrderId']
                # print(self.order_id_buy)
                #######################
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_buy)
                #######################
            except KeyError:
                isfilled = False
                print('Probably not enough funding...')

            if isfilled:
                time.sleep(10)
                # store the last buy price, to compare with sell price
                closed = self.session.get('https://api.hitbtc.com/api/2/history/trades').json()
                for c in closed:
                    if c['clientOrderId'] == self.order_id_buy:
                        price = c['price']
                    else:
                        price = 0
                    self.update_balance(price, self.order_id_buy)
                else:
                    print('error in isfilled buy')

                # update the balance sheet with buy/sell price
                self.update_balance(self.lastbuy, self.order_id_buy)
            else:
                self.update_balance('-', '-')

            # change the asset status ! redundant
            self.asset_check()

        self.set_broker_status(False)

    def sell_order(self):
        # executes a sell order
        self.set_broker_status(True)
        bid_str = str(self.asset_market_bid())
        current_asset1_funds = self.get_asset1_balance()
        self.asset_check()
        # diese if abfrage ist ein double check
        if self.asset_status is True:
            #######################
            # poloniex query: what's our stock?
            volume = str(round((current_asset1_funds * 0.9999), 7))

            # submits the order!
            orderData = {'symbol': self.pair, 'side': 'sell', 'quantity': volume, 'price': bid_str}
            self.order = self.session.post('https://api.hitbtc.com/api/2/order', data=orderData)
            self.order = self.order.json()

            try:
                self.order_id_sell = self.order['orderNumber']
                # check
                # print(self.order_id_sell)
                #######################
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_sell)
                #######################
            except KeyError:
                isfilled = False
                print('Probably not enough funding ...')

            if isfilled:
                time.sleep(10)
                # store the last buy price, to compare with sell price
                closed = self.session.get('https://api.hitbtc.com/api/2/history/trades').json()
                for c in closed:
                    if c['clientOrderId'] == self.order_id_sell:
                        price = c['price']
                    else:
                        price = 0
                    self.update_balance(price, self.order_id_sell)
                else:
                    print('error in isfilled sell')
                    price = 0

                #######################
                # DAS SOLLTE IN EINE METHODE GEBAUT WERDEN
                # checkt ob niedriger verkauft wird als gekauft
                if self.lastbuy > price:
                    print('Bad Deal!\n SELL < BUY\n')
                elif self.lastbuy < price:
                    print('GREAT Deal!\n SELL > BUY\n')

                # twitters, if enabled: setTwitter(True)
                if self.twitter:
                    self.setTweet(self.lastbuy, price)
                #######################
            else:
                self.update_balance('-', '-')

            # change the asset status!
            self.asset_check()

        self.set_broker_status(False)

    def idle(self):
        self.set_broker_status(True)
        try:
            __balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!\n')
        #
        # update the balance sheet
        self.update_balance('-', '-')

        self.set_broker_status(False)

    ###################################
    # Weitere member functions:

    def asset_balance(self):
        self.balance_all = self.k.query_private('Balance')
        balance_str = self.balance_all['result'][self.asset1]
        balance = float(balance_str)
        print(balance)

    def asset_market_bid(self):
        data = requests.get(self.url + self.pair).json()
        return round(float(data['bid']), 7)

    def asset_market_ask(self):
        data = requests.get(self.url + self.pair).json()
        return round(float(data['ask']), 7)

    def market_price(self):
        data = requests.get(self.url + self.pair).json()
        return round(float(data['last']), 7)

    def get_asset2_balance(self):
        # unsere XBT
        balance = self.session.get('https://api.hitbtc.com/api/2/account/balance').json()
        for b in balance:
            if b['currency'] == self.asset2:
                asset2_funds = b['available']
            else:
                asset2_funds = 0

        return round(float(asset2_funds), 7)

    def get_asset1_balance(self):
        # unsere ETH
        balance = self.session.get('https://api.hitbtc.com/api/2/account/balance').json()
        for b in balance:
            if b['currency'] == self.asset1:
                asset1_funds = b['available']
            else:
                asset1_funds = 0

        return round(float(asset1_funds), 7)

    def update_balance(self, price, id):
        # update time
        time = self.getTime()
        new_asset1 = self.get_asset1_balance()
        new_asset2 = self.get_asset2_balance()
        market_price = self.market_price()

        balance_update_vec = [[time, new_asset1, new_asset2, price, market_price, id]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)
        print(balance_update_df)

        # schreibt die beiden .txt für den online upload
        self.writeTXT(new_asset1, new_asset2)

    def check_order(self, order_id):
        # IMPORTANT: checks if your order was filled after some time! If not -> cancel
        print('Alto is checking the order')
        count = 0
        cancel_flag = False
        # returns all open orders for given currency pair
        open_orders = self.session.get('https://api.hitbtc.com/api/2/order').json()
        open_orders = [(e['orderNumber']) for e in open_orders]

        # check if the order id appears in the OpenOrders list
        # BOOLEAN check
        while bool(order_id in open_orders) is True:
            print('Order is still open ... ')
            open_orders = self.session.get('https://api.hitbtc.com/api/2/order').json()
            open_orders = [(e['orderNumber']) for e in open_orders]
            count += 1
            # cancel the order if not filled after 10 checks
            if count > 10:
                cancel_flag = True
                break
            # repeat check after 30 seconds
            time.sleep(30)

        if cancel_flag is True:
            # cancle the order
            try:
                cancel = self.session.delete('https://api.hitbtc.com/api/2/order/' + order_id).json()
                print('Order was not filled and canceled!\n')
                isfilled = False
            except:
                print('Somethings wrong with the orderCancel')
        else:
            print('Success: Order was filled!\n')
            isfilled = True

        return isfilled

    def our_balance(self):
        print(self.balance_df.tail())

    def asset_check(self):
        pass

    def writeTXT(self,asset1,asset2):
        # this is for further upload
        asset_balance_1 = round(asset1,3)
        asset_balance_2 = round(asset2,3)
        filename1 = self.asset1+'.txt'
        filename2 = self.asset2+'.txt'
        with open(filename1, "w") as text_file:
            text_file.write('%s' % asset_balance_1)
        with open(filename2, "w") as text_file:
            text_file.write('%s' % asset_balance_2)


##############################################

# remove the round
# check definition of ask and bid

class Broker_virtual_Poloniex(Broker_base):
    # this class is for dry run without conection to the exchange
    #
    def __init__(self, myinput, url='https://poloniex.com/public?command=returnTicker'):
        super().__init__(myinput)
        self.url = url

        self.balance_all = []
        self.fee = myinput.fee
        self.invest = myinput.investment
        self.pair = self.asset2+'_'+self.asset1
        print('Is the pair correct for Poloniex?')
        print(self.pair)

    def initialize(self):
        self.column_names = ['Time stamp', self.asset1, self.asset2, self.asset1+' shares',  'Altcoin price','Pair']
        self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns= self.column_names)
        self.balance_df['Time stamp'] = self.getTime()
        self.balance_df[self.asset2] = self.invest
        self.balance_df['Altcoin price'] = self.asset_market_bid()
        self.balance_df['Pair'] = self.pair

        print(self.balance_df)

    # different from base clase
    def writeCSV(self,df):
        # write data to csv
        filename = 'Coins_balance.csv'
        pd.DataFrame.to_csv(df,filename)

    def buy_order(self):
        self.broker_status = True

        if self.asset_status is False:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            current_eur_funds = balance_np[-1, 2] * 0.999999
            current_costs = current_eur_funds * self.fee

            asset_ask = self.asset_market_ask()

            new_shares = (current_eur_funds - current_costs) / asset_ask
            new_XETH = new_shares * asset_ask
            new_eur_fund = balance_np[-1, 2] - current_eur_funds

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares,  asset_ask, self.pair ]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(' ')
            print(balance_update_df)
            print(' ')

            self.lastbuy=asset_ask

            self.asset_status = True

        else:
            print('No money to buy coins')

        self.broker_status = False


    def sell_order(self):
        self.broker_status = True

        if self.asset_status is True:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            asset_bid = self.asset_market_bid()
            current_shares = balance_np[-1, 3] * 0.999999
            current_costs = current_shares * asset_bid * self.fee

            new_eur_fund = current_shares * asset_bid - current_costs

            new_shares = balance_np[-1, 3] - current_shares  # --> sollte gegen null gehen
            new_XETH = new_shares * asset_bid

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares, asset_bid, self.pair]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(balance_update_df)
            print(' ')

            self.lastsell = asset_bid
            self.asset_status = False

        else:
            print('Nothing to sell')

        self.broker_status = False


    def idle(self):
        self.broker_status = True
        try:
            balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!')
        #
        if self.asset_status is True:
            market_price = self.asset_market_ask()
        elif self.asset_status is False:
            market_price = self.asset_market_bid()
        #
        new_shares = balance_np[-1,3]
        new_assets = new_shares*market_price
        new_eur_fund = balance_np[-1,2]
        #
        # update time
        time = self.getTime()
        #
        # old is same as new
        balance_update_vec = [[time, new_assets, new_eur_fund, new_shares, market_price, self.pair]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)

        self.broker_status = False

    #def get_broker_status(self):
    #    return self.broker_status

    def asset_balance(self):
        #from abstract one
        print(self.balance_df.tail())

    def asset_market_bid(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['highestBid']), 7)

    def asset_market_ask(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['lowestAsk']), 7)

    def market_price(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['last']), 7)

    # new one for this kind of trader
    def setPair(self,pair):
        self.pair = pair

    def get_asset2_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def get_asset1_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def asset_check(self):
        # from abstract one
        print('Not implemented in virtual...')

    def check_order(self,id):
        # from abstract one
        print('Not implemented in virtual...')


############################################

class Broker_Poloniex(Broker_base):
    '''
    IMPORTANT: Poloniex has different pairs than kraken!
    '''

    def __init__(self, myinput,url= 'https://poloniex.com/public?command=returnTicker'):
        super().__init__(myinput)
        self.url = url
        try:
            api_key = os.environ.get('Poloniex_API.key')
            api_secret = os.environ.get('Poloniex_SECRET.key')
            self.session = requests.session()
            self.session.auth = (api_key, api_secret)
        except:
            print('Provide the API Keys and secret as:\n Poloniex_API.key and Poloniex_SECRET.key')

        self.balance_all = []
        self.balance_df = []
        self.lastbuy = 0
        self.order_id_sell = self.order_id_buy = []
        self.twitter = False
        try:
            self.twitterEngine = twitterEngine()
        except:
            print('No Twitter module enabled\n')

        #self.column_names = []

    def initialize(self):
        # initialisiert den Broker: stellt das dataFrame auf und holt die ersten Werte

        # check den asset_status von asset1 und stellt fest ob wir im Markt sind :
        self.asset_check()

        # checks if there aready exists a balance sheet as .csv
        if (os.path.exists(self.pair + '_balance.csv')):
            print(self.pair + '_balance.csv exists \n')
            old_df = pd.read_csv(self.pair + '_balance.csv')
            old_df = old_df.drop('Unnamed: 0', 1)
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = old_df
        else:
            # sets up a new, empty data frame for the balance
            self.column_names = ['Time stamp', self.asset1, self.asset2, 'Buy/Sell', 'Market Price', 'Order Id']
            self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns=self.column_names)
            self.balance_df['Time stamp'] = self.getTime()
            self.balance_df[self.asset2] = self.get_asset2_balance()
            self.balance_df[self.asset1] = self.get_asset1_balance()
            self.balance_df['Buy/Sell'] = '-'
            self.balance_df['Market Price'] = self.market_price()
            self.balance_df['Order Id'] = '-'

        print(self.balance_df.tail())

    def buy_order(self):
        # executes a buy order

        self.set_broker_status(True)
        self.asset_check()
        # check den XBT balance
        current_asset2_funds = self.get_asset2_balance()

        # diese if abfrage ist ein double check
        if self.asset_status is False:
            #######################
            # hitbtc querry query
            # wir können keine Verkaufsorder auf XBT-basis setzen, sondern nur ETH kaufen.
            # Deshalb: Limit order auf Basis des aktuellen Kurses und Berechnung des zu kaufenden ETH volumens.
            volume2 = current_asset2_funds
            ask = self.asset_market_ask()
            volume1 = round(((volume2 / ask) * 0.9999), 7)
            vol_str = str(round(volume1, 5))  # round -> kraken requirement
            ask_str = str(ask)

            # submit the order!
            orderData = {'symbol': self.pair, 'side': 'buy', 'quantity': vol_str, 'price': ask_str}
            self.order = self.session.post('https://api.hitbtc.com/api/2/order', data=orderData)
            self.order = self.order.json()

            try:
                self.order_id_buy = self.order['clientOrderId']
                # print(self.order_id_buy)
                #######################
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_buy)
                #######################
            except KeyError:
                isfilled = False
                print('Probably not enough funding...')

            if isfilled:
                time.sleep(10)
                # store the last buy price, to compare with sell price
                closed = self.session.get('https://api.hitbtc.com/api/2/history/trades').json()
                for c in closed:
                    if c['clientOrderId'] == self.order_id_buy:
                        price = c['price']
                    else:
                        price = 0
                    self.update_balance(price, self.order_id_buy)
                else:
                    print('error in isfilled buy')

                # update the balance sheet with buy/sell price
                self.update_balance(self.lastbuy, self.order_id_buy)
            else:
                self.update_balance('-', '-')

            # change the asset status ! redundant
            self.asset_check()

        self.set_broker_status(False)

    def sell_order(self):
        # executes a sell order
        self.set_broker_status(True)
        bid_str = str(self.asset_market_bid())
        current_asset1_funds = self.get_asset1_balance()
        self.asset_check()
        # diese if abfrage ist ein double check
        if self.asset_status is True:
            #######################
            # poloniex query: what's our stock?
            volume = str(round((current_asset1_funds * 0.9999), 7))

            # submits the order!
            orderData = {'symbol': self.pair, 'side': 'sell', 'quantity': volume, 'price': bid_str}
            self.order = self.session.post('https://api.hitbtc.com/api/2/order', data=orderData)
            self.order = self.order.json()

            try:
                self.order_id_sell = self.order['orderNumber']
                # check
                # print(self.order_id_sell)
                #######################
                # IMPORTANT: check if order is still open!
                isfilled = self.check_order(self.order_id_sell)
                #######################
            except KeyError:
                isfilled = False
                print('Probably not enough funding ...')

            if isfilled:
                time.sleep(10)
                # store the last buy price, to compare with sell price
                closed = self.session.get('https://api.hitbtc.com/api/2/history/trades').json()
                for c in closed:
                    if c['clientOrderId'] == self.order_id_sell:
                        price = c['price']
                    else:
                        price = 0
                    self.update_balance(price, self.order_id_sell)
                else:
                    print('error in isfilled sell')
                    price = 0

                #######################
                # DAS SOLLTE IN EINE METHODE GEBAUT WERDEN
                # checkt ob niedriger verkauft wird als gekauft
                if self.lastbuy > price:
                    print('Bad Deal!\n SELL < BUY\n')
                elif self.lastbuy < price:
                    print('GREAT Deal!\n SELL > BUY\n')

                # twitters, if enabled: setTwitter(True)
                if self.twitter:
                    self.setTweet(self.lastbuy, price)
                #######################
            else:
                self.update_balance('-', '-')

            # change the asset status!
            self.asset_check()

        self.set_broker_status(False)

    def idle(self):
        self.set_broker_status(True)
        try:
            __balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!\n')
        #
        # update the balance sheet
        self.update_balance('-', '-')

        self.set_broker_status(False)

    ###################################
    # Weitere member functions:

    def asset_balance(self):
        self.balance_all = self.k.query_private('Balance')
        balance_str = self.balance_all['result'][self.asset1]
        balance = float(balance_str)
        print(balance)

    def asset_market_bid(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['highestBid']), 7)

    def asset_market_ask(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['lowestAsk']), 7)

    def market_price(self):
        data = requests.get(self.url).json()
        return round(float(data[self.pair]['last']), 7)

    def get_asset2_balance(self):
        # unsere XBT
        balance = self.session.get('https://api.hitbtc.com/api/2/account/balance').json()
        for b in balance:
            if b['currency'] == self.asset2:
                asset2_funds = b['available']
            else:
                asset2_funds = 0

        return round(float(asset2_funds), 7)

    def get_asset1_balance(self):
        # unsere ETH
        balance = self.session.get('https://api.hitbtc.com/api/2/account/balance').json()
        for b in balance:
            if b['currency'] == self.asset1:
                asset1_funds = b['available']
            else:
                asset1_funds = 0

        return round(float(asset1_funds), 7)

    def update_balance(self, price, id):
        # update time
        time = self.getTime()
        new_asset1 = self.get_asset1_balance()
        new_asset2 = self.get_asset2_balance()
        market_price = self.market_price()

        balance_update_vec = [[time, new_asset1, new_asset2, price, market_price, id]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)
        print(balance_update_df)

        # schreibt die beiden .txt für den online upload
        self.writeTXT(new_asset1, new_asset2)

    def check_order(self, order_id):
        # IMPORTANT: checks if your order was filled after some time! If not -> cancel
        print('Alto is checking the order')
        count = 0
        cancel_flag = False
        # returns all open orders for given currency pair
        open_orders = self.session.get('https://api.hitbtc.com/api/2/order').json()
        open_orders = [(e['orderNumber']) for e in open_orders]

        # check if the order id appears in the OpenOrders list
        # BOOLEAN check
        while bool(order_id in open_orders) is True:
            print('Order is still open ... ')
            open_orders = self.session.get('https://api.hitbtc.com/api/2/order').json()
            open_orders = [(e['orderNumber']) for e in open_orders]
            count += 1
            # cancel the order if not filled after 10 checks
            if count > 10:
                cancel_flag = True
                break
            # repeat check after 30 seconds
            time.sleep(30)

        if cancel_flag is True:
            # cancle the order
            try:
                cancel = self.session.delete('https://api.hitbtc.com/api/2/order/' + order_id).json()
                print('Order was not filled and canceled!\n')
                isfilled = False
            except:
                print('Somethings wrong with the orderCancel')
        else:
            print('Success: Order was filled!\n')
            isfilled = True

        return isfilled

    def our_balance(self):
        print(self.balance_df.tail())

    def writeTXT(self,asset1,asset2):
        # this is for further upload
        asset_balance_1 = round(asset1,3)
        asset_balance_2 = round(asset2,3)
        filename1 = self.asset1+'.txt'
        filename2 = self.asset2+'.txt'
        with open(filename1, "w") as text_file:
            text_file.write('%s' % asset_balance_1)
        with open(filename2, "w") as text_file:
            text_file.write('%s' % asset_balance_2)


###########################################################
class Broker_virtual_Bittrex(Broker_base):
    # this class is for dry run without conection to the exchange
    #
    def __init__(self, myinput, url='https://bittrex.com/api/v1.1/public/getmarketsummaries'):
        super().__init__(myinput)
        self.url = url

        self.balance_all = []
        self.fee = myinput.fee
        self.invest = myinput.investment
        self.pair = self.asset2+'-'+self.asset1
        print('This is the virtual broker for bittrex.')
        print('Pairs are written as: ',self.pair)
        print(' ')

    def initialize(self):
        # checks if there aready exists a balance sheet as .csv
        if (os.path.exists('Coins_balance.csv')):
            print('Coins_balance.csv exists \n')
            old_df = pd.read_csv('Coins_balance.csv')
            old_df = old_df.drop('Unnamed: 0',1)
            self.column_names = ['Time stamp', self.asset1, self.asset2, self.asset1 + ' shares', 'Altcoin price',
                                 'Pair']
            self.balance_df = old_df
        else:
            #sets up a new, empty data frame for the balance
            self.column_names = ['Time stamp', self.asset1, self.asset2, self.asset1 + ' shares', 'Altcoin price',
                                 'Pair']
            self.balance_df = pd.DataFrame([np.zeros(len(self.column_names))], columns=self.column_names)
            self.balance_df['Time stamp'] = self.getTime()
            self.balance_df[self.asset2] = self.invest
            self.balance_df['Altcoin price'] = self.asset_market_bid()
            self.balance_df['Pair'] = self.pair
        print(self.balance_df)

    # different from base clase
    def writeCSV(self,df):
        # write data to csv
        filename = 'Coins_balance.csv'
        pd.DataFrame.to_csv(df,filename)

    def buy_order(self):
        self.broker_status = True

        if self.asset_status is False:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            current_eur_funds = balance_np[-1, 2] * 0.999999
            current_costs = current_eur_funds * self.fee

            asset_ask = self.asset_market_ask()

            new_shares = (current_eur_funds - current_costs) / asset_ask
            new_XETH = new_shares * asset_ask
            new_eur_fund = balance_np[-1, 2] - current_eur_funds

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares,  asset_ask, self.pair ]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(' ')
            print(balance_update_df)
            print(' ')

            self.lastbuy=asset_ask

            self.asset_status = True

        else:
            print('No money to buy coins')

        self.broker_status = False


    def sell_order(self):
        self.broker_status = True

        if self.asset_status is True:
            # this only for virtual
            try:
                balance_np = np.array(self.balance_df.tail())
            except AttributeError:
                print('Broker muss noch initialisiert werden!')

            asset_bid = self.asset_market_bid()
            current_shares = balance_np[-1, 3] * 0.999999
            current_costs = current_shares * asset_bid * self.fee

            new_eur_fund = current_shares * asset_bid - current_costs

            new_shares = balance_np[-1, 3] - current_shares  # --> sollte gegen null gehen
            new_XETH = new_shares * asset_bid

            # update time
            time = self.getTime()

            balance_update_vec = [[time, new_XETH, new_eur_fund, new_shares, asset_bid, self.pair]]
            balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
            self.balance_df = self.balance_df.append(balance_update_df)

            # write as csv file
            self.writeCSV(self.balance_df)
            print(balance_update_df)
            print(' ')

            self.lastsell = asset_bid
            self.asset_status = False

        else:
            print('Nothing to sell')

        self.broker_status = False


    def idle(self):
        self.broker_status = True
        try:
            balance_np = np.array(self.balance_df.tail())
        except AttributeError:
            print('Broker muss noch initialisiert werden!')
        #
        if self.asset_status is True:
            market_price = self.asset_market_ask()
        elif self.asset_status is False:
            market_price = self.asset_market_bid()
        #
        new_shares = balance_np[-1,3]
        new_assets = new_shares*market_price
        new_eur_fund = balance_np[-1,2]
        #
        # update time
        time = self.getTime()
        #
        # old is same as new
        balance_update_vec = [[time, new_assets, new_eur_fund, new_shares, market_price, self.pair]]
        balance_update_df = pd.DataFrame(balance_update_vec, columns=self.column_names)
        self.balance_df = self.balance_df.append(balance_update_df)

        # write as csv file
        self.writeCSV(self.balance_df)

        self.broker_status = False

    #def get_broker_status(self):
    #    return self.broker_status

    def asset_balance(self):
        #from abstract one
        print(self.balance_df.tail())

    def asset_market_bid(self):
        data_all = requests.get(self.url).json()
        for i in range(len(data_all['result'])):
            if data_all['result'][i]['MarketName'] == self.pair:
                thisData = data_all['result'][i]
                break
        return round(float(thisData['Bid']), 9)

    def asset_market_ask(self):
        data_all = requests.get(self.url).json()
        for i in range(len(data_all['result'])):
            if data_all['result'][i]['MarketName'] == self.pair:
                thisData = data_all['result'][i]
                break
        return round(float(thisData['Ask']), 9)

    def market_price(self):
        data_all = requests.get(self.url).json()
        for i in range(len(data_all['result'])):
            if data_all['result'][i]['MarketName'] == self.pair:
                thisData = data_all['result'][i]
                break
        return round(float(thisData['Last']), 9)

    # new one for this kind of trader
    def setPair(self,pair):
        self.pair = pair

    def get_asset2_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def get_asset1_balance(self):
        # from abstract one
        print('Not implemented in virtual...')

    def asset_check(self):
        # from abstract one
        print('Not implemented in virtual...')

    def check_order(self,id):
        # from abstract one
        print('Not implemented in virtual...')