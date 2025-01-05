terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
    telegram = {
      source  = "yi-jiayu/telegram"
      version = "0.3.1"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = "ru-central1-a"
  service_account_key_file = pathexpand(var.sa_key_file_path)
}

provider "telegram" {
  bot_token = var.tg_bot_key
}

data "archive_file" "content" {
  type        = "zip"
  source_dir  = "../bot"
  output_path = "../archive/content.zip"
}

resource "yandex_function" "tg_bot" {
  name               = "tg_bot"
  description        = <<EOT
                       Функция принимает текстовые и мультимедийные
                       сообщения (фото), полученные от пользователей
                       Telegram-бота, и, используя YandexGPT,
                       генерирует ответы на их вопросы
                       EOT
  entrypoint         = "main.handler"
  memory             = "128"
  runtime            = "python312"
  service_account_id = yandex_iam_service_account.sa_tg_bot.id
  user_hash          = data.archive_file.content.output_sha512
  execution_timeout  = "30"

  environment = {
    TELEGRAM_BOT_TOKEN = var.tg_bot_key
    FOLDER_ID          = var.folder_id
    MOUNT_POINT        = var.bucket_name
    BUCKET_OBJECT_KEY  = var.bucket_object_key
  }

  content {
    zip_filename = data.archive_file.content.output_path
  }

  mounts {
    name = var.bucket_name
    mode = "ro"
    object_storage {
      bucket = yandex_storage_bucket.tg_bot_bucket.bucket
    }
  }
}

resource "yandex_function_iam_binding" "tg_bot_iam" {
  function_id = yandex_function.tg_bot.id
  role        = "functions.functionInvoker"
  members     = ["system:allUsers"]
}

resource "telegram_bot_webhook" "tg_bot_webhook" {
  url = "https://functions.yandexcloud.net/${yandex_function.tg_bot.id}"
}

resource "yandex_storage_bucket" "tg_bot_bucket" {
  bucket = var.bucket_name
}

resource "yandex_storage_object" "yandexgpt_instruction" {
  bucket = yandex_storage_bucket.tg_bot_bucket.id
  key    = var.bucket_object_key
  source = "instruction.txt"
}

resource "yandex_iam_service_account" "sa_tg_bot" {
  name = "sa-tg-bot"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_ai_vision_iam" {
  folder_id = var.folder_id
  role      = "ai.vision.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_ai_language_models_iam" {
  folder_id = var.folder_id
  role      = "ai.languageModels.user"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}

resource "yandex_resourcemanager_folder_iam_member" "sa_tg_bot_storage_viewer_iam" {
  folder_id = var.folder_id
  role      = "storage.viewer"
  member    = "serviceAccount:${yandex_iam_service_account.sa_tg_bot.id}"
}
