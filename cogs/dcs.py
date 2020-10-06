import os, sys, discord, mysql.connector, json, asyncio
from discord.ext import commands, tasks
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
db.autocommit = True

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

class DCS(commands.Cog, name="dcs"):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):
        for i in range(1, 4):
            playerCount = getPlayerCount(i)
            currentMission = getCurrentMission(i)
            game = f"{playerCount} players in {currentMission}"
            await self.bot.change_presence(activity=discord.Game(game))
            await asyncio.sleep(5)



def setup(bot):
    bot.add_cog(DCS(bot))