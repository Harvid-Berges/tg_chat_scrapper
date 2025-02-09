import asyncio
import csv
import pytz
import os

from cs50 import SQL
from datetime import datetime, timedelta
from telethon.tl.types import InputPeerChannel, InputPeerChat, InputPeerUser
from telethon import TelegramClient, events


async def scrap_group(group: str, keywords: str):


async def main():
    
    # Setup api, hash, create client and connect
    api_id = MY_API_ID
    api_hash = MY_API_HASH
    session_name = "h"
    client = TelegramClient(session_name, api_id, api_hash)
    
    chats = csv_to_list("chats_db.csv")
    
    
    # Get chat entity from user input
    chat_input = input("Enter chat name or ID: ")
    try:
        chat = await client.get_entity(chat_input)
    except ValueError:
        print("Chat not found. Make sure you're a member of the chat/channel.")
        await client.disconnect()
        return

    # Calculate time 8 hours ago in UTC
    start_time = datetime.now(pytz.utc) - timedelta(hours=8)
    
    print(f"Retrieving messages since {start_time.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    
    # Collect messages
    messages = []
    async for message in client.iter_messages(
        chat,
        offset_date=start_time,
        reverse=True  # Get messages in chronological order
    ):
        messages.append(message)

    # Print results
    print(f"\nFound {len(messages)} messages in the last 8 hours:")
    for msg in messages:
        message_time = msg.date.astimezone(pytz.utc)
        text = msg.text or "<media message>"
        print(f"{message_time.strftime('%Y-%m-%d %H:%M:%S %Z')}: {text}")

    await client.disconnect()

async def csv_to_list(filename: str)->list:
    """
    Parses a CSV file and returns its content as a list of lists.
    Each inner list represents a row in the CSV file.
    """
    data = []
    try:
        with open(filename, 'r', newline='') as csvfile:
            csv_reader = csv.reader(csvfile) 
            for row in csv_reader:
                data.append(row)
        return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == '__main__':
    import asyncio
    import getpass
    asyncio.run(main())