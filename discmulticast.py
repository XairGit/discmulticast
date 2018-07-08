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
from os import environ
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
config = toml.load(environ['DISCMULTI_CONFIG'])
destination_channels = config['dest_ids']

# Create bot class
class Bot(discord.Client):
    """Class implementing bot functionality"""

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
            f' and multicasting them to {len(config["dest_ids"])} other channels')

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
                await channel.send(msg.content)

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
