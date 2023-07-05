import base64
from io import BytesIO

import discord
from craiyon import Craiyon, craiyon_utils
from discord.commands import Option
from discord.commands import slash_command
from discord.ext import commands

from config import services_prices, commands_cooldown
from Database import Database


class Image(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.generator = Craiyon()

    @slash_command(name='пикча',
                   description=f'Сгенерируйте изображение по запросу за {services_prices["image"]} гемов')
    @commands.cooldown(1,commands_cooldown['image'], commands.BucketType.user)
    async def image(self,
                    ctx,
                    prompt: Option(str, 'Описание', required=True),
                    style: Option(str, 'Стиль', choices=['art', 'photo', 'drawing'], required=False) = 'none'
                    ):
        """Функция генерации изображения при помощи Craiyon API"""
        db = Database()
        try:
            await ctx.defer()

            cur_balance = db.get_balance(ctx.guild, ctx.author)
            price = config.services_prices["image"]

            if cur_balance < price:
                await ctx.respond(f"Недостаточно средств! Чтобы сгенерить пикчи нужно {price} 💎", ephemeral=True)

            else:
                db.add_cash(ctx.guild, ctx.author, price)
                generated_images = await self.generator.async_generate(prompt, model_type=style)  # Generate images
                b64_list = await craiyon_utils.async_encode_base64(
                    generated_images.images)  # Download images from https://img.craiyon.com and store them as b64 bytestring object

                images1 = []
                for index, image in enumerate(b64_list):  # Loop through b64_list, keeping track of the index
                    img_bytes = BytesIO(base64.b64decode(image))  # Decode the image and store it as a bytes object
                    image = discord.File(img_bytes)
                    image.filename = f"result{index}.webp"
                    images1.append(image)  # Add the image to the images1 list

                await ctx.respond(f'Генерация по запросу: **{prompt}**',
                                  files=images1)  # Reply to the user with all 9 images in 1 message

            db.close_connection()

        except Exception as e:
            print(f'Произошла ошибка в image: {e}')
            db.close_connection()
            await ctx.respond('Ошибка при генерации изображения!', ephemeral=True)


def setup(bot):
    bot.add_cog(Image(bot))
