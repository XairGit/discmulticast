#
# discmulticast.py
#
# discord multicast - Multicasting messages on Discord
# Copyright (c) 2018 Kaidan (fishstacks@protonmail)
#
# discord multicast is available free of charge under the terms of the ISC
# license. You are free to redistribute and/or modify it under those
# terms. It is distributed in the hopes that it will be useful, but
# WITHOUT ANY WARRANTY. See the LICENSE file for more details.

import logging
import os
from collections import defaultdict
import discord
import chromalog
import toml

# Setup for logging
# Log output format
LOG_FORMAT = '[%(levelname)s] %(asctime)s %(name)s: %(message)s'
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Use chromalog for coloured output
chromalog.basicConfig(
    level=logging.INFO, format=LOG_FORMAT, datefmt=DATE_FORMAT)
logger = logging.getLogger('discmulticast')
# Shut the discord module up
logging.getLogger('discord').setLevel(logging.ERROR)
logging.getLogger('websockets').setLevel(logging.ERROR)

# Load config
logger.info('Loading config')
config = toml.load(os.environ['DISCMULTI_CONFIG'])
destination_channels = config['dest_ids']


# Create bot class
class Bot(discord.Client):
    """Class implementing bot functionality"""

    def __init__(self):
        # Stores the ID of a message from a source channel as key and a list of delete
        # coroutines corresponding to messages in destination channels as values
        # Used to multicast message deletes
        self.message_mapping = defaultdict(list)
        super().__init__()

    def check(event_handler):
        """
        Used as a decorator to check if the bot should act on received events
        """

        async def do_checks(self, msg, *args):
            if msg.channel.id != config['src_id'] or msg.author != self.user:
                # Ignore input we don't care about
                return
            else:
                await event_handler(self, msg)

        return do_checks

    async def on_ready(self):
        """
        Event fired when bot is connected to discord websocket
        Currently just used to print status information
        """
        logger.info(
            f'Starting bot as user {self.user.name}#{self.user.discriminator}')
        logger.info(
            f'Listening for messages in \"#{self.get_channel(config["src_id"]).name}\" ({config["src_id"]})'
            f' and multicasting them to {len(config["dest_ids"])} other channels'
        )

    @check
    async def on_message(self, msg):
        """
        Event fired every time the bot sees a new message
        Used to send messages to destination channels
        """
        logger.info(f'Got message with ID {msg.id}, multicasting')
        for channel_id in destination_channels:
            channel = self.get_channel(channel_id)
            async with channel.typing():
                dest_message = await channel.send(msg.content)
                # Store delete coroutines directly
                # because we can't do msg ID lookups without bot account
                self.message_mapping[msg.id].append(dest_message.delete)

    @check
    async def on_message_delete(self, msg):
        """
        Event fired when a message is deleted

        May not be triggered if message is not in local cache
        which happens in large guilds or with old messages

        Used to check for deletes and to broadcast them to destination channels
        """
        logger.info(f"Got delete event for message ID {msg.id}, multicasting")
        for delete_message_func in self.message_mapping[msg.id]:
            async with msg.channel.typing():
                await delete_message_func()
        del self.message_mapping[msg.id]


# Start discord client
logger.info('Creating client and connecting to Discord API')
bot = Bot()
# Check if we need to run as a selfbot
if config['is_selfbot']:
    logger.warning('Running as selfbot - THIS CAN GET YOU BANNED')
    bot.run(config['discord_token'], bot=False)
else:
    logger.info('Running as regular bot')
    bot.run(config['discord_token'])
