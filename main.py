import telegram 
from telegram.ext import Updater, CommandHandler 
import requests 
import datetime
import random
 
def start(update, context): 
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi! I'm a news bot. Send me /news to get the latest headlines.") 
 
def news(update, context): 
    # Send a request to the Codeforces API to get the problem 
    api_key = "006bd70a81b066df6f1003d594ed5e6cc4c9abe7"     
    secret = "96e2964abe55f0bb755f18f9d0fa00da2b843040"
    tags = input()
    time = datetime.now()
    rand = random.randint(100000,999999)
    url = f"https://codeforces.com/api/problemset.problems?tags={tags}&apiKey={api_key}&time={time}&apiSig={rand}sha512Hex({rand}/problemset.problems?tags={tags}&apiKey={api_key}&time={time}#{secret})" 
    response = requests.get(url) 

    # Construct a message to get question from codeforces
    message = response.json()["Problem"]
 
    # Send the message to the user 
    context.bot.send_message(chat_id=update.effective_chat.id, text=message) 
 
# Set up the Updater and Dispatcher 
updater = Updater(token="", use_context=True) 
dispatcher = updater.dispatcher 
 





