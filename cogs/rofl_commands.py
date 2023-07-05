import asyncio
import random

import discord
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands

# import config
from Database import Database
from config import services_prices, commands_cooldown, icons_urls


async def add_rofl(ctx, member, seconds):
    try:
        rofl_role = discord.utils.get(ctx.guild.roles, name='Rofl')
        await member.add_roles(rofl_role)
        await asyncio.sleep(seconds)
        await member.remove_roles(rofl_role)
    except Exception as e:
        print(f'Ошибка в cogs/rofl_commands.py в функции add_rofl: {e}')


async def move_to_chulan(ctx, member):
    try:
        chulan = discord.utils.get(ctx.guild.channels, name='Чулан')
        if chulan is None:
            await ctx.guild.create_voice_channel(name='Чулан',
                                                 overwrites={
                                                     ctx.guild.default_role: discord.PermissionOverwrite(
                                                         view_channel=False)
                                                 })

        await member.move_to(chulan)

    except Exception as e:
        print(f'Ошибка в move_to_chulan: {e}')


class Rofl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='кто', description='Спросите меня что-то о ком-то, а я вам отвечу!')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __guess_who(self,
                          ctx,
                          what: Option(str, 'Что?', required=True)
                          ):
        """Угадайка"""

        try:
            await ctx.defer()
            users = [user for user in ctx.guild.members if user.bot is False]
            await ctx.respond(f'Я думаю, что **{what}** это {random.choice(users).mention} 😏',
                              allowed_mentions=discord.AllowedMentions(everyone=True))
        except Exception as e:
            print(f'Ошибка в cogs/rofl_commands в функции __guess_who: {e}')
            await ctx.respond('Произошла ошибка!')

    @slash_command(name='вероятность', description='Спросите меня о чем-то, я скажу, с какой вероятностью это правда!')
    @commands.cooldown(1, 1, commands.BucketType.user)
    async def __probability_who(self,
                                ctx,
                                what: Option(str, 'Что?', required=True)
                                ):
        """Угадайка ток с процентами"""

        try:
            await ctx.defer()
            await ctx.respond(f'Я уверен, что **{what}** на **{random.randint(0, 101)}%** 🤔')
        except Exception as e:
            print(f'Ошибка в cogs/rofl_commands в функции __probability_who: {e}')
            await ctx.respond('Произошла ошибка!')

    @slash_command(name='зарофлить',
                   description=f'Зарофлите кого-то по тарифу 1 минута - {services_prices["rofl_per_minute"]} гема')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __rofl(self,
                     ctx,
                     user: Option(discord.User, required=True),
                     time: Option(int, 'Время в минутах', required=True)
                     ):
        """Выдача роли "rofl_role_name" на время"""

        db = Database()
        try:
            await ctx.defer()

            for role in user.roles:
                if role.name == 'Rofl':
                    await ctx.respond(f'Пользователь **{user.name}** уже зарофлен!')
                    db.close_connection()
                    return

            cur_balance = db.get_balance(ctx.guild, ctx.author)
            price = time * services_prices["rofl_per_minute"]

            if cur_balance < price:
                await ctx.respond("На вашем счету недостаточно средств!", ephemeral=True)
            else:
                db.add_cash(ctx.guild, ctx.author, -price)

                embed = discord.Embed(title='**Это Rofls!**',
                                      description=f'Пользователь **{ctx.author.name}** зарофлил {user.mention} на **{time}** мин!',
                                      colour=discord.Colour.brand_red())
                embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                await ctx.respond(embed=embed)

                await add_rofl(ctx, user, time * 60)

            db.close_connection()

        except Exception as e:
            print(f'Ошибка в __rofl: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='чулан',
                   description=f'Отправьте кого-нить в Чулан за {services_prices["chulan"]} гемов')
    @commands.cooldown(1, commands_cooldown['chulan'], commands.BucketType.user)
    async def __chulan(self,
                       ctx,
                       user: Option(discord.User, required=True)
                       ):
        """Рофл команда отправки пользователя в канал с названием 'Чулан' """

        db = Database()
        try:
            await ctx.defer()
            if not user.voice:
                await ctx.respond(f'Пользователь **{user.name}** не находится в голосовом канале!', ephemeral=True)
                return

            cur_balance = db.get_balance(ctx.guild, ctx.author)
            price = services_prices["chulan"]

            if cur_balance < price:
                await ctx.respond("На вашем счету недостаточно средств!", ephemeral=True)
            else:
                db.add_cash(ctx.guild, ctx.author, -price)

                embed = discord.Embed(title='**Это Rofls!**',
                                      description=f'Пользователь **{ctx.author.name}** отправил {user.mention} в **Чулан**!',
                                      colour=discord.Colour.from_rgb(139, 69, 19))
                embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                await ctx.respond(embed=embed)

                await move_to_chulan(ctx, user)

            db.close_connection()

        except Exception as e:
            print(f'Произошла ошибка в chulan: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='0_0',
                   description=f'Станьте всевидящим и получите доступ к ...')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __vision(self,
                       ctx
                       ):
        """Рофл команда мута пользователя """
        db = Database()
        try:
            await ctx.defer()

            for role in ctx.author.roles:
                if role.name == 'Всевидящий':
                    await ctx.respond('Вы уже всевидящий!', ephemeral=True)
                    db.close_connection()
                    return

            cur_balance = db.get_balance(ctx.guild, ctx.author)
            price = services_prices["vision"]

            if cur_balance < price:
                await ctx.respond(f"Чтобы стать всевидящим нужно {price} 💎", ephemeral=True)

            else:
                # db.add_cash(ctx.guild, ctx.author, -price)

                embed = discord.Embed(title='**Ultra Omega Rofl was happened!**',
                                      description=f'\n@everyone\n\n**{ctx.author.name}** стал **ВСЕВИДЯЩИМ** 👁️!',
                                      colour=discord.Colour.nitro_pink())
                embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                embed.set_image(url=icons_urls['hellsing'])

                await ctx.respond(embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))
                await ctx.author.add_roles(discord.utils.get(ctx.guild.roles, name='Всевидящий'))

            db.close_connection()

        except Exception as e:
            print(f'Произошла ошибка в vision: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()


def setup(bot):
    bot.add_cog(Rofl(bot))
