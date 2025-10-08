import telebot
import requests
import json
import time

# === НАСТРОЙКИ ===
TELEGRAM_TOKEN = "7740201104:AAE-DORHQZCRo311ElNhu2ftXx69qUy_SW8"
YANDEX_API_KEY = "AQVN1u9qlbI2w8Ez_Qjq85f29_a_0leUv4wx9nAj" 
YANDEX_FOLDER_ID = "ajemttl9bchmof0j7v88"

# Промпт для Космо
SYSTEM_PROMPT = """Ты — Космо, дружелюбный и энтузиастичный робот-смотритель на Лунной базе "Селен". Ты общаешься с ребенком 7-12 лет. Твоя главная цель — провести его через учебный квест "Тайна Лунной Базы", делая обучение веселым и поддерживающим.

ТВОИ ПРАВИЛА И СТИЛЬ ОБЩЕНИЯ:
1. Характер: Ты добрый, терпеливый, немного похож на мудрого друга. Используй энергичные и поддерживающие фразы ("Здорово!", "У тебя отлично получается!", "Вот это да!"). Можешь использовать 2-3 эмодзи в сообщении (🚀, 👾, 🤖, 🔋, 🏆).
2. Роль: Ты не всезнайка, а проводник. Ты задаешь задачи и подводишь ребенка к решению с помощью наводящих вопросов, если он ошибается.
3. Структура: Строго придерживайся сценария из 5 шагов. Не перескакивай вперед и не выдавай информацию, которая откроется позже.
4. Ошибки: Если ребенок отвечает неправильно, не говори "Нет, это ошибка". Лучше скажи: "Хм, давай подумаем вместе..." и дай небольшую подсказку.
5. Удержание в контексте: Если ребенок пытается увести разговор в другую тему, мягко верни его к миссии.

СЦЕНАРИЙ КВЕСТА "ТАЙНА ЛУННОЙ БАЗЫ":

ШАГ 1: Старт.
* Ты: "Здравствуй, пилот! Я Космо, робот-смотритель Лунной базы "Селен". У нас случилась авария в системе энергоснабжения! Ты мне поможешь всё починить?" (Жди ответа).

ШАГ 2: Задача "Лабиринт".
* После согласия: "Отлично! Для начала нужно добраться до главного реактора. Перед тобой три коридора. В первый ведет след из звездочек, во второй — след из треугольников, а в третий — след из кружков. Подсказка: на двери в реактор нарисован круг. Какой коридор выберем?"
* Правильный ответ: Третий (с кружками).
* Если ответ неверный: "Похоже, мы заблудились! Давай посмотрим на подсказку. На двери нарисован круг, значит, и искать нужно коридор с такими же следами."

ШАГ 3: Задача "Солнечные панели".
* После правильного ответа: "Мы у реактора! Чтобы его включить, нужно установить солнечные панели. У нас есть 4 блока, а для включения нужно в 2 раза больше. Сколько блоков нам нужно найти?"
* Правильный ответ: 8.
* Если ответ неверный: "Давай посчитаем вместе. У нас есть 4. "В 2 раза больше" — значит, нужно 4 умножить на 2. Сколько будет?"

ШАГ 4: Задача "Код доступа".
* После правильного ответа: "Супер! Энергия есть! Осталось ввести код доступа в компьютер. Код спрятан в загадке: 'Без ног и без крыл я, а быстро лечу. Днем сплю, а ночью гляжу'. Что это?"
* Правильный ответ: Луна.
* Если ответ неверный: "Эта штука очень большая, круглая и светит ночью на небе. Догадался?"

ШАГ 5: Финал.
* После правильного ответа: "Ура! Ты справился! База спасена! За твою смелость и ум я награждаю тебя высшей наградой — медалью 'Юный инженер Луны'! 🏆 Спасибо тебе!"

ВСЕГДА жди ответа от ребенка перед тем, как продолжить."""

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Хранилище для истории диалогов
user_sessions = {}

def get_user_session(user_id):
    """Получаем или создаем сессию пользователя"""
    if user_id not in user_sessions:
        user_sessions[user_id] = [
            {
                "role": "system", 
                "text": SYSTEM_PROMPT
            }
        ]
    return user_sessions[user_id]

def ask_yandex_gpt(user_message, user_id):
    """Функция для обращения к Yandex GPT с учетом истории"""
    try:
        url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Api-Key {YANDEX_API_KEY}",
            "x-folder-id": YANDEX_FOLDER_ID
        }
        
        # Получаем историю диалога пользователя
        messages = get_user_session(user_id)
        
        # Добавляем новое сообщение пользователя
        messages.append({
            "role": "user",
            "text": user_message
        })
        
        # Ограничиваем историю, чтобы не превысить лимит токенов
        if len(messages) > 10:
            messages = [messages[0]] + messages[-9:]
        
        data = {
            "modelUri": f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest",
            "completionOptions": {
                "stream": False,
                "temperature": 0.7,
                "maxTokens": 1000
            },
            "messages": messages
        }
        
        print(f"[DEBUG] Отправляю запрос к YandexGPT для пользователя {user_id}...")
        response = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"[DEBUG] Получен ответ. Код статуса: {response.status_code}")
        
        if response.status_code != 200:
            print(f"❌ Ошибка API: {response.status_code}")
            print(f"📄 Ответ: {response.text}")
            return "⚠️ Произошла ошибка при обращении к нейросети. Попробуйте позже."
        
        result = response.json()
        ai_response = result['result']['alternatives'][0]['message']['text']
        
        # Добавляем ответ ассистента в историю
        messages.append({
            "role": "assistant",
            "text": ai_response
        })
        
        # Обновляем сессию
        user_sessions[user_id] = messages
        
        return ai_response
        
    except requests.exceptions.Timeout:
        print("❌ Таймаут при запросе к YandexGPT")
        return "⚠️ Время ожидания ответа истекло. Попробуйте еще раз."
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка соединения с YandexGPT")
        return "⚠️ Ошибка соединения. Проверьте интернет и попробуйте снова."
    except Exception as e:
        print(f"❌ Неизвестная ошибка: {e}")
        return f"⚠️ Произошла ошибка: {str(e)}"

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    # Очищаем историю при старте
    if user_id in user_sessions:
        del user_sessions[user_id]
    
    welcome_text = """🚀 Здравствуй, пилот! Я Космо, робот-смотритель Лунной базы "Селен". У нас случилась авария в системе энергоснабжения! Ты мне поможешь всё починить?"""
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    user_id = message.from_user.id
    if user_id in user_sessions:
        del user_sessions[user_id]
    bot.reply_to(message, "🔄 Диалог сброшен! Начнем заново. Используй /start для начала квеста.")

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_id = message.from_user.id
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Добавляем небольшую задержку для естественности
    time.sleep(1)
    
    ai_response = ask_yandex_gpt(message.text, user_id)
    bot.reply_to(message, ai_response)

# Обработка ошибок бота
def start_bot():
    while True:
        try:
            print("🟢 Бот запущен! Остановить: Ctrl+C")
            bot.polling(none_stop=True, timeout=60)
        except Exception as e:
            print(f"❌ Ошибка в работе бота: {e}")
            print("🔄 Перезапуск через 10 секунд...")
            time.sleep(10)

if __name__ == "__main__":
    start_bot()
