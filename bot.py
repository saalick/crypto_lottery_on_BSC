import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ChatAction
import logging
import openai

TOKEN = "5662393571:AAH0V3BKs2PVa8K2Sz-tsVDmgBUD1Nz44do"
OPENAI_API_KEY = "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"
ALLOWED_GROUP_ID = "-1001186189356"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
bot_info = {
    "name": "Bonobo",
    "past_chats": {}
}
# Create an Updater object
MAX_MESSAGES = 50
updater = Updater(token=TOKEN, use_context=True)
bot = updater.bot

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

# Store chat history
chat_history = {}


def check_authorization(update):
    """
    Check if the bot is authorized to work in the group.
    """
    chat_id = str(update.message.chat_id)
    if chat_id == ALLOWED_GROUP_ID:
        return True
    else:
        return False


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm Bonobo, please send /sendimage {text}or /ask {question}")


def send_image(update, context):
    # Check if the bot is authorized to work in the group
    if not check_authorization(update):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I'm not allowed to work here.")
        return

    context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    text = ' '.join(context.args)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {OPENAI_API_KEY}"
    }
    data = {
        "model": "image-alpha-001",
        "prompt": f"Generate an image of {text}",
        "num_images": 1,
        "size": "256x256",
        "response_format": "url"
    }
    response = requests.post('https://api.openai.com/v1/images/generations', headers=headers, json=data)
    image_url = response.json()["data"][0]["url"]
    context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)


def ask(update, context):
    # Check if the bot is authorized to work in the group
    if not check_authorization(update):
        context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I'm not allowed to work here.")
        return
    # Get user message
    message = update.message.text[5:].strip()  # Remove "/ask " from the message
  # Add user message to chat history
    chat_id = str(update.message.chat_id)
    if chat_id not in bot_info["past_chats"]:
        bot_info["past_chats"][chat_id] = []
    bot_info["past_chats"][chat_id].append(message)

    # Truncate message history
    if len(bot_info["past_chats"][chat_id]) > MAX_MESSAGES:
        bot_info["past_chats"][chat_id] = bot_info["past_chats"][chat_id][-MAX_MESSAGES:]

    # Generate response
    prompt = "\n".join(bot_info["past_chats"][chat_id][-3:])
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"As the bonobo,answer this :\n{prompt}\n",
        max_tokens=128,
        n=1,
        stop=None,
        temperature=0.5,
    ).choices[0].text

    # Store chat history
    if len(bot_info["past_chats"][chat_id]) >= MAX_MESSAGES:
        bot_info["past_chats"][chat_id] = bot_info["past_chats"][chat_id][-MAX_MESSAGES:]
    bot_info["past_chats"][chat_id].append(response)

    # Send message back
    context.bot.send_message(chat_id=update.effective_chat.id, text=response)


def unknown(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I don't understand your command.")


def main():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("sendimage", send_image))
    dp.add_handler(CommandHandler("ask", ask))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
