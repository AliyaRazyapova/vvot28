import requests
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import variables

TELEGRAM_BOT_TOKEN = variables.TELEGRAM_BOT_TOKEN
YANDEX_GPT_API_KEY = variables.YANDEX_GPT_API_KEY
YANDEX_BUCKET_NAME = variables.YANDEX_STORAGE_BUCKET_NAME
YANDEX_OBJECT_KEY = variables.YANDEX_STORAGE_OBJECT_KEY
YANDEX_ACCESS_KEY = variables.YANDEX_ACCESS_KEY
YANDEX_SECRET_KEY = variables.YANDEX_SECRET_KEY

# Устанавливаем API ключ для YandexGPT
openai.api_key = YANDEX_GPT_API_KEY


# Инструкция для YandexGPT API из Yandex Object Storage
def get_instructions_from_yandex_storage():
    url = f'https://storage.yandexcloud.net/{YANDEX_BUCKET_NAME}/{YANDEX_OBJECT_KEY}'

    try:
        response = requests.get(url, auth=(YANDEX_ACCESS_KEY, YANDEX_SECRET_KEY))
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении инструкции: {e}")
        return None


# /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине 'Операционные системы'.\nПришлите мне фотографию с вопросом или наберите его текстом.")


# /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине 'Операционные системы'.\n Пришлите мне фотографию с вопросом или наберите его текстом.")


async def handle_text_message(update: Update, context: CallbackContext):
    # Текст вопроса
    question_text = update.message.text

    # Инструкция для YandexGPT из хранилища
    instructions = get_instructions_from_yandex_storage()
    if not instructions:
        await update.message.reply_text("Я не смог получить инструкции для генерации ответа.")
        return

    # Запрос для YandexGPT
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=f"{instructions}\nОтветьте на экзаменационный вопрос: {question_text}",
            max_tokens=2000,
            n=1,
            stop=None,
            temperature=0.7,
        )

        answer = response.choices[0].text.strip()
        await update.message.reply_text(answer)

    except Exception as e:
        print(f"Ошибка при запросе к YandexGPT API: {e}")
        await update.message.reply_text("Я не смог подготовить ответ на экзаменационный вопрос.")


def main():
    application = Application.builder().token(variables.TELEGRAM_BOT_TOKEN).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Обработчик текстового сообщения
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))

    application.run_polling()


if __name__ == '__main__':
    main()
