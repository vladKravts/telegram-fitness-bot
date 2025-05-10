from pydoc import describe
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
import json



BOT_TOKEN = '7294561923:AAHIn8E5DGoaDTeGJeXjrm3glXpPLoPqPU4'  # токен пользователя

async def choose_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Day 1", callback_data='Day 1')],
        [InlineKeyboardButton("Day 2", callback_data='Day 2')],
        [InlineKeyboardButton("Day 3", callback_data='Day 3')],
        [InlineKeyboardButton("Day 4", callback_data='Day 4')],
        [InlineKeyboardButton("Day 5", callback_data='Day 5')],
        [InlineKeyboardButton("Day 6-7", callback_data='Day 6-7')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Выбери день тренировки:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    day = query.data

    with open('workot_plan.json', 'r', encoding='utf-8') as file:
        plan = json.load(file)

    day_plan = plan.get(day, {})
    if not day_plan:
        await query.edit_message_text(f"План на {day} не найден.")
        return

    message = f"Тренировка: {day}\nГруппы мышц: {', '.join(day_plan['muscle_groups'])}\n\n"
    for ex in day_plan['exercises']:
        message += f"{ex['name']}: {ex['sets']}x{ex['reps']} (предыдущий вес: {ex['last_weight'] or '—'})\n"

    await query.edit_message_text(message)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я твой фитнес-бот 💪")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Я могу помочь тебе с тренировками. Команды : /start , /help ,   💪")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("choose_day", choose_day))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()

