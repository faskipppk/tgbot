from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
)
import json

# Ваш Telegram ID (куда будут отправляться анкеты)
OWNER_ID = 6198995960  # Замените на ваш Telegram ID
# Токен бота
TOKEN = "8139612394:AAFfO7Q60L_gMhIHKQ8yVZZ3eRKiULoHz9Y"  # Замените на токен вашего бота

# Пример анкеты
ANKETA_EXAMPLE = """Анкета для вступления на наш Minecraft-сервер! 

Привет, будущий житель нашего уютного мира! 🌍
Заполни эту анкету, чтобы мы могли узнать тебя получше и принять в нашу дружную команду! 

1. Твой ник в Minecraft 
(Напиши свой игровой ник, чтобы мы знали, кто ты в игре!)

2. Как тебя зовут? 😄
(Настоящее имя или как тебя называть в чате, решай сам!)

3. Сколько тебе лет? 
(Возраст не сильно, но нам любопытно!)

4. Как давно играешь в Minecraft? ⛏️
(Новичок или уже мастер-строитель? Расскажи!)

5. Почему хочешь присоединиться к нашему серверу? 
(Что тебя привлекло? Любишь строить, выживать или тусить с крутыми ребятами?)

6. Что ты любишь делать в игре? 🛠
(Строить замки 🏰, копать шахты ⛏️, сражаться с мобами ⚔️ или что-то ещё?)

7. Был ли опыт игры на других серверах? 🌐
(Если да, расскажи, что тебе там нравилось или не нравилось!)

8. Расскажи что-нибудь о себе! 
(Хобби, любимая еда, или просто пару слов !)

9. Согласен ли ты с правилами сервера? 📜
(Ознакомься с правилами на нашем канале! И напиши «Да» или «Согласен»!)

Мы рассмотрим её как только сможем! 
Спасибо, что хочешь стать частью нашего мира! 
Ждём тебя! 🚪✨"""

# Словарь для хранения анкет (user_id: anketa_text)
anketas = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Создаем клавиатуру с двумя кнопками
    keyboard = [
        [InlineKeyboardButton("Просмотреть анкету", callback_data="view")],
        [InlineKeyboardButton("Ввести анкету", callback_data="submit")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Добро пожаловать! Выберите действие:", reply_markup=reply_markup
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "view":
        await query.message.reply_text(ANKETA_EXAMPLE)
    elif query.data == "submit":
        context.user_data["awaiting_anketa"] = True
        await query.message.reply_text(
            f"Вот пример анкеты:\n\n{ANKETA_EXAMPLE}\n\nПожалуйста, введите текст вашей анкеты:"
        )
    elif query.data.startswith("accept_") or query.data.startswith("reject_"):
        # Обработка принятия/отклонения анкеты
        user_id = int(query.data.split("_")[1])
        if query.data.startswith("accept_"):
            # Уведомляем пользователя о принятии
            await context.bot.send_message(
                chat_id=user_id,
                text="Ваша анкета принята, в скором времени мы вас добавим.(⁠づ⁠｡⁠◕⁠‿⁠‿⁠◕⁠｡⁠)⁠づ"
            )
            await query.message.reply_text(f"Анкета пользователя {user_id} принята.")
        else:
            # Уведомляем пользователя об отклонении
            await context.bot.send_message(
                chat_id=user_id,
                text="Ваша анкета отклонена (⁠ʘ⁠ᗩ⁠ʘ⁠’⁠)"
            )
            await query.message.reply_text(f"Анкета пользователя {user_id} отклонена.")
        # Удаляем анкету из словаря
        if user_id in anketas:
            del anketas[user_id]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    user_id = user.id
    username = user.username
    user_mention = f"@{username}" if username else f"[{user.first_name}](tg://user?id={user_id})"

    if context.user_data.get("awaiting_anketa", False):
        anketa_text = update.message.text
        # Сохраняем анкету
        anketas[user_id] = anketa_text
        # Создаем клавиатуру для владельца (принять/отклонить)
        keyboard = [
            [
                InlineKeyboardButton("Принять", callback_data=f"accept_{user_id}"),
                InlineKeyboardButton("Отклонить", callback_data=f"reject_{user_id}"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        # Отправляем анкету владельцу
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"Новая анкета от {user_mention}:\n\n{anketa_text}",
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
        # Уведомляем пользователя
        await update.message.reply_text(
            "Ожидайте рассмотрения вашей анкеты. Мы напишем вам, когда решим, принимать вас или нет.🕔"
        )
        context.user_data["awaiting_anketa"] = False
    else:
        await update.message.reply_text(
            "Пожалуйста, выберите действие через команду /start."
        )

def main():
    # Создаем приложение
    app = Application.builder().token(TOKEN).build()

    # Регистрируем команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
