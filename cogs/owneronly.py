from discord.ext import commands
from discord import app_commands
import discord
import logging
from cogs.wordchain import WordChainCog


class PrivateCogs(commands.Cog, name="PrivateFuncs"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.logger = logging.getLogger('discord')

    @app_commands.command(name="shutdown", description="Shuts down the bot")
    @commands.is_owner()
    async def shutdown(self, interaction: discord.Interaction):
        await interaction.response.send_message("Shutting down bot", ephemeral=True)
        await interaction.client.close()
        print(f"Bot closed by {interaction.message.author.name}")

    @app_commands.command(name="reload-cogs", description="Reloads the functions to the bot")
    @commands.is_owner()
    async def reload_cogs(self, interaction: discord.Interaction):
        self.logger.info("Reloading cogs")
        bot = interaction.client
        await self.bot.remove_cog("PrivateFuncs")
        await self.bot.add_cog(PrivateCogs(bot))
        await self.bot.remove_cog("WordChain")
        await self.bot.add_cog(WordChainCog(bot))
        await interaction.response.send_message("Reloaded cogs", ephemeral=True)
        print("Cogs reloaded")
        self.logger.info("Cogs reloaded")
