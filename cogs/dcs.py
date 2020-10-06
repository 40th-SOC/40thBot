import os, sys, discord, mysql.connector, json
from discord.ext import commands
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

db = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    database=config.DB_DATABASE,
    )

def getPlayerCount(instance):
    mycursor = db.cursor()
    mycursor.execute("SELECT * from pe_dataraw WHERE pe_dataraw_type = 1 AND pe_dataraw_instance = "+str(instance))
    myresult = mycursor.fetchone()
    playerCount = json.loads(myresult[2])["c_players"]
    playerCount = playerCount - 1
    return playerCount

def getCurrentMission(instance):
    mycursor = db.cursor()
    mycursor.execute("SELECT * from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = "+str(instance))
    myresult = mycursor.fetchone()
    currentMission = json.loads(myresult[2])["mission"]["name"]
    return currentMission

Bot.change_presence(activity=discord.Game("Test"))

#class DCS(commands.Cog, name="dcs"):
#    def __init__(self, bot):
#        self.bot = bot
#
#
#    async def status_task():
#	    while True:
#		    await bot.change_presence(activity=discord.Game("Test"))

#    async def set_presence(self, status, server_key):
#        await self.bot.wait_until_ready()
#        server_data = self.key_data[server_key]
#        game="{} players on {} playing on {}".format(status["players"], server_data["alias"], status["missionName"])
#        health=self.determine_health(status, server_key)
#        bot_status=discord.Status.online
#        if health.status == "Unhealthy":
#            bot_status=discord.Status.idle
#            game="Slow updates - " + game
#        elif health.status == "Offline":
#            bot_status=discord.Status.dnd
#            game="{} Server offline".format(server_data["alias"])
#        await self.bot.change_presence(status=bot_status, game=discord.Game(name=game))



    #@commands.command(name="dcs")
    #async def help(self, context):
    #    # Note that commands made only for the owner of the bot are not listed here.
    #    embed = discord.Embed(
    #        title="Bot",
    #        description="List of commands are:",
    #        color=0x00FF00
    #    )
    #    embed.add_field(
    #        name="Invite",
    #        value=f"Usage: {config.BOT_PREFIX}invite",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Server",
    #        value=f"Usage: {config.BOT_PREFIX}server",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Poll",
    #        value=f"Usage: {config.BOT_PREFIX}poll <Idea>",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="8ball",
    #        value=f"Usage: {config.BOT_PREFIX}8ball <Question>",
    #        inline=False)
    #    embed.add_field(
    #        name="Bitcoin",
    #        value=f"Usage: {config.BOT_PREFIX}bitcoin",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Info",
    #        value=f"Usage: {config.BOT_PREFIX}info",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Kick",
    #        value=f"Usage: {config.BOT_PREFIX}kick <User> <Reason>",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Ban",
    #        value=f"Usage: {config.BOT_PREFIX}ban <User> <Reason>",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Warn",
    #        value=f"Usage: {config.BOT_PREFIX}warn <User> <Reason>",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Purge",
    #        value=f"Usage: {config.BOT_PREFIX}purge <Number>",
    #        inline=False
    #    )
    #    embed.add_field(
    #        name="Help",
    #        value=f"Usage: {config.BOT_PREFIX}help",
    #        inline=False
    #    )
    #    await context.send(embed=embed)

def setup(bot):
    bot.add_cog(DCS(bot))