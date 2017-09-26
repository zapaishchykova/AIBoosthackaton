#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)

import logging
from googleplaces import GooglePlaces, types, lang
import googlemaps
import pickle
import requests
import json
import numpy as np
import random

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ADVISE, LOCATION = range(2)
filename = 'finalized_model_log_reg.pkl'
loaded_model = pickle.load(open(filename, 'rb'))


def start(bot, update):
    greeting = ['Дратути! Как твое самочувствие?', 'Здравствуйте! На что жалутесь?', 'Привет! У тебя что-то болит?', 'Доброго времени суток, уважаемый. Опишите мне вашу проблему']
    update.message.reply_text(random.choice(greeting))   
    return ADVISE


def advise(bot, update):
    user = update.message.from_user
    logger.info("Question recieved from %s: %s" % (user.first_name, update.message.text))
    # load the model from disk
    global doctor
    doctor = loaded_model.predict([update.message.text])
    prob = np.max(loaded_model.predict_proba([update.message.text]))

    if (prob < 0.1) | (len(update.message.text) < 10):
        update.message.reply_text('Хмм, опиши более детально симптомы.')
        logger.info("Failed to get correct prediction %f", prob)
        return ADVISE
    else :    
        logger.info("Advised - %s, prob %f" % (doctor[0], prob))
        update.message.reply_text('Тебе нужен %s ! Пришли мне свое местоположение, и я найду тебе врача! Для отмены отправь //cancel ' % doctor[0])
        return LOCATION

def skip_location(bot, update):
    user = update.message.from_user
    logger.info("User %s did not send a location." % user.first_name)
    update.message.reply_text('Ну и лан')
    return BIO


def location(bot, update):
    user = update.message.from_user
    user_location = update.message.location
    logger.info("Местоположение %s: %f / %f"
                % (user.first_name, user_location.latitude, user_location.longitude))
    update.message.reply_text('Получай адресок:')

    API_KEY = 'AIzaSyB8iePIC8qHoF24pa-EM6Djm4EgaJRrRT0'
    params = {
        'key': API_KEY ,
        'location': '%f,%f' % (user_location.latitude, user_location.longitude),
        'radius': 5000,
        'keyword':  '%s' % doctor[0]}

    response = requests.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params)
    points = response.json()

    bot.sendLocation(update.message.chat.id, latitude=points['results'][0]['geometry']['location']['lat'], longitude=points['results'][0]['geometry']['location']['lng'])
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    replies = ['Будьте здоровы! Дотвидания','Не болей!','Выздоравливай!']
    update.message.reply_text(random.choice(replies))
    update.message.reply_text('Что бы повторно пройти консультацию используй команду //start')
    return ConversationHandler.END


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():
    # Create the EventHandler and pass it your bot's token.
    updater = Updater('441740281:AAERMz_K5NYzHNpfcGrn_wImVDvVlaGnErI')

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            ADVISE: [MessageHandler(Filters.text, advise)],

            LOCATION: [MessageHandler(Filters.location, location),
                       CommandHandler('skip', skip_location)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
