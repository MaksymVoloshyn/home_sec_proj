import telebot
import requests
import time
from bs4 import BeautifulSoup
from multiprocessing import Process

bot = telebot.TeleBot('\\token')
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard1.row('Мониторинг вкл.', 'Мониторинг выкл.')
keyboard1.row('Состояние дома', 'Температура\Влажность', 'Расстояние')
keyboard1.row('Запомнить положение')

saved_dis = '0'
monitoring = 1

def main_messages():

    global saved_dis

    @bot.message_handler(commands=['mvgeek'])
    def start_message(message):
        bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard1)

    @bot.message_handler(content_types=['text'])
    def send_text(message):
        global saved_dis
        global monitoring
        try:
            data = requests.get('http://176.36.243.54/')
            soup_text = BeautifulSoup(data.text, "html.parser")
            temp = (soup_text.find('a', {'class': 'temp'})).text
            hum = (soup_text.find('a', {'class': 'hum'})).text
            dis = (soup_text.find('a', {'class': 'dis'})).text
            tw = (soup_text.find('a', {'class': 'tw'})).text
            temp_hum = 'Температура в доме: ' + temp[1:] + ' гр.' + '\n' + 'Влажность: ' + hum[1:] + ' %'
            dis_bt = 'Расстояние до обьекта: ' + dis + 'см'
            tw_bt = 'Время работы Arduino: ' + tw
        except Exception:
            bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        def alert_st():
            if int(dis) <= int(saved_dis) - 2:
                alert = 'открыта'
            elif saved_dis == '0':
                alert = 'Не определено'
            else:
                alert = 'закрыта'
            return alert

        def monitoring_check():
            if monitoring == 1 :
                return 'Мониторинг двери: включен'
            else:
                return 'Мониторинг двери: выключен'

        if message.text.lower() == 'температура\влажность':
            try:
                bot.send_message(message.chat.id, temp_hum)
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        elif message.text.lower() == 'запомнить положение':
            try:
                saved_dis = dis
                bot.send_message(message.chat.id, 'Положение было сохранено!')
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        elif message.text.lower() == 'мониторинг вкл.':
            try:
                monitoring = 1
                bot.send_message(message.chat.id, 'Мониторинг был включен!')
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        elif message.text.lower() == 'мониторинг выкл.':
            try:
                monitoring = 0
                bot.send_message(message.chat.id, 'Хорошо, отключаем мониторинг...')
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        elif message.text.lower() == 'расстояние':
            try:
                bot.send_message(message.chat.id, dis_bt + '\n' + 'Сохранённая дистанция: ' + saved_dis + ' см')
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

        elif message.text.lower() == 'состояние дома':
            try:
                bot.send_message(message.chat.id, temp_hum + '\n' + 'Положение двери: ' + alert_st() + '\n'
                                 + monitoring_check() + '\n' + tw_bt)
            except Exception:
                bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

    @bot.message_handler(content_types=['sticker'])
    def sticker_id(message):
        print(message)

    while True:
        try:
            bot.polling()
        except Exception:
            print('Oooops')
            time.sleep(15)

def door_check():
    while True:
        try:
            data = requests.get('http://176.36.243.54/')
            soup_text = BeautifulSoup(data.text, "html.parser")
            dis = (soup_text.find('a', {'class': 'dis'})).text
            #print(int(dis))
            #print(saved_dis)
            if int(dis) <= int(saved_dis) - 2:
                bot.send_message(333009899, 'Дверь была открыта!')
        except Exception:
            bot.send_message(333009899, 'Ooops, something wrong -_-')
        time.sleep(2)

if __name__ == '__main__':
    p1 = Process(target=main_messages)
    p2 = Process(target=door_check)
    p1.start()
    p2.start()
    p1.join()
    p2.join()
