import telepot
import time
from Telegram_Bot.TOKEN_key import API_TOKEN
from pyemojify import emojify

class Telepot_engine(object):
    def __init__(self):
        self.bot = telepot.Bot(API_TOKEN)
        self.users = []

    def get_users(self):
        user_list = []
        try:
            with open("Telegram_Bot/users_bot.txt", 'r') as users_file:
                for line in users_file.readlines():
                    user_list.append(int(line))
        except FileNotFoundError:
            print('User ID File not found!')
        return user_list


    def sendMsg(self, coin='', investment='', price='',kind = 'BUY'):
        self.bot = telepot.Bot(API_TOKEN)
        self.users = self.get_users()
        try:
            if kind == 'BUY':
                message = emojify(':sparkles: I bought ' + coin[4:] + ' for ' + price + ' :zap:. \nYour investment was: ' + investment)
            elif kind == 'SELL':
                message = emojify(':boom: Success! :rocket: \n' +
                                  'I sold ' + coin[4:] + ' for ' + price + '. \nYour investment increased: ' + investment + ' :money_bag:')
            elif kind == 'EXIT':
                message = emojify(':ghost: So sad! :cry: \n' +
                                  'I sold ' + coin[4:] + ' for ' + price + '. :skull: \nYour investment decreased: ' + investment + ' :money_with_wings:')
            else:
                message = emojify(':iphone: Nothing to tell ...')

<<<<<<< HEAD
            for user in self.users:
                try:
                    self.bot.sendMessage(user, message)
                except telepot.exception.BotWasBlockedError:
                    self.users.remove(user)
        except:
            pass
=======
        if kind =='BUY':
            message = emojify(':sparkles: I bought '+coin[4:]+' for '+price+' :zap:. \nYour investment was: '+investment )
        elif kind =='SELL':
            message =  emojify(':boom: Success! :rocket: \n'+ \
                       'I sold '+coin[4:]+' for '+price+'. \nYour investment increased: '+investment+' :moneybag:')
        elif kind == 'EXIT':
            message =  emojify(':ghost: So sad! :cry: \n'+ \
                       'I sold '+coin[4:]+' for '+price+'. :skull: \nYour investment decreased: '+investment +' :money_with_wings:')
        else:
            message = emojify(':iphone: Nothing to tell ...')

        for user in self.users:
            try:
                self.bot.sendMessage(user, message)
            except telepot.exception.BotWasBlockedError:
                self.users.remove(user)
>>>>>>> 573eccc6f1e93e36d7071eed55038e9f56447ad9

    def individualMsg(self, message):
        self.bot = telepot.Bot(API_TOKEN)
        self.users = self.get_users()

        for user in self.users:
            try:
                self.bot.sendMessage(user, message)
            except telepot.exception.BotWasBlockedError:
                self.users.remove(user)


    def alive(self):
        self.bot = telepot.Bot(API_TOKEN)
        self.users = self.get_users()
        for user in self.users:
            try:
                self.bot.sendMessage(user,emojify(':rocket: To the moon with MillionVanillion Trading! :snowman:'))
                self.bot.sendPhoto(user,'http://assets.nydailynews.com/polopoly_fs/1.2930801.1483288897!/'+
                                        'img/httpImage/image.jpg_gen/derivatives/article_750/germany-obit-milli-vanilli.jpg')
            except telepot.exception.BotWasBlockedError:
                self.users.remove(user)


    #def write_users(self,user_list):
    #    with open("Telegram_Bot/users_bot.txt", 'w') as users_file:
    #        users_file.write("\n".join([str(uid) for uid in user_list]))
