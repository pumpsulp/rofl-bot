import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ui import Button
from discord.ui import View

from config import commands_cooldown, help_commands

# class HelpView(View):
#     def __init__(self):
#         super().__init__()
#
#     @button(label='Документация', style=discord.ButtonStyle.green, emoji='📖', url='')
#
# class AuthorButton(Button):
#     """Подкласс для кнопки автора"""
#
#     def __init__(self, ctx):
#         super().__init__(label='Автор', emoji='🗿', style=discord.ButtonStyle.blurple)
#         self.ctx = ctx
#
#     async def callback(self, interaction):
#         try:
#             await interaction.response.edit_message(view=None)
#             await self.client.chat.rate(self.char, rate=self.rate)
#             await interaction.followup.send('_Спасибо за обратную связь_', ephemeral=True)
#         except Exception as e:
#             print(f'Ошибка в RateButton: {e}')


class Help(commands.Cog):
    def __init__(self, bot: discord.bot.Bot):
        self.bot = bot

    @slash_command(name='помощь', description='Информация о боте, командах и т.п.', ephemeral=True)
    @commands.cooldown(1, commands_cooldown['default'], commands.BucketType.user)
    async def __help(self, ctx):
        """Вывод help панели"""
        try:
            await ctx.defer(ephemeral=True)

            view = View()
            view.add_item(Button(label='Автор',
                                 emoji='🤓',
                                 style=discord.ButtonStyle.blurple,
                                 url='https://t.me/circlesonwater'))
            view.add_item(Button(label='Документация',
                                 emoji='📖',
                                 style=discord.ButtonStyle.green,
                                 url='https://alder-client-88c.notion.site/Rofl-bot-documentation-faeee1b216d8488f9cb21444bf346b80'))
            embed = discord.Embed(title=f'{ctx.guild}\n**Доступные команды**',
                                  colour=discord.Colour.darker_grey())

            for command, description in help_commands.items():
                embed.add_field(name=command, value=description, inline=True)

            await ctx.respond(embed=embed, view=view)

        except Exception as e:
            print(f'Произошла ошибка в /help: {e}')
            await ctx.respond('Произошла ошибка!')


def setup(bot):
    bot.add_cog(Help(bot))
