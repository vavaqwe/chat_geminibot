import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import config
from ai import ai_response
from collections import deque

bot = telebot.TeleBot(config.TELEGRAM_API)

chat_contexts = {} 
MAX_CONTEXT_LENGTH = 3

@bot.message_handler(commands=['start'])
def main(message):
    chat_id = message.chat.id
    us_name = message.from_user.first_name
    
    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = deque(maxlen=MAX_CONTEXT_LENGTH)

    bot.send_message(chat_id, f'Вітаю {us_name}')
    
@bot.message_handler(content_types=['text'])
def func(message):
    chat_id = message.chat.id
    user_message = message.text
    
    if chat_id not in chat_contexts:
        chat_contexts[chat_id] = deque(maxlen=MAX_CONTEXT_LENGTH)
        
    user_entry = {"role": "user", "parts": [{"text": user_message}]}
    chat_contexts[chat_id].append(user_entry)
    
    current_context = list(chat_contexts[chat_id]) 
    
    res = ai_response(current_context) 
    
    bot.send_message(chat_id, res)
    
    assistant_entry = {"role": "model", "parts": [{"text": res}]}
    chat_contexts[chat_id].append(assistant_entry)
    
bot.infinity_polling()

