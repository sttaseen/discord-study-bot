from discord.ext import commands, tasks
import discord
from datetime import datetime, timedelta
import schedule
import database
import asyncio
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

    # Schedule the job to check for tomorrow's birthdays
    schedule.every().day.at("23:50").do(lambda: asyncio.create_task(check_tomorrows_birthdays()))

    run_schedule.start()

@bot.command(name='addbday')
async def add_birthday(ctx, member_or_name, date: str):
    # Handle both cases: Discord mention or name
    member = None
    if member_or_name.startswith('<@') and member_or_name.endswith('>'):
        member_id = int(member_or_name.strip('<@!>'))
        member = ctx.guild.get_member(member_id)
        name = member.display_name
        user_id = str(member.id)
    else:
        name = member_or_name
        user_id = None

    try:
        birthday = datetime.strptime(date, '%m-%d')
        month = birthday.month
        day = birthday.day
        database.add_birthday(user_id, name, month, day)
        await ctx.send(f'Birthday for {name.capitalize()} added successfully!')
    except ValueError:
        await ctx.send('Invalid date format. Use MM-DD.')

@bot.command(name='getbday')
async def get_birthday(ctx, member_or_name):
    # Handle both cases: Discord mention or name
    member = None
    if member_or_name.startswith('<@') and member_or_name.endswith('>'):
        member_id = int(member_or_name.strip('<@!>'))
        member = ctx.guild.get_member(member_id)
        user_id = str(member.id)
    else:
        user_id = None
        member = None

    birthday = database.get_birthday(user_id, member_or_name)
    if birthday:
        month, day = birthday
        name = member.display_name if member else member_or_name
        await ctx.send(f'{name}\'s birthday is on {month:02d}-{day:02d}.')
    else:
        name = member.display_name if member else member_or_name
        await ctx.send(f'No birthday found for {name}.')

@bot.command(name='deletebday')
async def delete_birthday(ctx, member_or_name):
    # Handle both cases: Discord mention or name
    member = None
    if member_or_name.startswith('<@') and member_or_name.endswith('>'):
        member_id = int(member_or_name.strip('<@!>'))
        member = ctx.guild.get_member(member_id)
        user_id = str(member.id)
    else:
        user_id = None
        member = None

    database.delete_birthday(user_id, member_or_name)
    name = member.display_name if member else member_or_name
    await ctx.send(f'Birthday for {name} has been removed.')

@bot.command(name='listbdays')
async def list_birthdays(ctx):
    guild = bot.guilds[0]  # Assuming bot is only in one guild
    birthdays = database.get_all_birthdays()
    
    if birthdays:
        await ctx.author.send("## Birthdays 🥳")

        for user_id, (name, month, day) in birthdays.items():
            member = discord.utils.get(guild.members, id=int(user_id)) if user_id else None
            
            if member:
                avatar_url = member.avatar.url if member.avatar else member.default_avatar.url
                
                embed = discord.Embed(title=f"{member.display_name}", color=discord.Color.blue())
                embed.add_field(name="Birthday", value=f"{month:02d}-{day:02d}", inline=False)
                embed.set_thumbnail(url=avatar_url)
                
                await ctx.author.send(embed=embed)  # Sending DM to the command invoker
            else:
                await ctx.author.send(f'{name}: {month:02d}-{day:02d}')
        
        await ctx.send("Birthday list sent via DM!")  # Inform the user that the list has been sent
    else:
        await ctx.send('No birthdays found.')

async def check_tomorrows_birthdays():
    # Send birthday reminders via DM for tomorrow's birthdays
    tomorrow = datetime.now() + timedelta(days=1)
    birthdays_tomorrow = database.get_birthdays_by_date(tomorrow.month, tomorrow.day)
    guild = bot.guilds[0]
    if birthdays_tomorrow:
        for member in guild.members:
            if member.bot:
                continue
            try:
                for user_id, name in birthdays_tomorrow:
                    birthday_member = discord.utils.get(guild.members, id=int(user_id)) if user_id else None
                    birthday_name = birthday_member.display_name if birthday_member else name
                    await member.send(f'Psst.. It\'s {birthday_name}\'s birthday tomorrow!')
            except discord.Forbidden:
                print(f"Couldn't send DM to {member.display_name}. They might have DMs disabled.")
            except Exception as e:
                print(f"Error sending DM to {member.display_name}: {e}")

@tasks.loop(minutes=1)
async def run_schedule():
    schedule.run_pending()

@tasks.loop(hours=24)
async def check_birthdays():
    # Send birthday announcements
    birthdays_today = database.get_birthdays_today()
    guild = bot.guilds[0]
    if birthdays_today:
        channel = bot.get_channel(CHANNEL_ID)
        if channel is not None:
            for user_id, name in birthdays_today:
                member = discord.utils.get(guild.members, id=int(user_id)) if user_id else None
                if member:
                    await channel.send(f'@everyone Happy Birthday to {member.display_name}! 🥳')
                else:
                    await channel.send(f'@everyone Happy Birthday to {name}! 🥳')
        else:
            print("Channel not found!")

# Run the bot with your token
bot.run(BOT_TOKEN)
