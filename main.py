import json
import random
import os

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from words import words

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN environment variable not found")


# -----------------------
# users.json
# -----------------------

def load_users():
    try:
        with open("users.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}


def save_users(users):
    with open("users.json", "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)


users = load_users()


# -----------------------
# Commands
# -----------------------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {
            "dozd": 0
        }
        save_users(users)

    await update.message.reply_text(
        "سلام 👋\n"
        "برای شروع آزمون /quiz را بزن."
    )


async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"dozd": 0}

    await update.message.reply_text(
        f"امتیاز فعلی تو: {users[user_id]['dozd']} dozd"
    )


async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    question = random.choice(words)

    context.user_data["current_question"] = question

    await update.message.reply_text(
        f"معنی این کلمه چیست؟\n\n{question['word']}"
    )


# -----------------------
# Answers
# -----------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = str(update.effective_user.id)

    if user_id not in users:
        users[user_id] = {"dozd": 0}

    if "current_question" not in context.user_data:
        return

    correct_answer = context.user_data["current_question"]["meaning"]

    user_answer = update.message.text.strip()

    if user_answer == correct_answer:

        users[user_id]["dozd"] += 10

        await update.message.reply_text(
            f"✅ درست!\n+10 dozd\n\nمجموع: {users[user_id]['dozd']}"
        )

    else:

        users[user_id]["dozd"] -= 1

        await update.message.reply_text(
            f"❌ اشتباه\n"
            f"جواب درست: {correct_answer}\n\n"
            f"مجموع: {users[user_id]['dozd']}"
        )

    save_users(users)

    del context.user_data["current_question"]


# -----------------------
# Main
# -----------------------

def main():

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CommandHandler("score", score))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("BOT STARTED")

    app.run_polling()


if __name__ == "__main__":
    main()
