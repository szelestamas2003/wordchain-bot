from discord.ext import commands
from discord import app_commands
import discord
import logging
import os
from cogs.wordchain import WordChainCog
from utils.decorators import is_owner


class PrivateCogs(commands.Cog, name="PrivateFuncs"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.logger = logging.getLogger('discord')

    @app_commands.command(name="shutdown", description="Shuts down the bot")
    @app_commands.guilds(int(os.environ["TEST_SERVER_ID"]))
    @app_commands.default_permissions(administrator=True)
    @is_owner()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("Shutting down bot", ephemeral=True)
        await self.bot.close()
        self.logger.info(f"Bot closed by {interaction.message.author.name}")
        print(f"Bot closed by {interaction.message.author.name}")

    @app_commands.command(name="reload-cogs", description="Reloads the functions to the bot")
    @app_commands.guilds(int(os.environ["TEST_SERVER_ID"]))
    @app_commands.default_permissions(administrator=True)
    @is_owner()
    async def reload_cogs(self, interaction: discord.Interaction):
        self.logger.info("Reloading cogs")
        await self.bot.remove_cog("PrivateFuncs")
        await self.bot.add_cog(PrivateCogs(self.bot))
        await self.bot.remove_cog("WordChain")
        await self.bot.add_cog(WordChainCog(self.bot))
        await interaction.response.send_message("Reloaded cogs", ephemeral=True)
        print("Cogs reloaded")
        self.logger.info("Cogs reloaded")
