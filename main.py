import asyncio
import csv
from datetime import datetime, timedelta
import logging
import os
import re
from cs50 import SQL
import pytz
from telethon import TelegramClient

MY_API_ID = "xxx"  # Your api id
MY_API_HASH = "xxx"  # Your api hash
MY_SESSION_NAME = "xxx"  # Your session name
MAX_HOURS = 8  # Hours to retrieve msgs
USER_NONREPETITION = True  # Set true for only getting one message per user
INTERCHAT_NONREPETITION = True  # Set true for making the nonrepetition across chats


# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


async def main():

    # Setup api, hash, create client and connect
    api_id = MY_API_ID
    api_hash = MY_API_HASH
    session_name = MY_SESSION_NAME

    try:
        async with TelegramClient(session_name, api_id, api_hash) as client:
            await client.start()

            chats = await csv_to_list("chats.csv")
            keywords = await csv_to_list("keywords.csv")

            print(chats[0])
            print(type(chats[0]))
            if chats is None or keywords is None:
                logging.error("Could not load chats or keywords. Exiting.")
                return

            messages = []

            for chat in chats:
                if INTERCHAT_NONREPETITION:
                    messages = await scrap_chat(chat, keywords, client, messages)
                else:
                    messages.append(scrap_chat(chat, keywords, client))

            for message in messages:
                print(message.text)
                print()
            print(len(messages))
            await client.disconnect()

    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)


async def scrap_chat(
    chat_input: str, keywords: str, client: TelegramClient, messages=None
):
    """
    Scraps messages from a Telegram chat/channel.

    Args:
        chat_input (str): The chat ID or username.
        keywords (list): A list of keywords to search for.
        client (TelegramClient): The Telegram client instance.
        messages (list, optional): A list to append messages to. Defaults to None.

    Returns:
        list: A list of messages containing keywords.
    """
    if messages is None:
        messages = []

    # Get chat entity
    try:
        chat = await client.get_entity(chat_input)
    except ValueError:
        print(
            f"Chat <<{chat_input}>> not found. Make sure you're a member of the chat/channel."
        )
        return messages

    # Calculate time 8 hours ago in UTC
    start_time = datetime.now(pytz.utc) - timedelta(hours=MAX_HOURS)

    print(f"Retrieving messages since {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")

    # Store sender IDs in a set
    existing_sender_ids = {
        message.sender_id for message in messages if message.sender_id
    }

    # Create search pattern
    keyword_pattern = re.compile(
        "|".join(re.escape(keyword) for keyword in keywords), re.IGNORECASE
    )

    # Collect messages
    async for message in client.iter_messages(
        chat,
        offset_date=start_time,
        reverse=False,  # Set true for getting messages in chronological order
    ):
        if USER_NONREPETITION:
            if (
                message.sender_id
                and message.sender_id not in existing_sender_ids
                and keyword_pattern.search(message.text)
            ):  # Check if the message contains keywords using regex
                messages.append(message)
                existing_sender_ids.add(message.sender_id)  # Add sender ID to the set
        else:
            if keyword_pattern.search(message.text):
                messages.append(message)

    # Print results
    print(
        f"\nFound {len(messages)} messages on <<{chat_input}>> in the last {MAX_HOURS} hours."
    )

    return messages


async def csv_to_list(filename: str) -> list:
    """
    Parses a CSV file and returns its content as a list of lists.
    Each inner list represents a row in the CSV file.
    """
    data = []
    try:
        with open(filename, "r", newline="") as csvfile:
            csv_reader = csv.reader(csvfile)
            for row in csv_reader:
                data.append(row)
        return data
    except FileNotFoundError:
        logging.error("Error: File %s not found.", filename)
        return None
    except csv.Error as e:
        logging.error("CSV error: %s", e)
        return None
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        return None


if __name__ == "__main__":
    asyncio.run(main())
