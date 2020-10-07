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

def getMissionList():
    mycursor = db.cursor()
    mycursor.execute("SELECT pe_DataMissionHashes_id,pe_DataMissionHashes_hash from pe_datamissionhashes ORDER BY pe_DataMissionHashes_id DESC LIMIT 10") 
    missionList = mycursor.fetchall()
    return missionList 

def getAttendance(mission_id):
    mycursor = db.cursor()
    mycursor.execute("SELECT pe_LogStats_playerid,pe_LogStats_typeid from pe_logstats WHERE pe_LogStats_masterslot <> -1 AND pe_LogStats_missionhash_id = "+str(mission_id)) 
    userList = mycursor.fetchall()
    return userList


class DCS(commands.Cog, name="dcs"):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):
        for i in range(1, 4):
            await asyncio.sleep(5)
            playerCount = getPlayerCount(i)
            currentMission = getCurrentMission(i)           
            if i == 1:
                game = f"{playerCount} players in 40th Mission Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(game))
            elif i == 2:
                game = f"{playerCount} players in 40th Training Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(game))
            else:
                game = f"{playerCount} players in 40th Dynamic Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(game))                  
            
            

    @commands.command(name="missionlist")
    async def missionlist(self, context):
        embed = discord.Embed(
            color=0x00FF00
        )
        embed.add_field(
            name="Recent Mission List",
            value=getMissionList(),
            inline=False
        )
        embed.set_footer(
            text=f"request by {context.message.author}"
        )
        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(DCS(bot))