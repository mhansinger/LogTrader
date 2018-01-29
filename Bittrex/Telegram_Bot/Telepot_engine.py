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

        if kind =='BUY':
            message = emojify(':sparkles: I bought '+coin[4:]+' for '+price+'. \nYour investment was: '+investment + ':boom:')
        elif kind =='SELL':
            message =  emojify(':boom: Success! :rocket: \n'+ \
                       'I sold '+coin[4:]+' for '+price+'. \nYour investment increased: '+investment+' :money_bag:')
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
                self.bot.sendMessage(user,'I am alive now and ready to trade!')
            except telepot.exception.BotWasBlockedError:
                self.users.remove(user)


    #def write_users(self,user_list):
    #    with open("Telegram_Bot/users_bot.txt", 'w') as users_file:
    #        users_file.write("\n".join([str(uid) for uid in user_list]))

    '''
    def send_message(self,msg):
        try:
            content_type, chat_type, chat_id = telepot.glance(msg)
            if content_type == 'text':
                user_id = msg['chat']['id']
                if msg['text'] in ["/start", "/start start", "Hallo", "Hi", "Start"]:
                    if user_id not in users:
                        users.append(user_id)
                        write_users(users)
                    bot.sendMessage(user_id, "Welcome ")
                elif msg['text'] in ["/stop", "Hör auf", "Stop", "Ende"]:
                    users.remove(user_id)
                    write_users(users)
                    bot.sendMessage(user_id, "Ich frage dich ab jetzt nicht mehr.")
                elif msg['text'].startswith("/"):
                    bot.sendMessage(user_id, "Mit dem Befehl `" + msg['text'] + "` kann ich leider nichts anfangen.")
                    bot.sendMessage(user_id,
                                    "Ich verstehe nur /start und /stop. Bei allen anderen Nachrichten gehe ich " +
                                    "davon aus, dass es ein Gefühl ist.")
                else:  # It must be a mood
                    with open("mood_data.csv", 'a') as data_file:
                        data_file.write(
                            "\n" + ", ".join([str(user_id), str(msg['date']), "".join(msg['text'].split(','))]))
                    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text='mies', callback_data='-2'),
                         InlineKeyboardButton(text='schlecht', callback_data='-1'),
                         InlineKeyboardButton(text='neutral', callback_data='0'),
                         InlineKeyboardButton(text='gut', callback_data='1'),
                         InlineKeyboardButton(text='super', callback_data='2')],
                    ])
                    bot.sendMessage(chat_id, 'Wie gut fühlt sich das an?', reply_markup=keyboard)
        except telepot.exception.BotWasBlockedError:
            pass
    '''