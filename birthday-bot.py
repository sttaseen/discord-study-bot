from discord.ext import commands, tasks
import discord
from datetime import datetime
import database
from config import *

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')
    channel = bot.get_channel(CHANNEL_ID)
    if channel is not None:
        await channel.send("Hello! Birthday bot is ready.")
    else:
        print("Channel not found!")

    # Start the task to check for today's birthdays
    check_birthdays.start()

@bot.command(name='addbday')
async def add_birthday(ctx, member: discord.Member, date: str):
    user_id = str(member.id)
    name = member.display_name
    try:
        # Convert the string to a month and day
        birthday = datetime.strptime(date, '%m-%d')
        month = birthday.month
        day = birthday.day
        database.add_birthday(user_id, name, month, day)
        await ctx.send(f'Birthday for {name.capitalize()} added successfully!')
    except ValueError:
        await ctx.send('Invalid date format. Use MM-DD.')

@bot.command(name='getbday')
async def get_birthday(ctx, member: discord.Member):
    user_id = str(member.id)
    birthday = database.get_birthday(user_id)
    if birthday:
        month, day = birthday
        await ctx.send(f'{member.display_name}\'s birthday is on {month:02d}-{day:02d}.')
    else:
        await ctx.send(f'No birthday found for {member.display_name}.')

@bot.command(name='deletebday')
async def delete_birthday(ctx, member: discord.Member):
    user_id = str(member.id)
    database.delete_birthday(user_id)
    await ctx.send(f'Birthday for {member.display_name} has been removed.')

@bot.command(name='listbdays')
async def list_birthdays(ctx):
    guild = bot.guilds[0]  # Assuming bot is only in one guild
    birthdays = database.get_all_birthdays()
    
    if birthdays:
        await ctx.author.send("## Birthdays 🥳")

        for user_id, (name, month, day) in birthdays.items():
            member = discord.utils.get(guild.members, id=int(user_id))
            
            if member:
                avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                
                embed = discord.Embed(title=f"{member.display_name}", color=discord.Color.blue())
                embed.add_field(name="Birthday", value=f"{month:02d}-{day:02d}", inline=False)
                embed.set_thumbnail(url=avatar_url)
                
                await ctx.author.send(embed=embed)  # Sending DM to the command invoker
            else:
                await ctx.author.send(f'Unknown User (ID: {user_id}): {month:02d}-{day:02d}')
        
        await ctx.send("Birthday list sent via DM!")  # Inform the user that the list has been sent
    else:
        await ctx.send('No birthdays found.')

@tasks.loop(hours=24)
async def check_birthdays():
    # Send birthday announcements
    birthdays_today = database.get_birthdays_today()
    guild = bot.guilds[0]
    if birthdays_today:
        channel = bot.get_channel(CHANNEL_ID)
        if channel is not None:
            for user_id in birthdays_today:
                member = discord.utils.get(guild.members, id=int(user_id))
                if member:
                    await channel.send(f'@everyone Happy Birthday to {member.display_name}! 🥳')
                else:
                    await channel.send(f'@everyone Happy Birthday to Unknown User (ID: {user_id})! 🥳')
        else:
            print("Channel not found!")

# Run the bot with your token
bot.run(BOT_TOKEN)
