import base64
import requests
from pathlib import Path
from logger import logger
import variables


def encode_to_base64(bytes_content):
    return base64.b64encode(bytes_content).decode("utf-8")


def get_file_path(file_id):
    url = f"{variables.TELEGRAM_API_URL}/getFile"
    response = requests.get(url, params={"file_id": file_id})
    if response.status_code != 200:
        logger.error("Failed to get file path", {"file_id": file_id})
        return None
    return response.json().get("result", {}).get("file_path")


def get_image(file_path):
    url = f"{variables.TELEGRAM_FILE_URL}/{file_path}"
    response = requests.get(url)
    if response.status_code != 200:
        logger.error("Failed to download image", {"file_path": file_path})
        return None
    return response.content


def recognize_text(base64_image, iam_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {iam_token}",
    }
    response = requests.post(
        variables.YC_API_OCR_URL,
        headers=headers,
        json={"content": base64_image, "mimeType": "image/jpeg", "languageCodes": ["ru", "en"]},
    )
    if response.status_code != 200:
        logger.error("OCR recognition failed")
        return None
    return response.json().get("result", {}).get("textAnnotation", {}).get("fullText")


def get_object_from_bucket(object_key):
    try:
        with open(Path("/function/storage", variables.MOUNT_POINT, object_key), "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        logger.error("File not found in bucket", {"object_key": object_key})
        return ""
