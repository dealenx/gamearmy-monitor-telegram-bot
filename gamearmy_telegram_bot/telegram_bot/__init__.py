# import json
# import logging
# import re
#
# import telegram
# from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
#
# import os
# from dotenv import load_dotenv
#
# from gs4u_telegram_bot import gs4u_server_players
#
# load_dotenv()
# TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# CHAT_ID=os.getenv("CHAT_ID")
#
#
#
# SERVER_GS4U_URL = os.getenv("SERVER_GS4U_URL")
#
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# # set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
#
# logger = logging.getLogger(__name__)
#
#
# # Define a `/start` command handler.
# async def start(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     match = re.search(r'/(\d+)\.', SERVER_GS4U_URL)
#     id = None
#     if match:
#         id = match.group(1)
#         print(f"ID из ссылки: {id}")
#     else:
#         print("ID не найден в ссылке.")
#     """Send a message with a button that opens a the web app."""
#     await update.message.reply_text(
#         "Нажмите на кнопку для мониторинга Ниже",
#         reply_markup=telegram.ReplyKeyboardMarkup.from_button(
#             telegram.KeyboardButton(
#                 text="Мониторинг",
#                 web_app=telegram.WebAppInfo(url=f"https://www.gs4u.net/en/webmod/frame-map:120;splr:1;players:210;mfs:100;mac:6d6d6d;mahc:8f8f8f;sna:d59120;mbg:1d1d1d;bg:4d4d4d;fg:ffffff;snb:666666;itc:aaaaaa;shs:1;/s/{id}.html"),
#             )
#         ),
#     )
#
#
# # Handle incoming WebAppData
# async def web_app_data(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Print the received data and remove the button."""
#     # Here we use `json.loads`, since the WebApp sends the data JSON serialized string
#     # (see webappbot.html)
#     data = json.loads(update.effective_message.web_app_data.data)
#     await update.message.reply_html(
#         text=(
#             f"You selected the color with the HEX value <code>{data['hex']}</code>. The "
#             f"corresponding RGB value is <code>{tuple(data['rgb'].values())}</code>."
#         ),
#         reply_markup=telegram.ReplyKeyboardRemove(),
#     )
#
# async def show_current_info(update: telegram.Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     current_players = gs4u_server_players.get_server_players(SERVER_GS4U_URL)
#     print("current_players", current_players)
#     info_message = 'На сервере нет игроков'
#
#     if len(current_players) > 0:
#         info_message = f"На сервере сейчас следующие игроки: {', '.join(current_players)}"
#
#     # Обновить таблицу игроков
#     gs4u_server_players.update_player_table(current_players)
#     await update.message.reply_text(info_message)
#
# def run_bot():
#     # Create the Application and pass it your bot's token.
#     application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
#
#     application.add_handler(CommandHandler("start", start))
#     application.add_handler(CommandHandler("info", show_current_info))
#     application.add_handler(MessageHandler(filters.StatusUpdate.WEB_APP_DATA, web_app_data))
#
#     # Run the bot until the user presses Ctrl-C
#     application.run_polling(allowed_updates=telegram.Update.ALL_TYPES)
#
#
# if __name__ == '__main__':
#     run_bot()