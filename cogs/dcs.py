import os, sys, discord, mysql.connector, json, asyncio, csv
from discord.ext import commands, tasks
if not os.path.isfile("config.py"):
    sys.exit("'config.py' not found! Please add it and try again.")
else:
    import config

# setup connector with values from config.py
db = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    database=config.DB_DATABASE,
    )

# to allow lookup values to update when changed in mysql
db.autocommit = True

def getServerStatus(instance):
    conn = db.cursor()
    conn.execute("SELECT * from pe_dataraw WHERE pe_dataraw_type = 1 AND pe_dataraw_instance = "+str(instance))
    myresult = conn.fetchone()
    playerCount = json.loads(myresult[2])["c_players"]
    playerCount = playerCount - 1

    conn.execute("SELECT * from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = "+str(instance))
    myresult = conn.fetchone()
    currentMission = json.loads(myresult[2])["mission"]["name"]

    return playerCount, currentMission

def getMissionList():
    conn = db.cursor()
    conn.execute("SELECT pe_DataMissionHashes_id,pe_DataMissionHashes_hash from pe_datamissionhashes WHERE pe_DataMissionHashes_instance = 1 ORDER BY pe_DataMissionHashes_id DESC LIMIT 10") 
    missionList = conn.fetchall()
    return missionList 

def getAttendance(mission_id):
    conn = db.cursor()
    conn.execute("SELECT pe_LogStats_playerid,pe_LogStats_typeid from pe_logstats WHERE pe_LogStats_masterslot <> -1 AND pe_LogStats_missionhash_id = "+str(mission_id)) 
    userList = conn.fetchall()
    userDict = dict(userList)
    userIDlist = {}
    planeIDlist = {}

    for keys in userDict.keys():
        conn = db.cursor()
        conn.execute("SELECT pe_DataPlayers_id,pe_DataPlayers_lastname from pe_dataplayers WHERE pe_DataPlayers_id="+str(keys))
        userID = conn.fetchall()
        userIDlist.update(userID)

    for values in userDict.values():
        conn = db.cursor()
        conn.execute("SELECT pe_DataTypes_id,pe_DataTypes_name from pe_datatypes WHERE pe_DataTypes_id="+str(values))
        planeID = conn.fetchall()
        planeIDlist.update(planeID)

    pilotDict = {userIDlist.get(k, k):v for k, v in userDict.items()}
    attendance = {k: planeIDlist.get(v, v) for k, v in pilotDict.items()}
    return attendance

def getMissionStatus(instance):
    conn = db.cursor()
    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = "+str(instance))
    myresult = conn.fetchone()
    playerName = json.loads(myresult[0])["players"]

    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 101 AND pe_dataraw_instance = "+str(instance))
    myresult = conn.fetchone()
    lotatcName = json.loads(myresult[0])

    return playerName, lotatcName


class DCS(commands.Cog, name="dcs"):
    def __init__(self, bot):
        self.bot = bot
        self.change_status.start()

    @tasks.loop(seconds=10)
    async def change_status(self):
        for i in range(1, 4):
            await asyncio.sleep(5)
            playerCount = getServerStatus(i)[0]
            currentMission = getServerStatus(i)[1]           
            if i == 1:
                game = f"{playerCount} players in 40th Mission Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=game))
            elif i == 2:
                game = f"{playerCount} players in 40th Training Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=game))
            else:
                game = f"{playerCount} players in 40th Dynamic Server playing {currentMission}" 
                await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=game))                  
            
            

    @commands.command(name="mlist")
    async def mlist(self, context):
        mlist = getMissionList()
        fmlist = '\n'.join(f"{line[0]}, '{line[1]}'" for line in mlist)
        embed = discord.Embed(
            color=0x00FF00
        )
        embed.add_field(
            name="Mission List",
            value=fmlist,
            inline=False
        )

        embed.set_footer(
            text=f"request by {context.message.author}"
        )
        await context.send(embed=embed)
    
    @commands.command(name="attendance")
    async def attendance(self, context, *args):
        mission_number = "".join(args)
        ulist = getAttendance(mission_number)
        fulist = '\n'.join(f"{line[0]}, '{line[1]}'" for line in ulist.items())
        with open('attendance.csv', 'w')  as f:
            for key in ulist.keys():
                f.write("%s,%s\n"%(key,ulist[key]))
        file = discord.File("attendance.csv", filename="attendance.csv")

        embed = discord.Embed(
            color=0x00FF00
        )
        embed.add_field(
            name="Mission Attendance",
            value=fulist,
            inline=False
        )
        embed.set_footer(
            text=f"request by {context.message.author}"
        )
        await context.send(file=file, embed=embed)

    @commands.command(name="status")
    async def status(self, context):

        for i in range(1, 4):
            pLen = len(getMissionStatus(i)[0])
            currentMission = getServerStatus(i)[1]           
            if i == 1:   
                embed = discord.Embed(
                title="40thsoc.org - Mission Server",
                color=0x00FF00
                )
                embed.add_field(
                    name="Current Mission",
                    value=str(currentMission),
                    inline=False
                )
                for p in range(1, pLen):
                    embed.add_field(
                        name="Connected Pilots",
                        value=getMissionStatus(i)[0][p]["name"],
                        inline=False
                    )
                for x in json.loads(getMissionStatus(i)[1])["clients"]["blue"]:
                    embed.add_field(
                        name="Connected LotATC",
                        value=x['name'],
                        inline=False
                    )
                        
            elif i == 2:
                embed2 = discord.Embed(
                title="40thsoc.org - Training Server",
                color=0x00FF00
                )
                embed2.add_field(
                    name="Current Mission",
                    value=str(currentMission),
                    inline=False
                )
                for p in range(1, pLen):
                    embed2.add_field(
                        name="Connected Pilots",
                        value=getMissionStatus(i)[0][p]["name"],
                        inline=False
                    )
                for x in json.loads(getMissionStatus(i)[1])["clients"]["blue"]:
                    embed2.add_field(
                        name="Connected LotATC",
                        value=x['name'],
                        inline=False
                    )

            else:
                embed3 = discord.Embed(
                title="40thsoc.org - Dynamic Server",
                color=0x00FF00
                )
                embed3.add_field(
                    name="Current Mission",
                    value=str(currentMission),
                    inline=False
                )
                for p in range(1, pLen):
                    embed3.add_field(
                        name="Connected Pilots",
                        value=getMissionStatus(i)[0][p]["name"],
                        inline=False
                    )
                for x in json.loads(getMissionStatus(i)[1])["clients"]["blue"]:
                    embed3.add_field(
                        name="Connected LotATC",
                        value=x['name'],
                        inline=False
                    )  

        await context.send(embed=embed)
        await context.send(embed=embed2)
        await context.send(embed=embed3)

def setup(bot):
    bot.add_cog(DCS(bot))