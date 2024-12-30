import aiohttp

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

import variables


# Получение данных из Yandex Object Storage
async def get_object_from_bucket(object_key, access_key, secret_key, bucket_name):
    url = f'https://storage.yandexcloud.net/{bucket_name}/{object_key}'

    try:
        async with aiohttp.ClientSession() as session:
            auth = aiohttp.BasicAuth(access_key, password=secret_key)
            async with session.get(url, auth=auth) as response:
                response.raise_for_status()
                content = await response.text()
                return content
    except aiohttp.ClientError as e:
        print(f"Ошибка при обращении к Yandex Object Storage: {e}")
        return None
    except Exception as e:
        print(f"Ошибка: {e}")
        return None


# Отправка запроса к Yandex GPT с использованием aiohttp
async def send_request_to_gpt(question):
    bucket_content = await get_object_from_bucket(
        variables.YANDEX_STORAGE_OBJECT_KEY,
        variables.YANDEX_ACCESS_KEY,
        variables.YANDEX_SECRET_KEY,
        variables.YANDEX_STORAGE_BUCKET_NAME
    )
    if not bucket_content:
        return None

    data = {
        "modelUri": f"gpt://{variables.YANDEX_FOLDER_ID}/yandexgpt",
        "messages": [
            {"role": "system", "text": bucket_content},
            {"role": "user", "text": question},
        ],
    }

    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {variables.IAM_TOKEN}",
            "x-folder-id": variables.YANDEX_FOLDER_ID
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    result = await response.json()

                    if result.get("result") and result["result"].get("alternatives"):
                        return result["result"]["alternatives"][0].get("message", {}).get("text", "Ответ не найден.")
                    else:
                        return "Ответ от GPT не найден."
                else:
                    return None
    except Exception as e:
        print(f"Ошибка при отправке запроса: {e}")
        return None


# Обработка текстового сообщения от пользователя
async def handle_text_message(update: Update, context: CallbackContext):
    user_question = update.message.text

    await update.message.reply_text("Я ищу ответ... Подождите немного.")

    # Генерация ответа через Yandex GPT
    try:
        response_text = await send_request_to_gpt(user_question)

        if response_text:
            await update.message.reply_text(response_text)
        else:
            await update.message.reply_text("Ответ не найден.")
    except Exception as e:
        print(f"Ошибка при запросе к Yandex GPT: {e}")
        await update.message.reply_text("Не удалось получить ответ. Попробуйте позже.")


# /start
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине 'Операционные системы'.\nПришлите мне фотографию с вопросом или наберите его текстом.")


# /help
async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Я помогу подготовить ответ на экзаменационный вопрос по дисциплине 'Операционные системы'.\n Пришлите мне фотографию с вопросом или наберите его текстом.")


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
