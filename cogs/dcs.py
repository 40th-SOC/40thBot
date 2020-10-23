import os, sys, discord, mysql.connector, json, asyncio, csv, datetime
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

conn = db.cursor()
db.autocommit = True

def getServerStatus(instance):

    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 1 AND pe_dataraw_instance = %s", (instance,))
    myresult = conn.fetchone()
    playerCount = json.loads(myresult[0])["c_players"]
    playerCount = playerCount - 1
    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = %s", (instance,))
    myresult = conn.fetchone()
    currentMission = json.loads(myresult[0])["mission"]["name"]
    
    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = %s", (instance,))
    myresult = conn.fetchone()
    missionTime = json.loads(myresult[0])["mission"]["modeltime"]
    missionTime = str(datetime.timedelta(seconds=int(missionTime)))
    missionTime = missionTime.split(".",maxsplit=1)[0]

    return playerCount, currentMission, missionTime

def getMissionList():
    conn.execute("SELECT pe_DataMissionHashes_id,pe_DataMissionHashes_hash from pe_datamissionhashes WHERE pe_DataMissionHashes_instance = 1 ORDER BY pe_DataMissionHashes_id DESC LIMIT 75") 
    result = conn.fetchall()
    olist = list()
    for mission in range(0, len(result)):
        mizid = result[mission][0]
        conn.execute("SELECT pe_LogStats_missionhash_id from pe_logstats WHERE pe_LogStats_missionhash_id = %s GROUP by pe_LogStats_masterslot HAVING count(*) > 1", (mizid,))
        r = conn.fetchall()
        if len(r) > 1:
            filist = (r[0][0])
            conn.execute("SELECT pe_DataMissionHashes_id,pe_DataMissionHashes_hash from pe_datamissionhashes WHERE pe_DataMissionHashes_id = %s", (filist,))
            mlist = conn.fetchall()
            mlist = mlist[0]
            sname = str(mlist[1])
            sname = sname.split("@")
            sname = f"{sname[0]} - {sname[3]}"
            molist = list(mlist)
            molist[1] = sname
            mlist = tuple(molist)
            olist += mlist
    return olist

def getAttendance(mission_id):
    conn.execute("SELECT pe_LogStats_playerid,pe_LogStats_typeid from pe_logstats WHERE pe_LogStats_masterslot <> -1 AND pe_LogStats_missionhash_id = %s", (mission_id,)) 
    userList = conn.fetchall()
    conn.execute("SELECT pe_DataMissionHashes_hash from pe_datamissionhashes WHERE pe_DataMissionHashes_id = %s", (mission_id,)) 
    mission = conn.fetchall()
    userDict = dict(userList)
    userIDlist = {}
    planeIDlist = {}

    for keys in userDict.keys():
        conn.execute("SELECT pe_DataPlayers_id,pe_DataPlayers_lastname from pe_dataplayers WHERE pe_DataPlayers_id = %s", (keys,))
        userID = conn.fetchall()
        userIDlist.update(userID)

    for values in userDict.values():
        conn.execute("SELECT pe_DataTypes_id,pe_DataTypes_name from pe_datatypes WHERE pe_DataTypes_id = %s", (values,))
        planeID = conn.fetchall()
        planeIDlist.update(planeID)

    pilotDict = {userIDlist.get(k, k):v for k, v in userDict.items()}
    attendance = {k: planeIDlist.get(v, v) for k, v in pilotDict.items()}
    return attendance, mission

def getMissionStatus(instance):
    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 2 AND pe_dataraw_instance = %s", (instance,))
    myresult = conn.fetchone()
    playerName = json.loads(myresult[0])["players"]

    conn.execute("SELECT pe_dataraw_payload from pe_dataraw WHERE pe_dataraw_type = 101 AND pe_dataraw_instance = %s", (instance,))
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
        ulist = getAttendance(mission_number)[0]
        mission = getAttendance(mission_number)[1][0][0]
        mission = str(mission)
        mission = mission.split("@")
        fulist = '\n'.join(f"{line[0]}, '{line[1]}'" for line in ulist.items())
        with open('attendance.csv', 'w')  as f:
            for key in ulist.keys():
                f.write("%s,%s\n"%(key,ulist[key]))
        file = discord.File("attendance.csv", filename="attendance.csv")

        embed = discord.Embed(
            color=0x00FF00
        )
        embed.add_field(
            name=f"Mission Attendance for:\n*****\n{mission[0]} - {mission[3]}\n*****",
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
            uptime = getServerStatus(i)[2]           
            if i == 1:  
                buffer = ""
                for p in range(1, pLen):
                  buffer += getMissionStatus(i)[0][p]["name"] + "\n"  
                
                embed = discord.Embed(
                title="40thsoc.org - Mission Server",
                color=0x00FF00
                )
                embed.add_field(
                    name="Current Mission",
                    value=str(currentMission)+"\n Uptime - "+uptime,
                    inline=False
                )
                embed.add_field(
                    name="Connected Pilots",
                    value=buffer if len(buffer) > 0 else 'empty',
                    inline=False
                )
                for x in json.loads(getMissionStatus(i)[1])["clients"]["blue"]:
                    embed.add_field(
                        name="Connected LotATC",
                        value=x['name'],
                        inline=False
                    )
                        
            elif i == 2:
                buffer2 = ""
                for p in range(1, pLen):
                  buffer2 += getMissionStatus(i)[0][p]["name"] + "\n"  

                embed2 = discord.Embed(
                title="40thsoc.org - Training Server",
                color=0x00FF00
                )
                embed2.add_field(
                    name="Current Mission",
                    value=str(currentMission)+"\n Uptime - "+uptime,
                    inline=False
                )
                embed2.add_field(
                    name="Connected Pilots",
                    value=buffer2 if len(buffer2) > 0 else 'empty',
                    inline=False
                )
                for x in json.loads(getMissionStatus(i)[1])["clients"]["blue"]:
                    embed2.add_field(
                        name="Connected LotATC",
                        value=x['name'],
                        inline=False
                    )

            else:
                buffer3 = ""
                for p in range(1, pLen):
                  buffer3 += getMissionStatus(i)[0][p]["name"] + "\n"  

                embed3 = discord.Embed(
                title="40thsoc.org - Dynamic Server",
                color=0x00FF00
                )
                embed3.add_field(
                    name="Current Mission",
                    value=str(currentMission)+"\n Uptime - "+uptime,
                    inline=False
                )
                embed3.add_field(
                    name="Connected Pilots",
                    value=buffer3 if len(buffer3) > 0 else 'empty',
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