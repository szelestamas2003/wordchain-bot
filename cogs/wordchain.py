from discord.ext import commands
import discord
from discord import app_commands
from utils.LanguageTransformer import LanguageTransformer


class WordChainCog(commands.Cog, name="WordChain"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="create-game", description="Create a word chain game in this text channel.",
                      auto_locale_strings=True)
    @app_commands.describe(language="The language of the game you wish to play")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def create_game(self, interaction: discord.Interaction, language: app_commands.Transform[str, LanguageTransformer]):
        if interaction.channel_id in (await self.bot.get_channels(interaction.guild_id)):
            await interaction.response.send_message("A game is already running in this channel.", ephemeral=True)
        else:
            await self.bot.add_channel(interaction.guild_id, interaction.channel_id, language)
            await interaction.response.send_message("A game of word chain is now live in this text channel.")

    @app_commands.command(name="end-game", description="End the word chain game in this text channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def end_game(self, interaction: discord.Interaction):
        if interaction.channel_id not in (await self.bot.get_channels(interaction.guild_id)):
            await interaction.response.send_message("No game is running in this channel.")
        else:
            await self.bot.remove_channel(interaction.guild_id, interaction.channel_id)
            await interaction.response.send_message("Game ended.")

