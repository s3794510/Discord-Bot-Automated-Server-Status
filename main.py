import discord
from discord.ext import commands, tasks
import requests
import asyncio
import botdb
import botinstancecontrol as botinstance

# Update DB parameters: Channel ID
botdb.create_item('channel_id', 593560627985907730)
if not botdb.exist_item('msg_id'):
  botdb.create_item('msg_id', '')

channel_id = botdb.read_item('channel_id')
command_prefixes = ["!!","$$","%%","@@", "##", "hey dogo ", "Hey dogo", "Hey Dogo", "hey Dogo"]
server_admin_role = botdb.read_item('server-admin-role')

# Necessary role to use Server Administration commands
if (server_admin_role == None):
  server_admin_role = 'admin'

intents = discord.Intents.all()
intents.messages = True  # Enable reading and writing messages
intents.webhooks = True  # Enable webhooks

# Create an instance of the bot
bot = commands.Bot(command_prefix=command_prefixes, intents = intents)


#########################################################
# Handling command errors
@bot.event
async def on_command_error(ctx, error):
    # If command is called by users without the right roles
    if isinstance(error, commands.MissingRole):
      await ctx.send(f"You don't have the required role ({server_admin_role}) to use this command.")
      return
  # If command is invalid
    if isinstance(error, commands.CommandNotFound):
      await ctx.send("Invalid command. Please use the help command for a list of available commands.")
      await ctx.send_help(ctx.command)
    # If command called in the incorrect channels
    if isinstance(error, commands.CheckFailure):
      await ctx.send("Commands can only be used in the 'bot' channel.")
      return
    if isinstance(error, commands.MissingRequiredArgument):
      await ctx.send("Missing required argument. Please complete your command.")
      return
    


#############################################################
# Bot Beheviours
# Event: Bot is ready and connected to Discord
@bot.event
async def on_ready():
  await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing, name=botdb.read_item('activitystatus')))
  fetch_data.start()
  print(f'Logged in as {bot.user.name} ({bot.user.id})')
  print('Bot is ready to receive commands')
  
# Run async function
def run_async_function():
    asyncio.run(fetch_data())

# Check if command in the specific channel with exact name
def in_bot_channel(name):
    async def predicate(ctx):
        return ctx.channel.name == name
    return commands.check(predicate)


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
  #instance_id_list = []
  for instance in data:
    instance_id = instance['Instance ID']
    #instance_id_list.append(instance_id)
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
@bot.command(category='TEST')
async def hello(ctx):
    """(TEST COMMAND)"""
    await ctx.send(f'Hello {ctx.author.name}!')


# Command: Say
@bot.command(category='TEST')
@in_bot_channel('bot')
async def say(ctx, *, message):
  """(TEST COMMAND) Return the message after command."""
  await ctx.send(message)

# Command: Start Instance
@bot.command(category='Instance Control')
@commands.has_role(server_admin_role)
@in_bot_channel('bot')
async def start_instance(ctx, message):
    """Start the instance based on ID"""
    instance_id = message
    start_response = botinstance.start_instance(instance_id)
    if start_response is None:
      await ctx.send(f"Error: Instance with ID: '{instance_id}' does not exist.")
      return
    await ctx.send(f"Starting instance: {instance_id}")
    return

# Commands: Stop Instance
@bot.command(category='Instance Control')
@commands.has_role(server_admin_role)
@in_bot_channel('bot')
async def stop_instance(ctx, message):
    """Stop the instance based on ID"""
    instance_id = message
    stop_response = botinstance.stop_instance(instance_id)
    if stop_response is None:
      await ctx.send(f"Error: Instance with ID: '{instance_id}' does not exist.")
      return
    await ctx.send(f"Stopping instance: {instance_id}")
    return

# Command: List Instance
@bot.command(category='Instance Control')
@commands.has_role(server_admin_role)
@in_bot_channel('bot')
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