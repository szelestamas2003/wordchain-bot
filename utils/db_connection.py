import mysql.connector.connection
from mysql.connector.aio import connect
from mysql.connector import Error
import os
import logging


class DatabaseConnection:
    def __init__(self):
        self.logger = logging.getLogger("discord")
        self.__connection: mysql.connector.aio.connection.MySQLConnection = None

    async def connect(self):
        try:
            self.__connection = await connect(host='host.docker.internal', user=os.environ['MYSQL_USER'],
                                        password=os.environ.get('MYSQL_PASSWORD'),
                                        database=os.environ['MYSQL_DB'])
            print(f"Connection id: {self.__connection.connection_id}")
            self.logger.info(f"Connected to {await self.__connection.get_database()} with {self.__connection.connection_id}")
        except Error as e:
            print("Error while connecting to MySQL", e)
            raise ModuleNotFoundError("Database connection not found")

    async def close_connection(self):
        await self.__connection.close()
        self.logger.info(f"Database connection closed {self.__connection.connection_id}")

    async def check_connection(self):
        self.logger.info("Checking connection to database")
        if not self.__connection.is_connected():
            self.logger.info("Not connected to the database. Retrying.")
            await self.__connection.connect()
            self.logger.info("Connected to database {}".format(await self.__connection.get_database()))
        else:
            cursor = await self.__connection.cursor()
            await cursor.execute(f"SELECT time, state from information_schema.tables where user='{os.environ['MYSQL_USER']}'")
            time, state = await cursor.fetchone()
            self.logger.info(f"Database has been pinged. The connection is in {state} since {time} seconds")

    async def get_languages(self):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT * FROM {os.environ['LANGUAGE_TABLE']}")
        rows = await cursor.fetchall()
        rows = {lang_L: lang for lang, lang_L in rows}
        self.logger.debug("Got languages from database: {}".format(rows))
        return rows

    async def get_special_chars(self, lang: str):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT * FROM {os.environ['SPECIAL_CHARS_TABLE']} WHERE lang = '{lang}'")
        rows = await cursor.fetchall()
        rows = [row[0] for row in rows]
        self.logger.debug("Got special chars from database: {}".format(rows))
        return rows

    async def get_guild(self, guild_id: int):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT COUNT(*) FROM {os.environ['GUILDS_TABLE_NAME']} WHERE guild_id = {guild_id}")
        result = await cursor.fetchone()
        self.logger.debug(f"{guild_id}'s count in the database: {result[0]}")
        return result[0] == 1

    async def get_guild_channels(self, guild_id: int):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT guild_channel_id FROM {os.environ['PROPS_TABLE_NAME']} WHERE guilds_id = {guild_id}")
        self.logger.debug(f"Getting {guild_id}'s channels")
        return await cursor.fetchall()

    async def get_props(self, guilds_id: int, channel_id: int, *props):
        self.logger.info("Getting props {}".format(*props))
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema='{os.environ['MYSQL_DB']}' AND table_name='{os.environ['PROPS_TABLE_NAME']}'")
        result = await cursor.fetchall()
        for prop in props:
            if not any([column[0] == prop for column in result]):
                self.logger.debug(f"{prop} is not found in the columns")
                return
        prop_string = ', '.join(["{}"] * len(props))
        sql = "SELECT {} FROM {} WHERE guilds_id={} AND guild_channel_id={}".format(prop_string, os.environ['PROPS_TABLE_NAME'], guilds_id, channel_id).format(*props)
        await cursor.execute(sql)
        self.logger.info(f"Successfully got the props for {guilds_id}:{channel_id}")
        return await cursor.fetchone()

    async def add_guild(self, guild_id: int):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"INSERT INTO {os.environ['GUILDS_TABLE_NAME']} (guild_id) VALUES ({guild_id})")
        await self.__connection.commit()
        self.logger.info(f"{guild_id} added to database")
        print("Guild added to database")

    async def add_channel(self, guilds_id: int, channel_id: int, lang: str):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"INSERT INTO {os.environ['PROPS_TABLE_NAME']} (guilds_id, guild_channel_id, guild_lang) VALUES ('{guilds_id}', '{channel_id}', '{lang}')")
        await self.__connection.commit()
        self.logger.debug(f"Added {guilds_id} - {channel_id} - {lang}")
        self.logger.info(f"{guilds_id} - {channel_id} props are added")
        print("Guild props are added to database")

    async def remove_guild(self, guilds_id: int):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"DELETE FROM {os.environ['GUILDS_TABLE_NAME']} WHERE guilds_id={guilds_id}")
        await self.__connection.commit()
        self.logger.info(f"{guilds_id} is removed from the database")
        print("Guild removed from the database")

    async def remove_channel(self, guilds_id: int, channel_id: int):
        cursor = await self.__connection.cursor()
        await cursor.execute(f"DELETE FROM {os.environ['PROPS_TABLE_NAME']} WHERE guilds_id={guilds_id} AND guild_channel_id={channel_id}")
        await self.__connection.commit()
        self.logger.info(f"{guilds_id} - {channel_id} props are deleted")
        print("Guild props are removed from database")

    async def update_db(self, guilds_id: int, channel_id: int, last_sender_id: int, last_message: str, game_over: bool):
        cursor = await self.__connection.cursor()
        if not game_over:
            await cursor.execute(f"UPDATE {os.environ['PROPS_TABLE_NAME']} SET last_sender_id={last_sender_id}, last_word='{last_message}', streak_count = streak_count + 1 WHERE guilds_id={guilds_id} AND guild_channel_id={channel_id}")
            self.logger.debug(f"Updated props of {guilds_id}:{channel_id} to last sender:{last_sender_id}, last word:{last_message}, streak_count++")
            await cursor.execute(
                f"INSERT INTO {os.environ['WORDS_TABLE_NAME']} (guild_id, guild_channel_id, word) VALUES ({guilds_id}, {channel_id}, '{last_message}')")
            self.logger.debug(f"Inserted {last_message} into {guilds_id} {channel_id}")
        else:
            await cursor.execute(f"UPDATE {os.environ['PROPS_TABLE_NAME']} SET last_sender_id=NULL, last_word=NULL, streak_count=0 WHERE guilds_id={guilds_id} AND guild_channel_id={channel_id}")
            self.logger.debug(f"Updated props of {guilds_id}:{channel_id} to default.")
            await cursor.execute(
                f"DELETE FROM {os.environ['WORDS_TABLE_NAME']} WHERE guild_id = {guilds_id} AND guild_channel_id = {channel_id}")
            self.logger.debug(f"Deleted words from {guilds_id} {channel_id}")
        await self.__connection.commit()
        self.logger.info(f"{guilds_id} : {channel_id} has been updated")

    async def check_words(self, guild_id: int, channel_id: int, word: str):
        self.logger.info("Checking word started")
        cursor = await self.__connection.cursor()
        await cursor.execute(f"SELECT COUNT(*) FROM {os.environ['WORDS_TABLE_NAME']} WHERE '{word}' IN (SELECT word FROM {os.environ['WORDS_TABLE_NAME']} WHERE guild_id = {guild_id} AND guild_channel_id = {channel_id})")
        self.logger.debug(f"Checking {guild_id}: {channel_id} - {word}")
        count = (await cursor.fetchone())[0]
        self.logger.debug(f"Checking {guild_id}: {channel_id} - {word} count {count}")
        return count == 0
