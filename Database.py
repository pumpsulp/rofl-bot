import sqlite3

from discord import Guild
from discord import Member
from discord.user import User


class Database:
    def __init__(self, database_path='Database/database.db'):
        self.connection = sqlite3.connect(database_path, isolation_level=None)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA journal_mode=WAL")

    def update(self, guilds: list[Guild]) -> None:
        """Обновление БД"""

        # Проходимся по всем серверам
        for guild in guilds:
            try:
                # Создаём таблицу сервера, если её нет
                self.cursor.execute(f"""CREATE TABLE IF NOT EXISTS {guild} (
                            name TEXT,
                            id INT,
                            cash INT,
                            coin_win INT,
                            coin_lose INT,
                            coin_networth INT,
                            dice_win INT,
                            dice_lose INT,
                            dice_networth INT
                                )""")

                # Добавляем пользователей в таблицу сервера
                for user in guild.members:
                    self.add_user(guild, user)

            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")
            else:
                self.connection.commit()

    def close_connection(self) -> None:
        """Закрывает соединение с БД."""
        self.cursor.close()
        self.connection.close()

    def userid_check(self, guild: Guild, user: User or Member) -> bool:
        """Проверка наличия пользователя в БД по id.\n
        Возвращает True, если пользователь есть в БД."""
        return self.cursor.execute(f"SELECT id FROM {guild} WHERE id = {user.id}").fetchone() is not None

    def add_user(self,
                 guild: Guild,
                 user: User or Member,
                 cash: int = 0,
                 coin_win: int = 0,
                 coin_lose: int = 0,
                 coin_networth: int = 0,
                 dice_win: int = 0,
                 dice_lose: int = 0,
                 dice_networth: int = 0
                 ) -> None:

        """Добавление пользователя в БД"""

        if not self.userid_check(guild, user):
            try:
                self.cursor.execute("BEGIN TRANSACTION")
                self.cursor.execute(
                    f"INSERT INTO {guild} VALUES ('{user.name}', {user.id}, {cash}, {coin_win}, {coin_lose}, {coin_networth}, {dice_win}, {dice_lose}, {dice_networth})")
                self.cursor.execute("END TRANSACTION")
                print(f'Database: User {user} added to {guild} table')
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")
            else:
                self.connection.commit()

    def remove_user(self, guild: Guild, user: User or Member) -> None:
        """Удаление пользователя из БД"""
        if self.userid_check(guild, user):
            try:
                self.cursor.execute("BEGIN TRANSACTION")
                self.cursor.execute(f"DELETE FROM {guild} WHERE id = {user.id}")
                self.cursor.execute("END TRANSACTION")
                print(f'Database: User {user} remove from {guild} table')
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")
            else:
                self.connection.commit()

    def get_balance(self, guild: Guild, user: User or Member) -> int:
        """Получаем из БД баланс по id пользователя."""
        if self.userid_check(guild, user):
            try:
                return self.cursor.execute(f"SELECT cash FROM {guild} WHERE id = {user.id}").fetchone()[0]
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")

    def get_statistics(self, guild: Guild, user: User or Member, game: str) -> tuple[int, int, int]:
        """Получаем из БД инфу о победах и поражениях, а также нетворс пользователя в игре game по id пользователя."""
        if self.userid_check(guild, user):
            try:
                return (self.cursor.execute(f"SELECT {game}_win FROM {guild} WHERE id = {user.id}").fetchone()[0],
                        self.cursor.execute(f"SELECT {game}_lose FROM {guild} WHERE id = {user.id}").fetchone()[0],
                        self.cursor.execute(f"SELECT {game}_networth FROM {guild} WHERE id = {user.id}").fetchone()[0])
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py, get_statistics: {err}")

    def add_cash(self, guild: Guild, user: User or Member, amount: int) -> None:
        """Добавляем пользователю деньгу по id."""
        current_cash = self.get_balance(guild, user)
        if abs(amount) > current_cash and amount < 0:
            raise Exception(f'Указанная сумма {amount} превышает баланс пользователя!')
        else:
            try:
                self.cursor.execute("BEGIN TRANSACTION")
                self.cursor.execute(f"UPDATE {guild} SET cash = cash + {amount} WHERE id = {user.id}")
                self.cursor.execute("END TRANSACTION")
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")
            else:
                self.connection.commit()
                # print(f'Database: {guild} server: Added {amount} cash to {user.id}')

    def add_statistics(self, guild: Guild, user: User or Member, game: str, result: str, networth: int):
        """Обновляем статистику пользователя в какой-то игре по id"""
        if self.userid_check(guild, user):
            try:
                self.cursor.execute("BEGIN TRANSACTION")
                self.cursor.execute(f"UPDATE {guild} SET {game}_{result} = {game}_{result} + 1 WHERE id = {user.id}")
                self.cursor.execute(f"UPDATE {guild} SET {game}_networth = {game}_networth + {networth} WHERE id = {user.id}")
                self.cursor.execute("END TRANSACTION")
            except sqlite3.DatabaseError as err:
                print(f"Произошла ошибка в Database.py: {err}")
            else:
                self.connection.commit()
