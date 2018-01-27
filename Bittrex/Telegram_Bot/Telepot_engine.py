import telepot
import time
from telepot.loop import MessageLoop
from TOKEN.key import API_TOKEN

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
            pass
        return user_list

    def write_users(self,user_list):
        with open("Telegram_Bot/users_bot.txt", 'w') as users_file:
            users_file.write("\n".join([str(uid) for uid in user_list]))


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
