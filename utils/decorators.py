from discord import app_commands
import discord


def is_owner():
    async def predicate(interaction: discord.Interaction):
        return await interaction.client.is_owner(interaction.user)

    return app_commands.check(predicate)
