import random
from collections import Counter

import discord
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands

from Database import Database
from config import commands_cooldown


class Dice(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            prediction = [int(item) for item in argument.split(sep=' ')]

            # Если в предикте больше 5 чисел
            if len(prediction) > 5:
                return None

            # Если пользователь ввёл предикт с одинаковыми числами ("1 1 2" или "3 4 3 5")
            # Или число в предикте меньше 1 / больше 6
            predict_count = Counter(prediction)
            for key, val in predict_count.items():
                if val != 1:
                    return None
                if key < 1 or key > 6:
                    return None

            return prediction
        except Exception as e:
            print(f'Ошибка в class Dice: {e}')
            return None


class Game(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='монетка', description='Подбросить монетку')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __coinflip(self,
                         ctx,
                         bet: Option(int, "Ставка", min_value=1, required=True),
                         prediction: Option(str, "Орёл или Решка", choices=['Орёл', 'Решка'], required=True)
                         ):
        """Подбрасывание монетки"""

        db = Database()
        try:
            await ctx.defer()
            user_balance = db.get_balance(ctx.guild, ctx.author)

            if user_balance < bet:
                await ctx.respond('У вас **недостаточно средств** для такой ставки!', ephemeral=True)

            else:
                result = random.choice(['Орёл', 'Решка'])

                if result == prediction:
                    db.add_cash(ctx.guild, ctx.author, bet)
                    db.add_statistics(ctx.guild, ctx.author, 'coin', 'win', bet)
                    embed = discord.Embed(title='**Бросок монетки** :coin: ',
                                          description=f'Предикт: **{prediction}**\nРезультат броска: **{result}**\nВыигрыш: **{bet}** 💎',
                                          colour=discord.Colour.brand_green())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    await ctx.respond(embed=embed)

                else:
                    db.add_cash(ctx.guild, ctx.author, -bet)
                    db.add_statistics(ctx.guild, ctx.author, 'coin', 'lose', -bet)
                    embed = discord.Embed(title='**Бросок монетки** :coin: ',
                                          description=f'Предикт: **{prediction}**\nРезультат броска: **{result}**\nПроебано: **{bet}** 💎',
                                          colour=discord.Colour.dark_red())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    await ctx.respond(embed=embed)

            db.close_connection()

        except Exception as e:
            print(f'Ошибка в cogs/game.py в функции __coinflip: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='кубик', description='Бросить кубик')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __dice(self,
                     ctx,
                     bet: Option(int, description="Ставка", min_value=1, required=True),
                     predict: Option(Dice,
                                     description="Прогноз (введите одно или несколько чисел от 1 до 6 через пробел)",
                                     required=True)
                     ):
        """Подбрасывание игральной кости"""

        db = Database()
        try:
            await ctx.defer()
            # Если некорректный предикт
            if predict is None:
                await ctx.respond(f'Вы ввели некорректный **прогноз**!', ephemeral=True)
                return

            user_balance = db.get_balance(ctx.guild, ctx.author)

            # Если недостаточно средств для ставки
            if user_balance < bet:
                await ctx.respond('У вас **недостаточно средств** для такой ставки!', ephemeral=True)
            # Если средства есть
            else:
                result = random.choice([1, 2, 3, 4, 5, 6])
                str_predict = ''.join(str(x) + ' ' for x in predict)
                # Если пользователь выиграл
                if result in predict:
                    loot = int(bet * 6 / len(predict)) - bet
                    db.add_cash(ctx.guild, ctx.author, loot)
                    db.add_statistics(ctx.guild, ctx.author, 'dice', 'win', loot)

                    embed = discord.Embed(title='**Бросок кубика** :game_die: ',
                                          description=f'Предикт: **{str_predict}**\nРезультат броска: **{result}**\nВыигрыш: **{loot}** 💎',
                                          colour=discord.Colour.brand_green())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    await ctx.respond(embed=embed)
                # Если проиграл
                else:
                    db.add_cash(ctx.guild, ctx.author, -bet)
                    db.add_statistics(ctx.guild, ctx.author, 'dice', 'lose', -bet)

                    embed = discord.Embed(title='**Бросок кубика**  :game_die: ',
                                          description=f'Предикт: **{str_predict}**\nРезультат броска: **{result}**\nПроебано: **{bet}** 💎',
                                          colour=discord.Colour.dark_red())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    await ctx.respond(embed=embed)

            db.close_connection()

        except Exception as e:
            print(f'Ошибка в cogs/game.py в функции __dice: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='русская_рулетка',
                   description='Сыграй в русскую рулетку! Получи x2 баланса или потеряй всё богатство!')
    @commands.cooldown(1, commands_cooldown['russian_roulette'], commands.BucketType.user)
    async def __russian_roulette(self, ctx):
        """Русская рулетка, пользователь проигрывает свой баланс или удваивает его"""

        db = Database()
        try:
            await ctx.defer()
            user_balance = db.get_balance(ctx.guild, ctx.author)
            if user_balance == 0:
                await ctx.respond(f'У тебя нету денег, дружище!', ephemeral=True)
            else:
                result = random.choice([0, 0, 1, 0, 0, 0])
                if result:
                    embed = discord.Embed(title='**Omega Rofl was happened**',
                                          description=f'@everyone\n{ctx.author.name} сыграл в Русскую Рулетку и **потерял все свои сбережения**!',
                                          colour=discord.Colour.dark_red())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    db.add_cash(ctx.guild, ctx.author, -user_balance)
                    await ctx.respond(embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))

                else:
                    embed = discord.Embed(title='**Rofl was happened**',
                                          description=f'@everyone\n{ctx.author.name} сыграл в Русскую Рулетку и **увеличил свой баланс в два раза**!',
                                          colour=discord.Colour.green())
                    embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                    db.add_cash(ctx.guild, ctx.author, + user_balance)
                    await ctx.respond(embed=embed, allowed_mentions=discord.AllowedMentions(everyone=True))

            db.close_connection()
        except Exception as e:
            db.close_connection()
            print(f'Ошибка в cogs/game.py: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)


def setup(bot):
    bot.add_cog(Game(bot))
