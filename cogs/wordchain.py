from discord.ext import commands
from discord import app_commands
import discord
from emoji import is_emoji
from utils.LanguageTransformer import LanguageTransformer
from typing import Optional


class WordChainCog(commands.Cog, name="WordChain"):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot

    @app_commands.command(name="create-game", description="Create a word chain game in this text channel.",
                          auto_locale_strings=True)
    @app_commands.describe(language="The language of the game you wish to play",
                           channel="The channel in which the game is running if you not write the command in it.",
                           pass_reaction="The emote to use if a word is passed.",
                           wrong_reaction="The emote to use if a word is passed.")
    @app_commands.rename(pass_reaction='pass-emote', wrong_reaction='wrong-emote')
    @app_commands.checks.has_permissions(manage_channels=True)
    async def create_game(self, interaction: discord.Interaction,
                          language: app_commands.Transform[str, LanguageTransformer],
                          channel: Optional[discord.TextChannel] = None, pass_reaction: Optional[str] = None,
                          wrong_reaction: Optional[str] = None):
        if channel is None:
            channel_id = interaction.channel.id
        else:
            channel_id = channel.id

        if channel_id in (await self.bot.get_channels(interaction.guild_id)):
            await interaction.response.send_message("A game is already running in this channel.", ephemeral=True)
        else:
            pass_reaction, wrong_reaction = await self.__check_reaction_strings(pass_reaction, wrong_reaction)
            if (pass_reaction is not None and len(pass_reaction) == 0) or (
                    wrong_reaction is not None and len(wrong_reaction) == 0):
                await interaction.response.send_message("Couldn't find one of the passed reactions in your guild.",
                                                        ephemeral=True)
                return
            else:
                await self.bot.add_channel(interaction.guild_id, channel_id, language)
                await self.bot.add_reaction(interaction.guild_id, channel_id, pass_reaction, wrong_reaction)
                await interaction.response.send_message("A game of word chain is now live in this text channel.")

    @app_commands.command(name="end-game", description="End the word chain game in this text channel.")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def end_game(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None):
        if channel is not None and channel not in (await self.bot.get_channels(interaction.guild_id)):
            await interaction.response.send_message("The specified channel doesn't run a word chain game.")
        elif channel is None and interaction.channel_id not in (await self.bot.get_channels(interaction.guild_id)):
            await interaction.response.send_message("No game is running in this channel.")
        else:
            if channel is not None:
                channel_id = channel.id
            else:
                channel_id = interaction.channel_id
            await self.bot.remove_channel(interaction.guild_id, channel_id)
            await interaction.response.send_message("Game ended.")

    @app_commands.command(name="change-reaction", description="Changes one or both reaction emote to a custom one.")
    @app_commands.describe(channel="The channel in which the game is running if you not write the command in it.",
                           pass_reaction="The emote to use if a word is passed.",
                           wrong_reaction="The emote to use if a word is passed.")
    @app_commands.rename(pass_reaction="pass-emote", wrong_reaction="wrong-emote")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def change_reaction(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None,
                              pass_reaction: Optional[str] = None, wrong_reaction: Optional[str] = None):
        guild_id = interaction.guild_id
        if pass_reaction is None and wrong_reaction is None:
            await interaction.response.send_message("One or both reactions must be passed", ephemeral=True)
            return
        elif channel is not None and channel.id not in (await self.bot.get_channels(guild_id)):
            await interaction.response.send_message("Passed channel is not running a game", ephemeral=True)
            return
        elif channel is None and interaction.channel_id not in (await self.bot.get_channels(guild_id)):
            await interaction.response.send_message(
                "Either pass a channel or use the command in a channel that has a word chain game in it.",
                ephemeral=True)
            return
        else:
            if channel is None:
                channel_id = interaction.channel_id
            else:
                channel_id = channel.id

            pass_reaction, wrong_reaction = await self.__check_reaction_strings(pass_reaction, wrong_reaction)
            if (pass_reaction is not None and len(pass_reaction) == 0) or (
                    wrong_reaction is not None and len(wrong_reaction) == 0):
                await interaction.response.send_message("Couldn't find one of the passed reactions in your guild.",
                                                        ephemeral=True)
            else:
                await self.bot.add_reaction(guild_id, channel_id, pass_reaction, wrong_reaction)
                await interaction.response.send_message("Successfully added reactions to your guild.", ephemeral=True)

    @app_commands.command(name="remove-custom-reactions", description="Remove the custom added reactions if needed.")
    @app_commands.describe(channel="The channel in which the game is running if you not write the command in it.",
                           pass_reaction="If you would like to remove the custom pass reaction emote.",
                           wrong_reaction="If you would like to remove the custom wrong reaction emote.")
    @app_commands.rename(pass_reaction="delete-pass-emote", wrong_reaction="delete-wrong-emote")
    @app_commands.checks.has_permissions(manage_channels=True)
    async def remove_reactions(self, interaction: discord.Interaction, channel: Optional[discord.TextChannel] = None,
                               pass_reaction: bool = False, wrong_reaction: bool = False):
        guild_id = interaction.guild_id
        if channel is not None and channel.id not in (await self.bot.get_channels(guild_id)):
            await interaction.response.send_message("Passed channel is not running a game", ephemeral=True)
            return
        elif channel is None and interaction.channel_id not in (await self.bot.get_channels(guild_id)):
            await interaction.response.send_message(
                "Either pass a channel or use the command in a channel that has a word chain game in it.",
                ephemeral=True)
            return
        else:
            if channel is None:
                channel_id = interaction.channel_id
            else:
                channel_id = channel.id

        await self.bot.remove_reactions(guild_id, channel_id, pass_reaction, wrong_reaction)

    async def __check_reaction_strings(self, pass_reaction: Optional[str] = None,
                                       wrong_reaction: Optional[str] = None):
        pass_reaction = await self.__check_reaction(pass_reaction)
        wrong_reaction = await self.__check_reaction(wrong_reaction)
        return pass_reaction, wrong_reaction

    async def __check_reaction(self, reaction: Optional[str] = None) -> Optional[str]:
        if reaction is not None:
            if not is_emoji(reaction):
                emoji = self.bot.get_emoji(int(reaction.replace(">", "").replace("<", "").split(":")[-1]))
                if emoji is not None:
                    return str(emoji.id)
                else:
                    return ""
            return reaction
        else:
            return None
