import Model
import telebot
from telebot import types

# from PIL import Image
# import io
# from io import BytesIO

token = '5185987014:AAFz0Ak25o780eUEHRj75dWhL1TPL13-2to'

bot = telebot.TeleBot(token)  # создаем экземпляр класса TeleBot

img_num = 0
trans_status = 0
content_img = 0
style_img = 0

Initial_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
Cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
Go_cancel_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
Info_status_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

info_btn = types.KeyboardButton(text="/about_me")
begin_btn = types.KeyboardButton(text='/begin')
cancel_btn = types.KeyboardButton(text='/cancel')
go_btn = types.KeyboardButton(text='/go')
status_btn = types.KeyboardButton(text='/status')

Initial_keyboard.add(begin_btn, info_btn)
Cancel_keyboard.add(cancel_btn)
Go_cancel_keyboard.add(go_btn, cancel_btn)
Info_status_keyboard.add(info_btn, status_btn)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, f"Привет, {message.from_user.first_name}, я бот для переноса стиля."
                                      f"\nНажми *about_me* если хочешь узнать обо мне и о том, что я умею,"
                                      f"\nили *begin*, если хочешь приступить к переносу стиля.",
                                      reply_markup=Initial_keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['about_me'])
def about_me(message):
    bot.send_message(message.chat.id, "Я просто бот")


@bot.message_handler(commands=['begin'])
def begin(message):
    bot.send_message(message.chat.id, "Отправь мне изображение, которое ты хочешь стилизовать,"
                                      "\nили нажми *cancel*, если хочешь прервать загрузку",
                                      reply_markup=Cancel_keyboard, parse_mode='Markdown')


@bot.message_handler(commands=['cancel'])
def cancel(message):
    global img_num
    global trans_status
    if trans_status == 1:
        bot.send_message(message.chat.id, "Трансфер в процессе, пожалуйста, дождись окончания", reply_markup=Initial_keyboard)
    else:
        img_num = 0
        bot.send_message(message.chat.id, "Процедура остановлена", reply_markup=Initial_keyboard)


@bot.message_handler(commands=['status'])
def status(message):
    global trans_status
    if trans_status == 0:
        bot.send_message(message.chat.id, "Трансфер не запущен", reply_markup=Info_status_keyboard)
    else:
        bot.send_message(message.chat.id, "Трансфер в процессе", reply_markup=Info_status_keyboard)


@bot.message_handler(content_types=['photo'])
def photo_processing(message):
    # print('message.photo =', message.photo)
    fileID = message.photo[-1].file_id
    # print('fileID =', fileID)
    file_info = bot.get_file(fileID)
    # print('file.file_path =', file_info.file_path)
    # print('\n\n')
    downloaded_file = bot.download_file(file_info.file_path)
    global img_num
    global trans_status

    if img_num == 0:
        global content_img
        content_img = Model.image_loader(downloaded_file)
        bot.send_message(message.chat.id, 'Изображение для наложения стиля принято.'
                                          '\nТеперь отправь образец стиля'
                                          '\nили нажми *cancel*, если хочешь прервать загрузку.',
                                           reply_markup=Cancel_keyboard, parse_mode='Markdown')
        img_num = 1

    elif img_num == 1:
        global style_img
        style_img = Model.image_loader(downloaded_file)
        bot.send_message(message.chat.id, 'Образец стиля принят.'
                                          '\nНажми *go*, чтобы начать обработку'
                                          '\nили нажми *cancel*, если хочешь прервать загрузку.',
                                            reply_markup=Go_cancel_keyboard, parse_mode='Markdown')
        img_num = 2

    elif img_num == 2 and trans_status == 0:
        bot.send_message(message.chat.id, 'У меня уже есть оба изображения!'
                                          '\nНажми *go*, чтобы начать обработку,'
                                          '\nили нажми *cancel*, если хочешь прервать загрузку.',
                                            reply_markup=Go_cancel_keyboard, parse_mode='Markdown')

    elif img_num == 2 and trans_status == 1:
        bot.send_message(message.chat.id, 'Я не могу принимать новые изображения, пока трансфер в процессе, пожалуйста, дождись окончания',
                                           reply_markup=Info_status_keyboard, parse_mode='Markdown')
    else:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')

@bot.message_handler(commands=['go'])
def send_photo(message):
    global img_num
    global trans_status
    if img_num == 0:
        bot.send_message(message.chat.id, 'Похоже, ты еще не выслал мне ни одного изображения')
    elif img_num == 1:
        bot.send_message(message.chat.id, 'У меня еще нет образца стиля!')
    elif img_num == 2 and trans_status == 1:
        bot.send_message(message.chat.id, 'Трансфер в процессе, пожалуйста, дождись окончания')
        trans_status = 1
    elif img_num == 2:
        bot.send_message(message.chat.id, 'Трансфер запущен'
                                          '\nПроцесс может занять какое-то время, пожалуйста, дождись окончания.',
                                            reply_markup=Info_status_keyboard, parse_mode='Markdown')
        trans_status = 1
        # bot.send_chat_action(message.chat.id, 'upload_photo')
        output = Model.transfer(content_img, style_img)
        bot.send_photo(message.chat.id, output, reply_to_message_id=message.message_id)
        img_num = 0
        trans_status = 0
    else:
        bot.send_message(message.chat.id, 'Непредвиденная ошибка')


bot.infinity_polling()
