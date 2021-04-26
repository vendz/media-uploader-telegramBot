import logging
import os
import constants
from telegraph import upload_file
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    name = update.message.from_user.first_name
    update.message.reply_text("Hello " + name + "," + constants.welcome_text)


def help_command(update: Update, _: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text("/start : to start the bot")
    update.message.reply_text("/donate : to donate to the developer")
    update.message.reply_text("or just send me an image/video to make a permanent link from it")


def upload_image(update: Update, context: CallbackContext) -> None:
    """Upload image to cloud"""
    global img
    chat_id = update.message.chat_id
    msg = update.message.reply_text("Trying to download...")
    try:
        try:
            file_id = update.message.photo[-1].get_file()
            img_name = str(chat_id) + '.jpg'
            img = file_id.download(img_name)
            msg.edit_text("Image Downloaded")
        except:
            update.message.reply_text("Operation Failed while downloading image.")
        try:
            msg.edit_text("Trying to upload...")
            tlink = upload_file(img)
            msg.edit_text(f"https://telegra.ph{tlink[0]}")
        except:
            update.message.reply_text("Operation Failed while uploading image.")
        os.remove(img)
    except:
        update.message.reply_text("Something went wrong!")


def upload_video(update: Update, _: CallbackContext) -> None:
    """Upload video to cloud"""
    global vid
    chat_id = update.message.chat_id
    if update.message.video.file_size < 5242880:
        msg = update.message.reply_text("Trying to download...")
        try:
            file_id = update.message.video.get_file()
            vid_name = str(chat_id) + '.mp4'
            vid = file_id.download(vid_name)
            msg.edit_text("Video Downloaded")
        except:
            update.message.reply_text("Operation Failed while downloading video.")
        try:
            msg.edit_text("Trying to upload...")
            tlink = upload_file(vid)
            msg.edit_text(f"https://telegra.ph{tlink[0]}")
        except:
            update.message.reply_text("Operation Failed while uploading video.")
        os.remove(vid)
    else:
        update.message.reply_text("Size Should Be Less Than 5 mb")


def button(update: Update, _: CallbackContext) -> None:
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text=f"Selected option: {query.data}")


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(secrets.BOT_TOKEN)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.video & ~Filters.command, upload_video))
    dispatcher.add_handler(MessageHandler(Filters.photo & ~Filters.command, upload_image))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
