import discord
from discord.ext import commands
from discord import app_commands
import logging


class GeneralCog(commands.Cog, name="General"):
    def __init__(self, bot: commands.Bot):
        super().__init__()
        self.bot = bot
        self.logger = logging.getLogger("discord")

    @app_commands.command(name="invite", description="Shows you the invite for the bot")
    @app_commands.allowed_installs(users=True, guilds=True)
    @app_commands.allowed_contexts(guilds=True, private_channels=True, dms=True)
    async def invite(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Invite the bot", description="If you liked the bot you can install it with this link.", colour=discord.Color.blue())
        view = discord.ui.View()
        button = discord.ui.Button(label="Invite the bot", url="https://discord.com/oauth2/authorize?client_id=1222232775449509980")
        view.add_item(button)
        await interaction.response.send_message(embed=embed, view=view)
