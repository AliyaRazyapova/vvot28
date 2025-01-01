terraform {
  required_providers {
    yandex = {
      source = "yandex-cloud/yandex"
    }
  }
  required_version = ">= 0.13"
}

provider "yandex" {
  cloud_id                 = var.cloud_id
  folder_id                = var.folder_id
  zone                     = var.zone
  service_account_key_file = var.service_account_key_file
}

resource "yandex_storage_bucket" "telegram_bot" {
  bucket        = "telegram-bot-files"
  acl    = "private"
}

resource "null_resource" "register_webhook" {
  provisioner "local-exec" {
    command = "curl -X POST https://api.telegram.org/bot${var.tg_bot_key}/setWebhook -d url=https://functions.yandexcloud.net/${var.cloud_function_url}"
  }

  depends_on = [yandex_storage_bucket.telegram_bot]
}

resource "null_resource" "deregister_webhook" {
  provisioner "local-exec" {
    command = "curl -X POST https://api.telegram.org/bot${var.tg_bot_key}/deleteWebhook"
  }

  depends_on = [yandex_storage_bucket.telegram_bot]
}

resource "yandex_storage_object" "telegram_instruction" {
  bucket = yandex_storage_bucket.telegram_bot.bucket
  key   = "instructions.txt"
  source = "instructions.txt"
}
