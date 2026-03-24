---
name: telegram-bot
description: Build Telegram bots with python-telegram-bot — commands, handlers, inline keyboards, and webhook deployment
---

# Telegram Bot Development

## Setup

```python
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm Piddy Bot.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start - Start\n/help - Help\n/status - Status")

app = Application.builder().token("TOKEN").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_cmd))
app.run_polling()
```

## Message Handlers

```python
from telegram.ext import MessageHandler, filters

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(update.message.text)

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
```

## Inline Keyboards

```python
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Status", callback_data="status")],
        [InlineKeyboardButton("Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Choose:", reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(f"You chose: {query.data}")

app.add_handler(CallbackQueryHandler(button_callback))
```

## Conversation Handler

```python
from telegram.ext import ConversationHandler

NAME, AGE = range(2)

async def start_conv(update, context):
    await update.message.reply_text("What's your name?")
    return NAME

async def name_handler(update, context):
    context.user_data["name"] = update.message.text
    await update.message.reply_text("How old are you?")
    return AGE

async def age_handler(update, context):
    name = context.user_data["name"]
    await update.message.reply_text(f"Hi {name}, age {update.message.text}!")
    return ConversationHandler.END

conv = ConversationHandler(
    entry_points=[CommandHandler("register", start_conv)],
    states={NAME: [MessageHandler(filters.TEXT, name_handler)],
            AGE: [MessageHandler(filters.TEXT, age_handler)]},
    fallbacks=[CommandHandler("cancel", lambda u, c: ConversationHandler.END)],
)
```

## Key Patterns
- Use `Application.builder()` (v20+) — replaces the old `Updater` class
- `run_polling()` for development, `run_webhook()` for production
- Use `context.user_data` / `context.chat_data` for per-user/chat state
- Rate limits: Telegram allows ~30 messages/sec to different chats, 1/sec to same chat
- File uploads: `await update.message.reply_document(document=open(path, "rb"))`
- Photos: `await update.message.reply_photo(photo=open(path, "rb"))`
- Error handling: `app.add_error_handler(error_handler)`
