# Discmulticast - multicasting discord messages
This bot was created to allow one-too-many messages on discord, meaning you can send a single message to one channel and have it automatically sent to many others. It is currently early in development and more features are planned, but the good news is it's usable right now.

It should work on both windows and linux, however windows support is untested.

## Requirements
The bot requires the latest version of python to be installed and uses the latest version of discord.py, plus some other libraries. Everything required can be easily installed using `pip` via `pip install -r requirements.txt`

## Running and configuration
The bot largely operates based on a TOML configuration file, for an example see the [example config](example_config.txt).

The config file needs to be specified in the `DISCMULTI_CONFIG` environment variable in order for it to be loaded by the bot.
this means you need to run the bot like this:
```
DISCMULTI_CONFIG=config.toml python discmulticast.py
```
The above should work for both windows and linux.

## Wanted features list
- [x] Multicast message edits and deletes
- [ ] Allow for multiple source addresses
- [ ] Monitor messages from multiple users in source channel, not just bot user

## License
This program is released under the terms of the ISC license, details can be found in the [license file](LICENSE.txt).
