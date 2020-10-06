import discord, asyncio, os, platform, sys, json, mysql.connector
from discord.ext.commands import Bot
from discord.ext import commands
if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

bot = Bot(command_prefix=config.BOT_PREFIX)
db = mysql.connector.connect(
    host=config.DB_HOST,
    user=config.DB_USERNAME,
    password=config.DB_PASSWORD,
    database=config.DB_DATABASE,
    )

# The code in this even is executed when the bot is ready
@bot.event
async def on_ready():
	bot.loop.create_task(status_task())
	print(f"Logged in as {bot.user.name}")
	print(f"Discord.py API version: {discord.__version__}")
	print(f"Python version: {platform.python_version()}")
	print(f"Running on: {platform.system()} {platform.release()} ({os.name})")
	print("-------------------")	

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

# Setup the game status task of the bot
async def status_task():
	server1 = str(getPlayerCount(1)) + " players in 40th Mission Server playing " + str(getCurrentMission(1))
	server2 = str(getPlayerCount(2)) + " players in 40th Training Server playing " + str(getCurrentMission(2))
	server3 = str(getPlayerCount(3)) + " players in 40th Dynamic Server playing " + str(getCurrentMission(3))

	while True:
 		await bot.change_presence(activity=discord.Game(server1))
 		await asyncio.sleep(10)
 		await bot.change_presence(activity=discord.Game(server2))
 		await asyncio.sleep(10)
 		await bot.change_presence(activity=discord.Game(server3))
 		await asyncio.sleep(5)


# Removes the default help command of discord.py to be able to create our custom help command.
bot.remove_command("help")

if __name__ == "__main__":
	for extension in config.STARTUP_COGS:
		try:
			bot.load_extension(extension)
			extension = extension.replace("cogs.", "")
			print(f"Loaded extension '{extension}'")
		except Exception as e:
			exception = f"{type(e).__name__}: {e}"
			extension = extension.replace("cogs.", "")
			print(f"Failed to load extension {extension}\n{exception}")

# The code in this event is executed every time someone sends a message, with or without the prefix
@bot.event
async def on_message(message):
	# Ignores if a command is being executed by a bot or by the bot itself
	if message.author == bot.user or message.author.bot:
		return
	else:
		if message.author.id not in config.BLACKLIST:
			# Process the command if the user is not blacklisted
			await bot.process_commands(message)
		else:
			# Send a message to let the user know he's blacklisted
			context = await bot.get_context(message)
			embed = discord.Embed(
				title="You're blacklisted!",
				description="Ask the owner to remove you from the list if you think it's not normal.",
				color=0x00FF00
			)
			await context.send(embed=embed)

# The code in this event is executed every time a command has been *successfully* executed
@bot.event
async def on_command_completion(ctx):
	fullCommandName = ctx.command.qualified_name
	split = fullCommandName.split(" ")
	executedCommand = str(split[0])
	print(f"Executed {executedCommand} command in {ctx.guild.name} by {ctx.message.author} (ID: {ctx.message.author.id})")

# The code in this event is executed every time a valid commands catches an error
@bot.event
async def on_command_error(context, error):
	if isinstance(error, commands.CommandOnCooldown):
		embed = discord.Embed(
			title="Error!",
			description="This command is on a %.2fs cooldown" % error.retry_after,
			color=0x00FF00
		)
		await context.send(embed=embed)
	raise error

# Run the bot with the token
bot.run(config.TOKEN)
