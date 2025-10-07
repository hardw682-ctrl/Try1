import telebot
import requests
import json

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "=="  # Замените на ваш токен
YANDEX_API_KEY = "=="     # Замените на ваш ключ
YANDEX_FOLDER_ID = "=="         # Замените на ваш folder ID

# Ваш промпт-инструкция для AI
SYSTEM_PROMPT = """Ты - полезный AI-помощник.
Отвечай вежливо и подробно на вопросы пользователя.
Всегда старайся помочь решить проблему."""

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_yandex_gpt(user_message):
    """Функция для обращения к Yandex GPT"""
    try:
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": YANDEX_FOLDER_ID
        }

        data = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 1000
            },
            "messages": [
                {
                    "role": "system",
                    "text": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "text": user_message
                }
            ]
        }

        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()

        result = response.json()
        return result['result']['alternatives'][0]['message']['text']

    except Exception as e:
        return f"⚠️ Ошибка: {str(e)}"

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """🤖 Привет! Я твой AI-помощник.

Просто напиши мне любой вопрос или задачу, и я постараюсь помочь!"""

    bot.reply_to(message, welcome_text)

# Обработчик всех текстовых сообщений
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')

    # Получаем ответ от Yandex GPT
    ai_response = ask_yandex_gpt(message.text)

    # Отправляем ответ пользователю
    bot.reply_to(message, ai_response)

# Запуск бота
print("🟢 Бот запущен! Остановить: Ctrl+C")
bot.polling()