import configparser
import csv
import logging
import os
import re
from pathlib import Path

import questionary
from telethon import TelegramClient, events

logging.basicConfig(
    format='[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger(__name__)


def get_creds():
    if os.path.exists('config.ini'):
        config = configparser.ConfigParser()
        config.read('config.ini')
        api_id = config['TelegramApi']['api_id']
        api_hash = config['TelegramApi']['api_hash']
    else:
        api_id = int(questionary.password('Api ID:').ask())
        api_hash = questionary.password('Api hash:').ask()

        config = configparser.ConfigParser()
        config['TelegramApi'] = {'api_id': api_id, 'api_hash': api_hash, }
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
    return api_id, api_hash


def process_channel_names():
    channel_names = []
    with open('channels_list.txt') as file:
        for line in file:
            name = re.search(r'https://t.me/(.*)', line).group(1)
            channel_names.append(name)
    return channel_names


async def write_to_file(row_data, file_name):
    data_file = Path(f'{file_name}.csv')
    if not data_file.is_file():
        with open('data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["text", "hash_tags", "phones", 'credit_cards'])
    else:
        with open('data.csv', 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row_data)


client = TelegramClient('new_session', *get_creds())
client.start()
logger.info('Bot started')


async def write_new_message_handler(event):
    try:
        # may be used as an option
        # hash_tags = re.findall(r'#\w+', event.text)
        # phones = re.findall(r'\+d{12,15}(?<=\d)|\d{10,13}(?<=\d)', event.text)
        # credit_cards = re.findall(r'[\d\s]{16,21}(?<=\d)', event.text)

        message = event.text
        sender = await event.get_sender()
        sender_name = (
            f'{sender.username}: '
            f'{sender.first_name or ""} {sender.last_name or ""}'.strip()
        )

        data_to_write = [sender, message]
        logger.info(data_to_write)

        await write_to_file(data_to_write, sender_name)
    except TypeError:
        logger.error(f'Something went wrong with the message: {event.text}')


for channel_name in process_channel_names():
    client.add_event_handler(write_new_message_handler, events.NewMessage(channel_name))


client.run_until_disconnected()
