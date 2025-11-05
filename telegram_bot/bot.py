import os
import logging
import random
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes
from database import init_db, get_score, update_score

# Load environment variables
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Game choices
choices = ["rock", "paper", "scissors"]

def get_keyboard(show_play_again=False):
    if show_play_again:
        keyboard = [[InlineKeyboardButton("Play Again", callback_data="play_again")]]
    else:
        keyboard = [
            [
                InlineKeyboardButton("🗿 Rock", callback_data="rock"),
                InlineKeyboardButton("📄 Paper", callback_data="paper"),
                InlineKeyboardButton("✂️ Scissors", callback_data="scissors"),
            ]
        ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}! Let's play Rock, Paper, Scissors.",
        reply_markup=get_keyboard(),
    )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    user_choice = query.data
    user_id = query.from_user.id

    if user_choice == "play_again":
        await query.edit_message_text(
            text="Choose your weapon:", reply_markup=get_keyboard()
        )
        return

    bot_choice = random.choice(choices)
    result = ""

    if user_choice == bot_choice:
        result = "tie"
    elif (
        (user_choice == "rock" and bot_choice == "scissors")
        or (user_choice == "paper" and bot_choice == "rock")
        or (user_choice == "scissors" and bot_choice == "paper")
    ):
        result = "win"
    else:
        result = "loss"

    update_score(user_id, result)
    wins, losses, ties = get_score(user_id)

    text = (
        f"You chose {user_choice}, I chose {bot_choice}.\n"
        f"Result: You {result}!\n\n"
        f"Score: Wins: {wins}, Losses: {losses}, Ties: {ties}"
    )

    await query.edit_message_text(text=text, reply_markup=get_keyboard(show_play_again=True))

def main() -> None:
    """Start the bot."""
    init_db()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
