import random

import discord
from discord.ext import commands

import config
from Database import Database


async def roles_update(guild):
    """Обновляет у участников серверов, на которых работает бот"""

    basic_roles = config.basic_roles  # Получаем из конфига роли, которые будем проверять

    # Проверяем наличие ролей на сервере guild

    required_roles = []
    # Итерируемся по словарю с ролями из конфига
    for name, color in basic_roles.items():

        role = discord.utils.get(guild.roles, name=name)  # Получаем роль

        # Если роли нет, создаем новую
        if role is None:
            role = await guild.create_role(name=name, colour=discord.Colour.from_rgb(*color), hoist=True)
            print(f'Created new role "{name}" at {guild.name}')

        # Добавляем роль в список ролей, которые потом будем проверять у пользователя
        if name == 'Radiant' or name == 'Dire' or name == 'Neutral':
            required_roles.append(role)

    # Проверяем роли у пользователя, если нету одной из, добавляем рандомную
    for user in guild.members:
        if len(list(set(required_roles) & set(user.roles))) == 0:
            await user.add_roles(random.choice(required_roles))


# def database_update(database: Database, users) -> None:
#     """Выполняет обновление базы данных"""
#     for user in users:
#         try:
#             database.add_user(user=user, cash=50)
#         except Exception as e:
#             print(f'Произошла ошибка в database_update: {e}')


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        """Выполняется при запуске бота"""
        print(f'Бот {self.bot.user} запущен!')
        db = Database()
        db.update(self.bot.guilds)
        db.close_connection()
        print('База данных обновлена!')
        for guild in self.bot.guilds:
            await roles_update(guild)
            print(f'Роли на сервере {guild} обновлены!')

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx, error):
        """Ловим ошибки разных модулей"""

        # Application command on cooldown
        if isinstance(error, commands.errors.CommandOnCooldown):
            days = error.retry_after // (24 * 3600)
            hour = (error.retry_after % (24 * 3600)) // 3600
            minute = ((error.retry_after % (24 * 3600)) % 3600) // 60
            seconds = round((((error.retry_after % (24 * 3600)) % 3600) % 60), 2)

            await ctx.respond(f'**Кулдаун {int(days)}д. {int(hour)}ч. {int(minute)}м. {int(seconds)}с.**',
                              ephemeral=True)

        # Permission denied
        elif isinstance(error, commands.errors.NotOwner):
            await ctx.respond(f'У вас **нет прав** для использования этой команды! 🤡', ephemeral=True)

        # Прочие ошибки
        else:
            print(f'Ошибка: {error}')

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        print(f'Бот подключился к серверу {guild}')
        db = Database()
        db.update([guild])
        db.close_connection()
        print(f'Сервер {guild} добавлен в БД')
        await roles_update(guild)
        print(f'Роли на сервере {guild} обновлены!')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Добавляем нового пользователя в БД"""
        guild = member.guild
        print(f'Новый пользователь {member} прибыл на сервер {guild}')
        db = Database()
        db.add_user(guild, member)
        db.close_connection()
        # print('База данных обновлена!')
        await roles_update(guild)
        print(f'Роль {member} обновлена!')

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        """Удаляем пользователя из БД"""
        guild = member.guild
        print(f'Пользователь {member} покинул сервер {guild}')
        db = Database()
        db.remove_user(guild, member)
        db.close_connection()
        # print('База данных обновлена!')


def setup(bot):
    bot.add_cog(Events(bot))
