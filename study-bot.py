from discord.ext import commands, tasks
import discord

BOT_TOKEN = 'MTI1NDAwMjcxMDMzNzAyODEyNw.GUOJa4.8BvdTV4Im0zEBX4W53TfnZzbte4gR5R1c6V8M4'
CHANNEL_ID = 1254004414184689694

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send("Hello! Study bot is ready.")
    else:
        print("Channel not found!")

    tasks.start()

        
@bot.command()
async def hello(ctx):
    await ctx.send("Hello!")

@bot.command()
async def add(ctx, x, y):
    await ctx.send(f"{int(x) + int(y)}")

@tasks.loop(minutes=1, count=2)
async def tasks():
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send("# Scheduled task executed!")
    else:
        print("Channel not found!")

bot.run(BOT_TOKEN)