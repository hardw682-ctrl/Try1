import telebot
import requests
import json

TELEGRAM_TOKEN = "7740201104:AAE-DORHQZCRo311ElNhu2ftXx69qUy_SW8"
YANDEX_API_KEY = "AQVN1u9qlbI2w8Ez_Qjq85f29_a_0leUv4wx9nAj"
YANDEX_FOLDER_ID = "ajemttl9bchmof0j7v88"

SYSTEM_PROMPT = "Ты — Космо, дружелюбный робот-смотритель на Лунной базе. Общаешься с ребенком 7-12 лет. Будь веселым и поддерживающим."

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def ask_yandex_gpt(user_message):
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
                {"role": "system", "text": SYSTEM_PROMPT},
                {"role": "user", "text": user_message}
            ]
        }
        response = requests.post(url, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['result']['alternatives'][0]['message']['text']
        return "Ошибка подключения к AI"
    except Exception as e:
        return f"Ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 Здравствуй, пилот! Я Космо, робот-смотритель Лунной базы. У нас авария! Поможешь всё починить?")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    bot.send_chat_action(message.chat.id, 'typing')
    ai_response = ask_yandex_gpt(message.text)
    bot.reply_to(message, ai_response)

print("🟢 Бот запущен!")
bot.infinity_polling()
