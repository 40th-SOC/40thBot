import os, sys, discord, mysql.connector, json
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
        while True:
            for i in range(1, 4):
                playerCount = getPlayerCount(i)
                currentMission = getCurrentMission(i)
                game = f"{playerCount} players in {currentMission}"
                await self.bot.change_presence(activity=discord.Game(game))


'''
    async def set_presence(self, status, server_key):
        await self.bot.wait_until_ready()
        server_data = self.key_data[server_key]
        game="{} players on {} playing on {}".format(status["players"], server_data["alias"], status["missionName"])
        health=self.determine_health(status, server_key)
        bot_status=discord.Status.online
        if health.status == "Unhealthy":
            bot_status=discord.Status.idle
            game="Slow updates - " + game
        elif health.status == "Offline":
            bot_status=discord.Status.dnd
            game="{} Server offline".format(server_data["alias"])
        await self.bot.change_presence(status=bot_status, game=discord.Game(name=game))

    async def get_status(self, key):
        url = self.base_url + key
        resp = await self.session.get(url)
        if (resp.status != 200):
            raise ErrorGettingStatus(resp.status)
        status = json.loads(await resp.text())
        #Hoggy Server counts himself among the players.
        status["players"] = status["players"] - 1
        status["maxPlayers"] = status["maxPlayers"] - 1
        return status

    def determine_health(self, status, server_key):
        last_update = arrow.get(status["updateTime"])
        return ServerHealth(last_update, server_key)

    def humanize_time(self, updateTime):
        arrowtime = arrow.get(updateTime)
        return arrowtime.humanize()

    def get_mission_time(self, status):
        time_seconds = datetime.timedelta(seconds=status["data"]["uptime"])
        return str(time_seconds).split(".")[0]
'''

def setup(bot):
    bot.add_cog(DCS(bot))