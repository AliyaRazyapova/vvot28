import requests
from logger import logger
from helpers import get_file_path, get_image, encode_to_base64, recognize_text, get_object_from_bucket
import variables


def send_message(reply_text, input_message):
    data = {
        "chat_id": input_message["chat"]["id"],
        "text": reply_text,
        "reply_to_message_id": input_message.get("message_id"),
    }
    response = requests.post(f"{variables.TELEGRAM_API_URL}/sendMessage", json=data)
    if variables.DEBUG:
        logger.debug("Message sent", {"status_code": response.status_code})


def get_answer_from_gpt(question, iam_token):
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {iam_token}",
    }
    data = {
        "modelUri": f"gpt://{variables.FOLDER_ID}/yandexgpt",
        "messages": [
            {"role": "system", "text": get_object_from_bucket(variables.BUCKET_OBJECT_KEY)},
            {"role": "user", "text": question},
        ],
    }
    response = requests.post(variables.YC_API_GPT_URL, headers=headers, json=data)
    if response.status_code != 200:
        logger.error("Failed to get GPT response")
        return None
    alternatives = response.json().get("result", {}).get("alternatives", [])
    final_answer = next((alt["message"].get("text") for alt in alternatives if alt.get("status") == "ALTERNATIVE_STATUS_FINAL"), None)
    return final_answer


def handle_text_message(text, message, iam_token):
    answer = get_answer_from_gpt(text, iam_token)
    if not answer:
        send_message("Я не смог подготовить ответ на ваш запрос.", message)
    else:
        send_message(answer, message)


def handle_photo_message(photo, message, iam_token):
    if len(photo) > 3:
        send_message("Я могу обработать только одну фотографию.", message)
        return

    file_id = photo[-1]["file_id"]
    file_path = get_file_path(file_id)
    if not file_path:
        send_message("Не удалось обработать изображение.", message)
        return

    image = get_image(file_path)
    if not image:
        send_message("Ошибка загрузки изображения.", message)
        return

    text = recognize_text(encode_to_base64(image), iam_token)
    if not text:
        send_message("Я не могу обработать эту фотографию.", message)
    else:
        handle_text_message(text, message, iam_token)


def handle_message(message, iam_token):
    if (text := message.get("text")) in {"/start", "/help"}:
        send_message('Я помогу подготовить ответ на экзаменационный вопрос по дисциплине "Операционные системы"\nПришлите мне фотографию с вопросом или наберите его текстом.', message)
    elif text:
        handle_text_message(text, message, iam_token)
    elif photo := message.get("photo"):
        handle_photo_message(photo, message, iam_token)
    else:
        send_message("Могу обработать только текст или фото.", message)
