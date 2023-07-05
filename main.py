import os

import discord

import config

# intents = disnake.Intents.all()

bot = discord.Bot(
    command_prefix='/',
    intents=discord.Intents.all(),
    activity=discord.Game('Dota 2',
                          status=discord.Status.online)
)

if __name__ == '__main__':
    for filename in os.listdir("cogs"):
        if filename.endswith(".py"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    # load_dotenv(find_dotenv())
    try:
        bot.run(config.BOT_TOKEN)
    except Exception as e:
        print(f'Произошла ошибка в main.py: {e}')
