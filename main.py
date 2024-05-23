import telegram
from telegram.ext import Updater, CommandHandler
import requests
import random

TOKEN = '6961128694:AAEIo_uOkefBc5ihGnWvPmocmLLY21p9Vgw'
bot = telegram.Bot(token=TOKEN)

def start(update, context):
    update.message.reply_text("Welcome to Codeforces Random Question Generator Bot! Use /random <tag(s)> <rating> to get a random problem.")

def random_problem(update, context):
    try:
        tags = context.args[:-1]
        rating = int(context.args[-1])

        url = f"https://codeforces.com/api/problemset.problems?tags={';'.join(tags)}&minRating={rating}&maxRating={rating}"
        response = requests.get(url)
        data = response.json()

        if data["status"] == "OK":
            problems = data["result"]["problems"]
            if problems:
                random_problem = random.choice(problems)
                problem_name = random_problem["name"]
                problem_url = f"https://codeforces.com/problemset/problem/{random_problem['contestId']}/{random_problem['index']}"
                update.message.reply_text(f"Random problem: {problem_name}\nLink: {problem_url}")
            else:
                update.message.reply_text("No problems found with the given parameters.")
        else:
            update.message.reply_text("Failed to fetch problems. Please try again later.")
    except (IndexError, ValueError):
        update.message.reply_text("Usage: /give <tag(s)> <rating>")

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("give", random_problem))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
