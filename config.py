# Базовые роли, создаются при появлении бота на сервере
basic_roles = {'Rofl': (255, 69, 0),
               'Radiant': (34, 139, 34),
               'Neutral': (228, 228, 228),
               'Dire': (178, 34, 34),
               'Всевидящий': (123, 104, 238)
               }
# Cooldown комманд в секундах
commands_cooldown = {'default': 2,
                     'kit_start': 86400,
                     'kit_premium': 604800,
                     'russian_roulette': 259200,
                     'image': 60,
                     'chulan': 600
                     }
# Стоимость различных приколов
services_prices = {'rofl_per_minute': 2,
                   'chulan': 50,
                   'vision': 8888,
                   'image': 20}

# Кол-во валюты в наборах
kit_prices = {'start': 50,
              'premium': 170}

# Url разных картинок
icons_urls = {
    'raiden_ass': 'https://sun9-8.userapi.com/impg/85ypW5mwBqwZMMEo_6U7tHGzFULD9beY2CbCMw/x1VVuzNoiLc.jpg?size=1280x327&quality=95&sign=0e98ffd6098bbaf34bfd1e41850055a7&c_uniq_tag=Nct__Ry-4LdzRD08NAsD4tvlGntEfSRk0ExFm7SbpAE&type=album',
    'hellsing': 'https://xn----7sbcgrydczc.xn--p1ai/src/img/lower/anime/anime-khelsing/anime-khelsing-1.png',
    'berserk': 'https://sun9-13.userapi.com/impg/zIYx0me1veuTI7NFxIPqjvyo6BRy5Pc3m2B5ZQ/hnZFxt-kc4E.jpg?size=960x320&quality=96&sign=6918a5189b5bdea2580e6b46f5a36cc8&type=album'}

# Словарь для /помощь
help_commands = {'💳 | **баланс**': 'Проверка баланса пользователя',
                 '💸 | **передать**': 'Передача денег пользователю',
                 '📊 | **статистика**': 'Получение игровой статистики пользователя',
                 '🔹 | **китстарт**': f'Получение базового набора в размере **{kit_prices["start"]}** 💎 раз в сутки',
                 '🔸 | **китпремиум**': f'Получение премиум набора в размере **{kit_prices["premium"]}** 💎 раз в неделю',
                 '❓ | **кто**': 'Позволяет узнать много нового о людях на сервере',
                 '🤔 | **вероятность**': 'Вероятностная аналитика от рофл-бота',
                 '🤡 | **зарофлить**': f'“Рофл” пользователя\nТариф 1 минута ~ **{services_prices["rofl_per_minute"]}** 💎',
                 '🚬 | **чулан**': f'Отправка пользователя в “Чулан”\nСтоимость **{services_prices["chulan"]}** 💎',
                 '🟡 | **монетка**': 'Подбросить монетку',
                 '🎲 | **кубик**': 'Игровая команда, подбрасывание кубика',
                 '🔫 | **русская_рулетка**': 'Название говорит само за себя',
                 '🖼️ | **пикча**': f'Генерация изображений при помощи Crayion\nСтоимость **{services_prices["image"]}** 💎',
                 '👁️ | **0_0**': 'Становление “Всевидящим”',
                 '📃| **помощь**': 'Помощь по командам / информация о владельце'
                 }

help_author = ''
