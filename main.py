import telegram
from telegram.ext import Application, CommandHandler, ContextTypes, Updater
from telegram import Update
import requests
import random
import asyncio
import os

TOKEN = '6961128694:AAEYun_Y4hjhOtKFg-GZip4p1lbSMkUTG2c'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome to Codeforces Random Question Bot! \n"
        "For help type /help.\n Type /give <your_handle> <rating> to get a random Codeforces question suited for your skill level."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "This bot provides you with a random Codeforces question suited for your skill level.\n\n"
        "Commands:\n"
        "/start - Starts the bot\n"
        "/help - List of commands and how to use them\n"
        "/give <your_handle> <rating> - Get a random question. Replace <your_handle> with your Codeforces username and <rating> with your preferred rating.\n"
        "/tags <question tag> - Get a random question with entered tag. "
    )

async def get_tag(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text(
            "Please enter the tags for question."
        )
        return
    
    tag = context.args[0]
    response = requests.get(f'https://codeforces.com/api/problemset.problems?tags={tag}')
    data = response.json()
    try:
        tag = str(tag)
    except ValueError:
        await update.message.reply_text("Invalid tag. Please provide a valid tag.")
        return

    if data['status'] != 'OK':
        update.message.reply_text('Error fetching problems.')
        return

    problems = data['result']['problems']
    if not problems:
        update.message.reply_text(f'No problems found for tag: {tag}')
        return

    problem_list = "\n".join([f"{p['name']} (https://codeforces.com/contest/{p['contestId']}/problem/{p['index']})" for p in problems[:5]])
    update.message.reply_text(f'Problems with tag {tag}:\n{problem_list}')


async def get_random_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text(
            "Please provide your Codeforces handle and the preferred rating (e.g., /give username 1700)."
        )
        return

    handle, rating = context.args

    try:
        response = requests.get(f"https://codeforces.com/api/user.info?handles={handle}")
        if response.status_code != 200:
            raise Exception("Failed to fetch user data from Codeforces.")

        user_info = response.json()
        if user_info['status'] != "OK":
            raise Exception(f"Error: {user_info['comment']}")

        try:
            rating = int(rating)
        except ValueError:
            await update.message.reply_text("Invalid rating. Please provide a numerical value.")
            return

        min_rating = 800 
        max_rating = 3600
        response = requests.get("https://codeforces.com/api/problemset.problems")
        if response.status_code != 200:
            raise Exception("Failed to fetch problems from Codeforces.")

        data = response.json()
        problems = [
            problem for problem in data['result']['problems'] if 'rating' == rating
        ]

        if rating < min_rating or rating > max_rating:
            await update.message.reply_text(f"No problems found please enter a rating within the range {min_rating}-{max_rating}.")
            return

        random_problem = random.choice(problems)
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
    bot.add_handler(CommandHandler("tags", get_tag))

    bot.run_polling()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    main()
