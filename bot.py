"""Main file with the bot's logic."""

import asyncio
import json
import logging
import os
import sys

import aioschedule
import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import BotCommand
from aiogram.utils.exceptions import WrongFileIdentifier
from google.cloud import dialogflow

import messages

DEVELOP = os.environ.get("DEVELOP", False)

# Telegram configs
API_HOST = os.getenv("API_HOST")
BOT_TOKEN = os.getenv("BOT_TOKEN")
APP_NAME = os.getenv("APP_NAME")
WEBHOOK_HOST = f"https://{APP_NAME}.herokuapp.com"
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEBAPP_HOST = "0.0.0.0"
WEBAPP_PORT = int(os.environ.get("PORT", "5000"))

# Dialogflow configs
CREDENTIAL_FILE = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
try:
    PROJECT_ID = json.load(open(CREDENTIAL_FILE))["project_id"]
except FileNotFoundError:
    logging.fatal("Credential file for Dialogflow not found")
    sys.exit(-1)

# Dialogflow init
session_client = dialogflow.SessionsClient()
session = session_client.session_path(PROJECT_ID, "session")

# Bot init
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
telegram_id = 0
language_code = "ru"

# Logging init
logging.basicConfig(level=logging.INFO)


class Information(StatesGroup):
    """States of bot."""

    waiting_for_user_language = State()
    waiting_for_user_name = State()
    waiting_for_pet_name = State()
    busy = State()


async def set_commands(tbot: Bot):
    """Add commands to MENU button. Also, can be done via BotFather."""
    commands = [
        BotCommand(command="/start", description="Включить робота"),
    ]
    await tbot.set_my_commands(commands)


async def set_article_is_sent(article_id: int, user_id: int):
    """Send POST to API to set article sent to user id_telegram."""
    url = f"{API_HOST}/users/set_sent"
    data = {"user_id": user_id, "article_id": article_id}
    request = requests.post(url=url, json=data)
    return request


async def save_user_to_db(
    id_telegram: int, username: str, pet_name: str, user_language: str
):
    """POST user data to API."""
    url = f"{API_HOST}/users/"
    data = {
        "telegram_id": id_telegram,
        "username": username,
        "pet_name": pet_name,
        "language_code": user_language,
    }
    request = requests.post(url=url, json=data)
    return request


async def get_user(id_telegram: int):
    """GET user data from API by telegram_id."""
    url = f"{API_HOST}/users/{id_telegram}"
    request = requests.get(url=url, json=True)
    return request


async def get_all_users_ids():
    """GET all users telegram ids from API."""
    url = f"{API_HOST}/users/"
    request = requests.get(url=url, json=True)
    return request


async def get_articles():
    """GET all articles from API that much user language."""
    url = f"{API_HOST}/articles/"
    request = requests.get(url=url, json=True)
    return request


async def send_scheduled_message(
    id_telegram: int, user_id: int, article_id: int, img_url: str, content: str
):
    """Send scheduled message to user and set a message as sent."""
    await bot.send_photo(chat_id=id_telegram, photo=img_url, caption=content)
    await set_article_is_sent(article_id=article_id, user_id=user_id)
    print("sent article", article_id)


async def prepare_message():
    """Prepare message for sending."""
    users_ids = await get_all_users_ids()
    articles = await get_articles()
    if articles.status_code == 200 and users_ids.status_code == 200:
        for user in users_ids.json():
            for article in articles.json():
                list_of_telegram_ids = [
                    i["telegram_id"] for i in article["sent_to_user"]
                ]
                if (
                    user["telegram_id"] not in list_of_telegram_ids
                    and article["language_code"] == user["language_code"]
                ):
                    try:
                        await send_scheduled_message(
                            id_telegram=user["telegram_id"],
                            user_id=user["id"],
                            article_id=article["id"],
                            img_url=article["image_url"],
                            content=article["text"],
                        )
                        break
                    except WrongFileIdentifier as e:
                        print(f"Error: {e}")
                        break
            else:
                await bot.send_message(
                    chat_id=user["telegram_id"],
                    text=messages.dialogs[user["language_code"]]["no_articles"],
                )


async def scheduler():
    """Scheduler for sending messages."""

    # aioschedule.every(10).seconds.do(prepare_message)
    # keep in mind that this is remote server time
    aioschedule.every().day.at("17:00").do(prepare_message)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def on_startup(dispatcher):
    """Startup function."""
    asyncio.create_task(scheduler())
    if not DEVELOP:
        await bot.set_webhook(WEBHOOK_URL)


async def on_shutdown(dispatcher):
    """Shutdown function."""
    await bot.delete_webhook()


