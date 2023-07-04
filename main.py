import discord
from discord.ext import commands, tasks
import os
import requests
import asyncio
import botdb

#from keep_alive import keep_alive
#keep_alive()

# Replit db: Create pair
def create_keypair(key, value):
  replit.db[key]=value
  print(f'DB updated for {key}.')

# Update DB parameters: Channel ID
create_keypair('channel_id', 593560627985907730)
create_keypair('msg_id', '')

channel_id = replit.db['channel_id']
command_prefixes = ["@", "%", "hey dogo ", "Hey dogo", "Hey Dogo", "hey Dogo"]

intents = discord.Intents.all()
intents.messages = True  # Enable reading and writing messages
intents.webhooks = True  # Enable webhooks

# Create an instance of the bot
bot = commands.Bot(command_prefix=command_prefixes, intents = intents)


# Event: Bot is ready and connected to Discord
@bot.event
async def on_ready():
  print(f'Logged in as {bot.user.name} ({bot.user.id})')
  print('Bot is ready to receive commands')
  fetch_data.start()
  

def run_async_function():
    asyncio.run(fetch_data())

# Command: Hello
@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.name}!')


# Command: Say
@bot.command()
async def say(ctx, *, message):
  await ctx.send(message)


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
    if (replit.db['msg_id'] == ''):
      sent_msg = await channel.send(status_msg)
      replit.db['msg_id'] = sent_msg.id
      print(f"New Status Message sent. Message ID: {sent_msg.id}.")
      
    if instance['Instance ID'] not in replit.db: 
      create_keypair(instance_id, instance)
    else:
      if new_status != replit.db[instance_id]['Instance Status']:
        await edit_message(replit.db['msg_id'], status_msg)
        create_keypair(instance_id, instance)
        print(f"Status of instance {instance_id} is changed and has been updated.")
    
    
    
  print('SUCCESSED Fetched and sent servers statuses')
    
# Bot: Edit mesagge
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



bot.run(botdb.get_bottoken())
