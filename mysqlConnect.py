import mysql.connector, json, time

db = mysql.connector.connect(
    host="192.168.13.6",
    user="perun",
    password="dcsded",
    database="perun"
    )
db.autocommit = True

def getPlayerlist():
    mycursor = db.cursor()
    mycursor.execute("SELECT pe_DataPlayers_id,pe_DataPlayers_lastname FROM pe_dataplayers")
    myresult = mycursor.fetchall()
    return myresult

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
    myresult = mycursor.fetchall()
    return myresult 

#while True:
#    for i in range(1, 4):
#        playerCount = getPlayerCount(i)
#        currentMission = getCurrentMission(i)
#        time.sleep(5)
#        print(playerCount)
#        print(currentMission)
mission_list = getMissionList()
print(mission_list)