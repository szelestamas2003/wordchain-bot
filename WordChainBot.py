from discord.ext import commands
import discord
from discord.ext import tasks
from discord.app_commands import AppInstallationType, AppCommandContext
import datetime
import os
import logging
from typing import Optional
from emoji import is_emoji

from cogs.general import GeneralCog
from utils.db_connection import DatabaseConnection
from utils.check_spelling import check_spelling
from cogs.owneronly import OwnerOnlyCog
from cogs.wordchain import WordChainCog


class WordChainBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.all()
        self.__database = DatabaseConnection()
        self.languages = []
        self.command_prefix = '!'
        self.logger = logging.getLogger('discord')
        super().__init__(command_prefix=self.command_prefix, allowed_contexts=AppCommandContext(guild=True), allowed_installs=AppInstallationType(guild=True), intents=intents, activity=discord.Game("Word Chain", start=datetime.datetime.now(datetime.UTC)))

    async def setup_hook(self):
        self.languages = await self.get_languages()
        self.logger.debug("Got available languages")
        self.__test_server_id = int(os.environ["TEST_SERVER_ID"])
        await self.add_cog(OwnerOnlyCog(self))
        await self.add_cog(WordChainCog(self))
        await self.add_cog(GeneralCog(self))
        self.logger.debug("Added cogs.")

    async def on_connect(self):
        await self.connect_to_db()

    async def on_disconnect(self):
        await self.close_connection()
        print("WordChain bot is now sleeping. Bye!")

    async def close(self):
        self.logger.info("Shutting down the bot")
        await self.close_connection()
        await super().close()
        self.logger.info("Shutdown completed")
        self.logger.info("\n------------------------------------------------------\n")

    async def on_ready(self):
        print(f"The bot is on {len(self.guilds)} discord server:")
        for guild in self.guilds:
            if not await self.get_guild_by_id(guild.id):
                await self.add_guild(guild.id)
            print(guild)
        self.logger.info(f"Logged in as {self.user}")
        print("WordChain bot is ready to be used!")

    async def on_message(self, message: discord.Message):
        if message.content.startswith(self.command_prefix):
            await self.process_commands(message)
        else:
            if message.author == self.user:
                return
            elif self.user.mentioned_in(message) and (await self.is_owner(message.author)):
                self.logger.debug("Syncing the commands started")
                await self.tree.sync()
                await self.tree.sync(guild=discord.Object(self.__test_server_id))
                self.logger.debug("Synced all commands")
                print("Synced all commands.")
                return
            elif message.guild is not None and message.channel.id not in (await self.get_channels(message.guild.id)):
                return
            elif len(message.mentions) > 0 or len(message.role_mentions) > 0 or message.mention_everyone:
                return

            passed, streak = await self.check_input(message.content, message.guild.id, message.channel.id,
                                                    message.author.id)

            pass_react, wrong_react = await self.get_reactions(message.guild.id, message.channel.id)

            if passed:
                if pass_react is None:
                    pass_react = "✅"
                elif not is_emoji(pass_react):
                    pass_react = self.get_emoji(int(pass_react))
                await message.add_reaction(pass_react)
            else:
                if wrong_react is None:
                    wrong_react = "❌"
                elif not is_emoji(wrong_react):
                    wrong_react = self.get_emoji(int(wrong_react))
                await message.add_reaction(wrong_react)
                await message.channel.send(
                    f"The game has ended after {streak} different word(s) thanks to {message.author.mention}! Congratulate to him/her!\nSend a new word to start a new game!")

    async def on_guild_join(self, guild: discord.Guild):
        await self.add_guild(guild.id)
        self.logger.info(f"Joined to {guild.name} server")
        print(f"Joined to {guild.name} discord server!")

    async def on_guild_remove(self, guild: discord.Guild):
        await self.remove_guild(guild.id)
        self.logger.info(f"Removed from {guild.name} server")
        print(f"Removed from {guild.name} discord server! Bye!")

    async def get_languages(self):
        await self.__database.connect()
        languages = await self.__database.get_languages()
        await self.__database.close_connection()
        return languages

    async def get_guild_by_id(self, guild_id: int):
        return await self.__database.get_guild_by_id(guild_id)

    async def get_channels(self, guild_id: int):
        channels = await self.__database.get_guild_channels(guild_id)
        return [channel[0] for channel in channels]

    async def get_reactions(self, guild_id: int, channel_id: int):
        return await self.__database.get_props(guild_id, channel_id, "pass_reaction", "wrong_reaction")

    async def add_channel(self, guild_id: int, channel_id: int, lang: str):
        await self.__database.add_channel(guild_id, channel_id, lang)

    async def add_guild(self, guild_id: int):
        await self.__database.add_guild(guild_id)

    async def add_reaction(self, guild_id: int, channel_id: int, pass_reaction: Optional[str],
                           wrong_reaction: Optional[str]):
        await self.__database.add_reactions(guild_id, channel_id, pass_reaction, wrong_reaction)

    async def remove_channel(self, guild_id: int, channel_id: int):
        await self.__database.remove_channel(guild_id, channel_id)

    async def remove_guild(self, guild_id: int):
        await self.__database.remove_guild(guild_id)

    async def remove_reaction(self, guild_id: int, channel_id: int, pass_reaction: bool, wrong_reaction: bool):
        await self.__database.remove_reactions(guild_id, channel_id, pass_reaction, wrong_reaction)

    async def check_input(self, message: str, guild_id: int, channel_id: int, author_id: int):
        lang, last_sender_id, last_word, streak_count = await self.__database.get_props(guild_id, channel_id,
                                                                                        "guild_lang", "last_sender_id",
                                                                                        "last_word", "streak_count")
        special_chars = await self.__database.get_special_chars(lang)
        is_matching = False
        if len(message.split(" ")) == 1:
            word = message.split(" ")[0]
            if check_spelling(word, lang) and await self.__database.check_words(guild_id, channel_id, word):
                if streak_count == 0 and last_sender_id is None and last_word is None:
                    is_matching = True
                elif last_sender_id is not None and last_word is not None and last_sender_id != author_id:
                    i = 0
                    while i < len(special_chars) and not is_matching:
                        char = special_chars[i]
                        if last_word.find(char) == len(last_word) - len(char):
                            if word.find(char) == 0:
                                is_matching = True
                            else:
                                break
                        i = i + 1
                    if last_word[-1] == word[0]:
                        is_matching = True

        if is_matching:
            await self.__database.update_db(guild_id, channel_id, author_id, message, False)
            return True, streak_count
        else:
            await self.__database.update_db(guild_id, channel_id, author_id, message, True)
            return False, streak_count

    async def close_connection(self):
        await self.__database.close_connection()

    async def connect_to_db(self):
        await self.__database.connect()

    @tasks.loop(hours=4)
    async def check_connection(self):
        await self.__database.check_connection()
