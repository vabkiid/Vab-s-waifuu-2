import discord
from discord.ext import commands
import datetime
import os
import time
from keep_alive import keep_alive

start_time = time.time()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="_", intents=intents)

deleted_messages = {}

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_message_delete(message):
    if message.author.bot or not message.content:
        return

    now = datetime.datetime.utcnow()
    channel_id = message.channel.id
    entry = (message.content, message.author.name, now)

    if channel_id not in deleted_messages:
        deleted_messages[channel_id] = []

    deleted_messages[channel_id].append(entry)

    # Keep only messages from last 48 hours
    deleted_messages[channel_id] = [
        msg for msg in deleted_messages[channel_id]
        if (now - msg[2]).total_seconds() < 48 * 3600
    ]

@bot.command()
async def snipe(ctx):
    channel_id = ctx.channel.id
    now = datetime.datetime.utcnow()

    if channel_id not in deleted_messages or not deleted_messages[channel_id]:
        await ctx.send("🚫 No deleted messages in the last 48 hours.")
        return

    messages_to_show = deleted_messages[channel_id][-10:]  # last 10 messages
    embed = discord.Embed(title="🕵️ Last Deleted Messages", color=discord.Color.orange())

    for i, (content, author, time) in enumerate(reversed(messages_to_show), 1):
        minutes_ago = int((now - time).total_seconds() / 60)
        embed.add_field(
            name=f"{i}. {author} ({minutes_ago} min ago)",
            value=content if content else "*[No content]*",
            inline=False
        )

    await ctx.send(embed=embed)

@bot.command()
async def privacy(ctx):
    embed = discord.Embed(
        title="🔐 Privacy & Security",
        description="This bot does **not store messages** permanently. Deleted messages are cached for 42–48 hours **in memory only**.\n\nNo personal data is logged or shared.",
        color=discord.Color.green()
    )
    embed.add_field(name="Encryption?", value="Your token is safe in `.env`, and Replit uses HTTPS encryption.")
    embed.set_footer(text="DM the developer for more info.")
    await ctx.send(embed=embed)

@bot.command()
async def uptime(ctx):
    current_time = time.time()
    uptime_seconds = int(current_time - start_time)

    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    msg = f"🟢 Bot has been online for "
    if days: msg += f"**{days}d** "
    if hours: msg += f"**{hours}h** "
    if minutes: msg += f"**{minutes}m** "
    msg += f"**{seconds}s**"

    await ctx.send(msg)

@bot.command()
async def invite(ctx):
    invite_url = "https://discord.com/oauth2/authorize?client_id=1392559062331424929&permissions=3072&scope=bot"

    embed = discord.Embed(
        title="🤖 Invite This Bot",
        description=f"[Click here to invite me to your server!]({invite_url})",
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Invite powered by Vab's Waifu 🔗")
    
    await ctx.send(embed=embed)

keep_alive()  # ✅ keeps the bot running 24/7
bot.run(os.getenv("TOKEN"))