import os, sys, discord
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

class Help(commands.Cog, name="help"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, context):
        # Note that commands made only for the owner of the bot are not listed here.
        embed = discord.Embed(
            title="Bot",
            description="List of commands are:",
            color=0x00FF00
        )
        embed.add_field(
            name="Invite",
            value=f"Usage: {config.BOT_PREFIX}invite",
            inline=False
        )
        embed.add_field(
            name="Server",
            value=f"Usage: {config.BOT_PREFIX}server",
            inline=False
        )
        embed.add_field(
            name="Poll",
            value=f"Usage: {config.BOT_PREFIX}poll <Idea>",
            inline=False
        )
        embed.add_field(
            name="8ball",
            value=f"Usage: {config.BOT_PREFIX}8ball <Question>",
            inline=False)
        embed.add_field(
            name="Bitcoin",
            value=f"Usage: {config.BOT_PREFIX}bitcoin",
            inline=False
        )
        embed.add_field(
            name="Info",
            value=f"Usage: {config.BOT_PREFIX}info",
            inline=False
        )
        embed.add_field(
            name="status",
            value=f"Usage: {config.BOT_PREFIX}status\n Desc: Get DCS Mission, Uptime, Players for servers",
            inline=False
        )
        embed.add_field(
            name="mlist",
            value=f"Usage: {config.BOT_PREFIX}mlist\n Desc: Get DCS Mission Server last 10 missions",
            inline=False
        )
        embed.add_field(
            name="attendance",
            value=f"Usage: {config.BOT_PREFIX}attendance <mission ID> \n Desc: Get DCS attendance using ID from mlist",
            inline=False
        )
        embed.add_field(
            name="Purge",
            value=f"Usage: {config.BOT_PREFIX}purge <Number>",
            inline=False
        )
        embed.add_field(
            name="Help",
            value=f"Usage: {config.BOT_PREFIX}help",
            inline=False
        )
        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))