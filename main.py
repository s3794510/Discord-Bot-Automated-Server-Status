import discord
from discord.ext import commands, tasks
import requests
import asyncio
import botdb


# Update DB parameters: Channel ID
botdb.create_item('channel_id', 593560627985907730)
if not botdb.exist_item('msg_id'):
  botdb.create_item('msg_id', '')

channel_id = botdb.read_item('channel_id')
command_prefixes = ["@", "%", "hey dogo ", "Hey dogo", "Hey Dogo", "hey Dogo"]

intents = discord.Intents.all()
intents.messages = True  # Enable reading and writing messages
intents.webhooks = True  # Enable webhooks

# Create an instance of the bot
bot = commands.Bot(command_prefix=command_prefixes, intents = intents)




#############################################################
# Bot Beheviours
# Event: Bot is ready and connected to Discord
@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name} ({bot.user.id})')
  print('Bot is ready to receive commands')
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=botdb.read_item('activitystatus')))
  fetch_data.start()
  

def run_async_function():
    asyncio.run(fetch_data())


# Fetch data for instance status
@tasks.loop(minutes=1)
async def fetch_data():
  response = requests.get('https://c38ltc8s3a.execute-api.ap-southeast-1.amazonaws.com/default/GetEC2InstancesWithTag')
  channel = bot.get_channel(channel_id)
  # Check response
  if response.status_code != 200:
    await channel.send('Failed to fetch data from the API.')
    print('FAILED Fetched and sent servers statuses')
    return

  # Bot Actions
  data = response.json()
  for instance in data:
    instance_id = instance['Instance ID']
    new_status = instance['Instance Status']
    ip_address = instance['Public IP Address']
    status_msg = generate_status_msg(instance_id, ip_address)

    # Send new message and update database if first message has not been sent
    if (botdb.read_item('msg_id') == ''):
      sent_msg = await channel.send(status_msg)
      botdb.create_item('msg_id', sent_msg.id)
      print(f"New Status Message sent. Message ID: {sent_msg.id}.")
      
    if not botdb.exist_item(instance['Instance ID']): 
      botdb.create_item(instance_id, instance)
    else:
      if new_status != botdb.read_item(instance_id)['Instance Status']:
        await edit_message(botdb.read_item('msg_id'), status_msg)
        botdb.create_item(instance_id, instance)
        print(f"Status of instance {instance_id} is changed and has been updated.")
    
    
    
  print('SUCCESSED Fetched and sent servers statuses')
    
# Edit mesagge
async def edit_message(message_id, new_content):
    channel = bot.get_channel(channel_id)
    message = await channel.fetch_message(message_id)

    if message:
      await message.edit(content=new_content)
      print(f'Message with ID {message_id} edited successfully.')
    else:
      print(f'Message with ID {message_id} not found.')

# Generate Status Message
def generate_status_msg(instance_id, ip):
  status_msg = ""
  # Server Status
  if ip == 'N/A':
    status_msg += "```diff\n-<SERVER OFFLINE>\n```"
  else:
    status_msg += "```ini\n[<SERVER ONLINE>]\n```"

  # Server Name
  status_msg += "\n:chicken: :chicken: :chicken: **MINECRAFT SERVER ⛏**:chicken: :chicken: :chicken:\n"

  # Server IP
  status_msg += f"\nIP (non-static):\n**{ip}**\n"

  # Addtional info
  status_msg += "\nCurrent Version: 1.20.1\n"
  status_msg += "\n__Note__: **No cheats, debug, creative modes**"
  return status_msg

# Event: Bot has joined a guild (server)
@bot.event
async def on_guild_join(guild):
  print(f'Bot has joined the guild: {guild.name} ({guild.id})')


# Event: Bot has been removed from a guild (server)
@bot.event
async def on_guild_remove(guild):
  print(f'Bot has been removed from the guild: {guild.name} ({guild.id})')


#########################################################
# Bot Commands

# Command: Hello
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')


# Command: Say
@bot.command()
async def say(ctx, *, message):
  await ctx.send(message)

# Command: List Instance
@bot.command(category='Instance Control')
async def list_instances(ctx):
    """Show a lsit of available instances"""
    await ctx.send("Finding instances...")
    instance_list = botinstance.list_instances()
    response = ""
    if (len(instance_list) ==0):
       await ctx.send("No instances found.")
       return
    for instance in instance_list:
      if (instance[1] == 'Discord Bot'):
        continue
      response += f"\nInstance Name: {instance[1]}\nInstance ID: {instance[0]}\n"
    await ctx.send(response)


####################################################
# Run the bot
bot.run(botdb.get_bottoken())