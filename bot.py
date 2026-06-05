import os
from telegram.ext import Application

TOKEN = os.environ.get("BOT_TOKEN")

def main():
    app = Application.builder().token(TOKEN).build()
    app.run_polling()

if __name__ == "__main__":
    main()
