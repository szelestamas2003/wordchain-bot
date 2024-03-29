from discord import app_commands
import discord
import WordChainBot


class LanguageTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction[WordChainBot], value: str):
        return value

    async def autocomplete(self, interaction: discord.Interaction[WordChainBot], value: str):
        return [app_commands.Choice(name=lang_L, value=lang) for lang_L, lang in interaction.client.languages.items()]