@dp.message_handler(commands=["start"])
async def send_welcome(message: types.Message):
    """
    This handler will be called when user sends `/start` command.
    Check if user already registered in database.
    Define preferred language. If language is not set, ask user to choose language.
    """

    # add commands to MENU button
    await set_commands(bot)

    global telegram_id
    telegram_id = int(message.from_user.id)
    # Check if user is in database already.
    user_api = await get_user(id_telegram=telegram_id)

    if user_api.status_code == 404:
        # Try to get user language from telegram settings.
        global language_code
        language_code = message.from_user.locale.language
        if language_code in (messages.UA, messages.RU, messages.EN):
            await message.answer(messages.dialogs[language_code]["start"])
            await Information.waiting_for_user_name.set()
        else:
            await message.answer(messages.dialogs[messages.EN]["intro"])
            keyboard = types.ReplyKeyboardMarkup(
                resize_keyboard=True, one_time_keyboard=True
            )
            for name in (messages.UKR, messages.RUS, messages.ENG):
                keyboard.insert(name)
            await message.answer("What language will we talk?", reply_markup=keyboard)
            await Information.waiting_for_user_language.set()

    elif user_api.status_code == 200:
        # If user is in DB
        # TODO доработать сообщение и логику
        await message.answer(messages.dialogs[user_api.json()["language_code"]]["busy"])
        await Information.busy.set()

    else:
        # If DB is not available
        await message.answer(f"Ошибка. Error {user_api.status_code}")


@dp.message_handler(content_types=["text"], state=Information.busy)
async def chat_user(message: types.Message):
    """User may chat with bot. Bot uses Google Dialogflow library."""
    user_api = await get_user(id_telegram=message.from_user.id)
    text_input = dialogflow.TextInput(
        text=message.text, language_code=user_api.json()["language_code"]
    )
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    if response.query_result.fulfillment_text:
        await message.answer(response.query_result.fulfillment_text)
    else:
        await message.answer(
            messages.dialogs[user_api.json()["language_code"]]["unknown_command"]
        )


@dp.message_handler(state=Information.waiting_for_user_language)
async def user_language_set(message: types.Message, state: FSMContext):
    """
    Get user language from user input. Prepare for next state to get user_name.
    """
    global language_code
    # If user input is not in list of languages, ask user to choose language.
    if message.text.capitalize().strip() not in (
        messages.UKR,
        messages.RUS,
        messages.ENG,
    ):
        await message.answer(messages.dialogs[messages.EN]["choose_lang"])
        return

    if message.text.capitalize().strip() == messages.UKR:
        language_code = messages.UA
    elif message.text.capitalize().strip() == messages.RUS:
        language_code = messages.RU
    else:
        language_code = messages.EN

    await state.update_data(language_code=language_code)
    await message.answer(messages.dialogs[language_code]["ask_name"])
    await Information.waiting_for_user_name.set()


@dp.message_handler(state=Information.waiting_for_user_name)
async def user_name_set(message: types.Message, state: FSMContext):
    """
    Get username from user input. Prepare for next state to get pet_name.
    """
    if not message.text.strip().isalpha():
        await message.answer(messages.dialogs[language_code]["wrong_name"])
        return
    username = message.text.strip().capitalize()

    await state.update_data(username=username)
    await message.answer(f"{username}{messages.dialogs[language_code]['ask_pet_name']}")
    await Information.waiting_for_pet_name.set()


@dp.message_handler(state=Information.waiting_for_pet_name)
async def pet_name_set(message: types.Message, state: FSMContext):
    """Get pet name from user."""
    if not message.text.strip().isalpha():
        await message.answer(messages.dialogs[language_code]["wrong_name"])
        return
    pet_name = message.text.strip().capitalize()

    await state.update_data(pet_name=pet_name)

    user_data = await state.get_data()
    await save_user_to_db(
        telegram_id, user_data["username"], user_data["pet_name"], language_code
    )

    await message.answer(messages.dialogs[language_code]["search"])
    await asyncio.sleep(3)
    await message.answer(
        f"{user_data['username']}{messages.dialogs[language_code]['found']}"
    )
    await message.answer(messages.dialogs[language_code]["personal"])
    await Information.busy.set()


if __name__ == "__main__":
    if DEVELOP:
        executor.start_polling(dispatcher=dp, skip_updates=True, on_startup=on_startup)
    else:
        executor.start_webhook(
            dispatcher=dp,
            webhook_path=WEBHOOK_PATH,
            on_startup=on_startup,
            on_shutdown=on_shutdown,
            skip_updates=True,
            host=WEBAPP_HOST,
            port=WEBAPP_PORT,
        )
