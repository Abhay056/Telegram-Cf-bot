from flask import Flask, request
import telegram
from telegram.ext import Application, CommandHandler, ContextTypes, Updater
from telegram import Update
import requests
import random
import asyncio
import os

TOKEN = os.getenv('BOT_TOKEN')
app = Flask(__name__)

@app.route('/hook', methods=['POST'])
def webhook_handler():
    if request.method == "POST":
        update = telegram.Update.de_json(request.get_json(force=True), bot)
        Application.process_update(update)
    return 'ok'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Codeforces Random Question Bot! \n"
        "For help type /help.\n Type /give <your_handle> <rating> and optionally specify a <tag> to filter questions.\n"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot provides you with a random Codeforces question suited for your skill level.\n\n"
        "Commands:\n"
        "/start - Starts the bot\n"
        "/help - List of commands and how to use them\n"
        "/give <your_handle> <rating> - Get a random question. Replace <your_handle> with your Codeforces username, <rating> with your preferred rating, and optionally specify a <tag> to filter questions.\n"
    )
    
async def get_random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text(
            "Please provide your Codeforces handle and the preferred rating (e.g., /give username 1700 tag[optional])."
        )
        return

    handle = context.args[0]
    try:
        rating = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid rating. Please provide a numerical value.")
        return

    tag = context.args[2] if len(context.args) > 2 else None

    try:
        user_response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}")
        user_data = user_response.json()
        if user_data['status'] != "OK":
            raise Exception(f"Error: {user_data['comment']}")
        try:
            rating = int(rating)
        except ValueError:
            await update.message.reply_text("Invalid rating. Please provide a numerical value.")
            return

        min_rating = 800 
        max_rating = 3600  
        
        if rating < min_rating or rating > max_rating:
            await update.message.reply_text(f"No problems found, please enter rating within the range {min_rating} - {max_rating}.")
            return 
        
        problems_response = requests.get("https://codeforces.com/api/problemset.problems")
        problems_data = problems_response.json()
        if problems_data['status'] != "OK":
            raise Exception("Failed to fetch problems from Codeforces.")
        
        problems = problems_data['result']['problems']
        filtered_problems = [
            problem for problem in problems 
            if problem.get('rating') == rating and (tag is None or tag in problem.get('tags', []))
        ]

        if not filtered_problems:
            await update.message.reply_text("No problems found with the given rating and tag.")
            return

        random_problem = random.choice(filtered_problems)
        problem_name = random_problem['name']
        problem_link = f"https://codeforces.com/problemset/problem/{random_problem['contestId']}/{random_problem['index']}"

        message = f"Here's a random Codeforces problem for {handle} with a rating {rating}:\n\n" \
                  f"Title: {problem_name}\n" \
                  f"Link: {problem_link}"
        await update.message.reply_text(message)

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {e}")
        
def main():
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("help", help_command))
    bot.add_handler(CommandHandler("give", get_random_question))

    bot.run_polling()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    main()
