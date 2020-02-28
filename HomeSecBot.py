import telebot
from bs4 import BeautifulSoup
import requests

bot = telebot.TeleBot('813041480:AAFi1MVGgrZWT-F6ELujp4aUFojfALwFPKw')
keyboard1 = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
keyboard1.row('Мониторинг вкл.', 'Мониторинг выкл.')
keyboard1.row('Состояние дома', 'Температура\Влажность', 'Расстояние')
keyboard1.row('Запомнить положение')

saved_dis = '0'

@bot.message_handler(commands=['mvgeek'])
def start_message(message):
    bot.send_message(message.chat.id, 'Привет!', reply_markup=keyboard1)

@bot.message_handler(content_types=['text'])
def send_text(message):
    global saved_dis
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

    def alert_st ():
        if int(dis) <= int(saved_dis)-2:
            alert = 'открыта'
        elif saved_dis == '0':
            alert = 'Не определено'
        else:
            alert = 'закрыта'
        return alert

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

    elif message.text.lower() == 'расстояние':
        try:
            bot.send_message(message.chat.id, dis_bt + '\n' + 'Сохранённая дистанция: ' + saved_dis + ' см')
        except Exception:
            bot.send_message(message.chat.id, 'Ooops, something wrong -_-')
            
    elif message.text.lower() == 'состояние дома':
        try:
            bot.send_message(message.chat.id, temp_hum  + '\n' + 'Положение двери: ' + alert_st() + '\n' +  tw_bt)
        except Exception:
            bot.send_message(message.chat.id, 'Ooops, something wrong -_-')

@bot.message_handler(content_types=['sticker'])
def sticker_id(message):
    print(message)

try:
    bot.polling()
except Exception:
    print('Oooops')