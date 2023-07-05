import discord
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands

from Database import Database
from config import commands_cooldown


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name='начислить')
    @commands.is_owner()
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __add_cash(self,
                         ctx,
                         member: Option(discord.Member, "Имя пользователя", required=True),
                         amount: Option(int, 'Сколько', required=True)
                         ):
        """Начисляем денег пользователю"""
        try:
            await ctx.defer(ephemeral=True)
            db = Database()
            db.add_cash(ctx.guild, member, amount)
            db.close_connection()
            await ctx.respond(f'Успешно начислено **{amount}** 💎 пользователю **{member.name}**')

        except Exception as e:
            print(f'Произошла ошибка в __add_cash: {e}')
            await ctx.respond('Произошла ошибка!', ephemeral=True)


def setup(bot):
    bot.add_cog(Admin(bot))
