variable "cloud_id" {
  type        = string
  description = "Идентификатор облака по умолчанию"
}

variable "folder_id" {
  type        = string
  description = "Идентификатор каталога по умолчанию"
}

variable "sa_key_file_path" {
  type        = string
  description = "Путь к ключу сервисного аккаунта с ролью admin"
  default     = "key.json"
}

variable "tg_bot_key" {
  type        = string
  description = "Токен telegram-бота"
}

variable "bucket_name" {
  type        = string
  description = "Название бакета, в котором находится объект с инструкцией к YandexGPT"
  default     = "tg-bot-bucket-098"
}

variable "bucket_object_key" {
  type        = string
  description = "Ключ объекта, в котором написана инструкция к YandexGPT"
  default     = "instruction.txt"
}
