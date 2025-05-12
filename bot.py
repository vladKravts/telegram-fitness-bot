from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json

BOT_TOKEN = '7294561923:AAHIn8E5DGoaDTeGJeXjrm3glXpPLoPqPU4'

# Глобальное хранилище выбора пользователя
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Предложим выбрать количество дней
    with open('workot_plan.json', 'r', encoding='utf-8') as file:
        data = json.load(file)

    day_options = sorted(set(key.split('_')[0] for key in data.keys()))
    keyboard = [[InlineKeyboardButton(f"{days} дня", callback_data=f"days_{days}")] for days in day_options]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери количество тренировочных дней в сплите:", reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    with open('workot_plan.json', 'r', encoding='utf-8') as file:
        plan_data = json.load(file)

    chat_id = query.from_user.id

    # Обработка выбора дней
    if data.startswith("days_"):
        days = data.split("_")[1]
        user_state[chat_id] = {"days": days}

        # Предложим фокус
        focus_keyboard = []
        for key in plan_data:
            if key.startswith(days):
                focus = plan_data[key]['focus']
                callback = f"focus_{key}"
                focus_keyboard.append([InlineKeyboardButton(focus, callback_data=callback)])

        await query.edit_message_text(
            f"Выбери фокус тренировок на {days} дня:",
            reply_markup=InlineKeyboardMarkup(focus_keyboard)
        )
        return

    # Обработка выбора фокуса
    if data.startswith("focus_"):
        key = data.replace("focus_", "")
        user_state[chat_id]["split_key"] = key

        days = plan_data[key]["days"]
        day_buttons = [[InlineKeyboardButton(day, callback_data=f"day_{day}")] for day in days]

        await query.edit_message_text(
            "Выбери день тренировки:",
            reply_markup=InlineKeyboardMarkup(day_buttons)
        )
        return

    # Обработка выбора дня
    if data.startswith("day_"):
        day = data.replace("day_", "")
        split_key = user_state[chat_id]["split_key"]
        day_data = plan_data[split_key]["days"].get(day)

        if not day_data:
            await query.edit_message_text("Ошибка: тренировка не найдена.")
            return

        msg = f"Тренировка: {day}\nМышцы: {', '.join(day_data['muscle_groups'])}\n"
        if day_data["exercises"]:
            for ex in day_data["exercises"]:
                msg += f"\n{ex['name']}: {ex['sets']}x{ex['reps']} (вес: {ex.get('last_weight', '—')})"
        else:
            msg += "\nУпражнения пока не добавлены."

        await query.edit_message_text(msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Команды:\n/start — начать\n/help — помощь")

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.run_polling()