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

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

ADVISE, LOCATION = range(2)


def start(bot, update):
    update.message.reply_text('Дратути! Как твое самочувствие?')
    return ADVISE


def advise(bot, update):
    user = update.message.from_user
    logger.info("Question recieved from %s: %s" % (user.first_name, update.message.text))
    # load the model from disk
    filename = 'finalized_model.sav'
    loaded_model = pickle.load(open(filename, 'rb'))
    result = loaded_model.predict([update.message.text])
    logger.info("Advised - %s " % result[0])
    update.message.reply_text('Тебе нужен %s ! Пришли мне свое местоположение, и я найду тебе врача!' % result[0])


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

    gmaps = googlemaps.Client(key='AIzaSyB8iePIC8qHoF24pa-EM6Djm4EgaJRrRT0')

    API_KEY = 'AIzaSyB8iePIC8qHoF24pa-EM6Djm4EgaJRrRT0'
    google_places = GooglePlaces(API_KEY)
    query_result = google_places.nearby_search(
        location="London", keyword='Fish and Chips',
        radius=2000, types=[types.TYPE_FOOD])

    #results = gmaps.reverse_geocode((user_location.latitude, user_location.longitude),
    #                                      keyword='Fish and Chips',
    #                                      location_type='ROOFTOP',
    #                                      result_type='street_address')

    #lat, lng = google_places.address_to_latlng(query_result)
    logger.info(results)

    bot.sendLocation(update.message.chat.id, latitude=user_location.latitude, longitude=user_location.longitude)
    return ConversationHandler.END


def cancel(bot, update):
    user = update.message.from_user
    logger.info("Будьте здоровы!")
    update.message.reply_text('Дотвидания')
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
