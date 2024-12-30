from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

import variables

TELEGRAM_BOT_TOKEN = variables.TELEGRAM_BOT_TOKEN


# /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Привет! Я бот. Отправьте команду /help для получения помощи.")


# /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text("Я помогу подготовить ответ на экзаменационный вопрос по дисциплине 'Операционные системы'.\n Пришлите мне фотографию с вопросом или наберите его текстом.")


def main():
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    application.run_polling()


if __name__ == '__main__':
    main()
