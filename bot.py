import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import random
import json
import os

TOKEN = "8203696019:AAHOJ6V8N7xPUvSJ1Xd_3b68dBPAgj51bXc"
bot = telebot.TeleBot(TOKEN)

# Используем абсолютный путь к файлу в той же папке, где находится скрипт
SCRIPT_DIR = os.path.dirname(os.path.abspath(file))
SCORE_FILE = os.path.join(SCRIPT_DIR, "scores.json")

# Загрузка счёта из файла
def load_scores():
    try:
        if os.path.exists(SCORE_FILE):
            with open(SCORE_FILE, "r", encoding='utf-8') as f:
                data = json.load(f)
                return data
        else:
            print("⚠️ Файл scores.json не существует, создан пустой словарь")
        return {}
    except Exception as e:
        print(f"❌ Ошибка загрузки файла: {e}")
        return {}

# Сохранение счёта в файл
def save_scores(scores):
    try:
        with open(SCORE_FILE, "w", encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return False

# Команда /start
@bot.message_handler(commands=['rps'])
def start_game(message):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🪨 Камень", callback_data="rock"),
        InlineKeyboardButton("✂️ Ножницы", callback_data="scissors"),
        InlineKeyboardButton("📄 Бумага", callback_data="paper")
    )
    bot.send_message(message.chat.id, "Выбери свой ход:", reply_markup=markup)

# Команда /score
@bot.message_handler(commands=['score'])
def show_score(message):
    user_id = str(message.from_user.id)
    scores = load_scores()

    if user_id in scores:
        user_score = scores[user_id]
        score_text = (
            f"📊 Ваш текущий счёт:\n"
            f"🏆 Победы: {user_score['wins']}\n"
            f"😢 Поражения: {user_score['losses']}\n"
            f"🤝 Ничьи: {user_score['draws']}"
        )
    else:
        score_text = "Вы ещё не сыграли ни одной игры. Начните с команды /start!"

    bot.send_message(message.chat.id, score_text)

# Обработка выбора игрока
@bot.callback_query_handler(func=lambda call: call.data in ["rock", "scissors", "paper"])
def handle_choice(call):
    user_id = str(call.from_user.id)
    user_choice = call.data
    bot_choice = random.choice(["rock", "scissors", "paper"])

    outcomes = {
        ("rock", "scissors"): "win",
        ("scissors", "paper"): "win",
        ("paper", "rock"): "win",
        ("scissors", "rock"): "lose",
        ("paper", "scissors"): "lose",
        ("rock", "paper"): "lose"
    }

    scores = load_scores()
    
    # Инициализируем счет для нового пользователя
    if user_id not in scores:
        scores[user_id] = {"wins": 0, "losses": 0, "draws": 0}
        print(f"👤 Создан новый пользователь: {user_id}")

    # Определяем результат
    if user_choice == bot_choice:
        result_text = "Ничья 🤝"
        scores[user_id]["draws"] += 1
    else:
        outcome = outcomes.get((user_choice, bot_choice), "error")
        if outcome == "win":
            result_text = "Вы победили! 🏆"
            scores[user_id]["wins"] += 1
        elif outcome == "lose":
            result_text = "Вы проиграли 😢"
            scores[user_id]["losses"] += 1
        else:
            result_text = "Ошибка"

    # Сохраняем результаты
    if save_scores(scores):
        print(f"💾 Счет пользователя {user_id} обновлен")
    else:
        print(f"❌ Не удалось сохранить счет пользователя {user_id}")

    emoji_map = {
        "rock": "🪨",
        "scissors": "✂️",
        "paper": "📄"
    }
    score_text = f"Победы: {scores[user_id]['wins']}, Поражения: {scores[user_id]['losses']}, Ничьи: {scores[user_id]['draws']}"

    bot.send_message(
        call.message.chat.id,
        f"Вы выбрали: {emoji_map[user_choice]}\nБот выбрал: {emoji_map[bot_choice]}\n\n{result_text}\n\n📊 Ваш счёт:\n{score_text}"
    )
# Запуск бота
print("Бот запущен...")
try:
    bot.polling()
except KeyboardInterrupt:
    print("\n🛑 Бот остановлен")
except Exception as e:
    print(f"\n❌ Ошибка при работе бота: {e}")