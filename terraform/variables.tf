variable "cloud_id" {
  description = "ID облака"
  type        = string
}

variable "folder_id" {
  description = "ID каталога"
  type        = string
}

variable "zone" {
  description = "Зона размещения ресурсов"
  type        = string
  default     = "ru-central1-a"
}

variable "service_account_key_file" {
  description = "Путь к ключу учетной записи"
  type        = string
}

variable "tg_bot_key" {
  description = "Токен для доступа к Telegram Bot API"
  type        = string
}

variable "cloud_function_url" {
  description = "URL для облачной функции"
  type        = string
}
