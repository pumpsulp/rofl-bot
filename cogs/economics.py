import discord
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands

# import config
from Database import Database
from config import commands_cooldown, kit_prices, icons_urls


def get_user_statistics(ctx, user):
    """Считает статистику пользователя в монетке, кубике и общую"""

    db = Database()
    try:
        coin_win, coin_lose, coin_networth = db.get_statistics(ctx.guild, user, 'coin')
        dice_win, dice_lose, dice_networth = db.get_statistics(ctx.guild, user, 'dice')

        coin_winrate = round((coin_win / (coin_lose + coin_win + 0.0001)) * 100, 1)
        dice_winrate = round((dice_win / (dice_lose + dice_win + 0.0001)) * 100, 1)
        total_winrate = round((dice_win + coin_win) / (dice_win + coin_win + dice_lose + coin_lose + 0.0001) * 100, 1)

        db.close_connection()
        return coin_win, coin_lose, coin_networth, coin_winrate, dice_win, dice_lose, dice_networth, dice_winrate, total_winrate

    except Exception as e:
        print(f'Ошибка в cogs/economics в функции get_user_statistics: {e}')
        db.close_connection()
        return None


class Economics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='баланс', description='Проверка баланса')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __balance(self,
                        ctx,
                        member: Option(discord.Member, "Пользователь", required=True) = None
                        ):
        """Команда проверки баланса пользователя."""

        db = Database()
        try:
            await ctx.defer(ephemeral=True)
            # Если не указан пользователь, то выводим баланс того, кто вызвал команду
            if member is None:
                await ctx.respond(embed=discord.Embed(
                    description=f"""Баланс пользователя **{ctx.author.name}** составляет **{db.get_balance(ctx.guild, ctx.author)}** 💎""",
                    colour=discord.Colour.green()),
                    ephemeral=True)
            # В противном случае показываем баланс указанного пользователя
            else:
                await ctx.respond(embed=discord.Embed(
                    description=f"""Баланс пользователя **{member.name}** составляет **{db.get_balance(ctx.guild, member)}** 💎""",
                    colour=discord.Colour.green()),
                    ephemeral=True)

            db.close_connection()

        except Exception as e:
            print(f'Ошибка в cogs/economics.py в функции __balance: {e}')
            db.close_connection()

    @slash_command(name='передать', description='Передача деняк')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __give(self,
                     ctx,
                     member: Option(discord.Member, "Имя пользователя", required=True),
                     amount: Option(int, "Деньги", required=True)
                     ):
        """Перевод деняк. member, amount - кому и кол-во."""

        db = Database()
        try:
            await ctx.defer()
            # Если указанная пользователем сумма отрицательная
            if amount <= 0:
                gif = 'https://images-ext-2.discordapp.net/external/LpasM5XrQtK9gubFjkaqfYprpPpjU6WakDArZEzbYFg/%3Fsize%3D48%26quality%3Dlossless/https/cdn.discordapp.com/emojis/964469248946761788.gif'
                await ctx.respond(gif, ephemeral=True)
            # Или же пользователю не хватает средств для совершения перевода
            elif db.get_balance(ctx.guild, ctx.author) < amount:
                await ctx.respond(f'Недостаточно средств для перевода!', ephemeral=True)
            # Если всё ок
            else:
                db.add_cash(ctx.guild, ctx.author, -amount)  # Отнимаем у того, кто вызвал команду
                db.add_cash(ctx.guild, member, amount)  # Переводим указанному пользователю
                embed = discord.Embed(title='**Rofl was happened!**',
                                      description=f'Пользователь {ctx.author.name} перевел {member.mention} **{amount}** 💎',
                                      colour=discord.Colour.blue())
                embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')

                await ctx.respond(embed=embed,
                                  allowed_mentions=discord.AllowedMentions())

            db.close_connection()

        except Exception as e:
            print(f'Ошибка в cogs/economics.py в функции __give: {e}')
            db.close_connection()

    @slash_command(name='китстарт', description='Получи кит старт')
    @commands.cooldown(1, commands_cooldown['kit_start'], commands.BucketType.user)
    async def kit_start(self, ctx):
        """Выдает кит старт раз в сутки"""

        db = Database()
        try:
            await ctx.defer()
            db.add_cash(ctx.guild, ctx.author, kit_prices['start'])
            embed = discord.Embed(title='**Rofl was happened**',
                                  description=f'{ctx.author.name} залутал **кит старт** в размере {kit_prices["start"]} 💎',
                                  colour=discord.Colour.dark_blue())
            embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
            await ctx.respond(embed=embed)
            db.close_connection()

        except Exception as e:
            print(f'Произошла ошибка в kit_start: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='китпремиум', description='Получи кит премиум')
    @commands.cooldown(1, commands_cooldown['kit_premium'], commands.BucketType.user)
    async def kit_premium(self, ctx):
        """Выдает кит премиум раз в неделю"""

        db = Database()
        try:
            await ctx.defer()
            db.add_cash(ctx.guild, ctx.author, kit_prices['premium'])
            embed = discord.Embed(title='**Rofl was happened**',
                                  description=f'{ctx.author.name} залутал **кит премиум** в размере {kit_prices["premium"]} 💎',
                                  colour=discord.Colour.nitro_pink())
            embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
            await ctx.respond(embed=embed)
            db.close_connection()

        except Exception as e:
            print(f'Произошла ошибка в kit_premium: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)
            db.close_connection()

    @slash_command(name='статистика', description='Показать игровую статистику')
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __statistics(self, ctx, member: Option(discord.Member, "Имя пользователя", required=False) = None):
        """Выводит игровую статистику"""

        try:
            await ctx.defer()
            # Если не указан пользователь, то выводим стату того, кто вызвал команду
            if member is None:
                coin_win, coin_lose, coin_networth, coin_winrate, dice_win, dice_lose, dice_networth, dice_winrate, total_winrate = get_user_statistics(
                    ctx,
                    ctx.author)

                embed = discord.Embed(title=f'**Статистика** на сервере **{ctx.guild}** :bar_chart: ',
                                      colour=discord.Colour.dark_theme())
                embed.set_author(name=f'{ctx.author.name}', icon_url=f'{ctx.author.display_avatar}')
                embed.add_field(name='**Монетка** :coin:',
                                value=f'Всего игр: {coin_win + coin_lose}\nПобед: {coin_win}\nПоражений: {coin_lose}\nВинрейт: {coin_winrate}%\nЗаработок: {coin_networth} 💎')
                embed.add_field(name='**Кубик** :game_die:',
                                value=f'Всего игр: {dice_win + dice_lose}\nПобед: {dice_win}\nПоражений: {dice_lose}\nВинрейт: {dice_winrate}%\nЗаработок: {dice_networth} 💎')
                embed.add_field(name='**Общая стата** :globe_with_meridians: ',
                                value=f'Всего игр: {dice_win + dice_lose + coin_win + coin_lose}\nПобед: {dice_win + coin_win}\nПоражений: {dice_lose + coin_lose}\nВинрейт: {total_winrate}%\nЗаработок: {dice_networth + coin_networth} 💎')
                embed.set_image(url=icons_urls['berserk'])
                await ctx.respond(embed=embed)
            else:
                coin_win, coin_lose, coin_networth, coin_winrate, dice_win, dice_lose, dice_networth, dice_winrate, total_winrate = get_user_statistics(
                    ctx,
                    member)

                embed = discord.Embed(title=f'**Статистика на сервере {ctx.guild}** :bar_chart: ',
                                      colour=discord.Colour.dark_theme())
                embed.set_author(name=f'{member.name}', icon_url=f'{member.display_avatar}')
                embed.add_field(name='**Монетка** :coin:',
                                value=f'Всего игр: {coin_win + coin_lose}\nПобед: {coin_win}\nПоражений: {coin_lose}\nВинрейт: {coin_winrate}%\nЗаработок: {coin_networth} 💎')
                embed.add_field(name='**Кубик** :game_die:',
                                value=f'Всего игр: {dice_win + dice_lose}\nПобед: {dice_win}\nПоражений: {dice_lose}\nВинрейт: {dice_winrate}%\nЗаработок: {dice_networth} 💎')
                embed.add_field(name='**Общая стата** :globe_with_meridians: ',
                                value=f'Всего игр: {dice_win + dice_lose + coin_win + coin_lose}\nПобед: {dice_win + coin_win}\nПоражений: {dice_lose + coin_lose}\nВинрейт: {total_winrate}%\nЗаработок: {dice_networth + coin_networth} 💎')
                embed.set_image(url=icons_urls['berserk'])
                await ctx.respond(embed=embed)

        except Exception as e:
            await ctx.respond(f'Невозможно отобразить статистику пользователя!', ephemeral=True)
            print(f'Ошибка в cogs/economics.py в функции __statistics: {e}')


def setup(bot):
    bot.add_cog(Economics(bot))
