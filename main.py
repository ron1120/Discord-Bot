import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import json
import random


load_dotenv()
token = "MTM3NzcwNzc2Njg1NjI5MDMwNA.GJEyah.NK4Dmi4we06U4LL5Glx6TN5KNchd_LcNbKZvoQ"
print("MTM3NzcwNzc2Njg1NjI5MDMwNA.GJEyah.NK4Dmi4we06U4LL5Glx6TN5KNchd_LcNbKZvoQ", token)  # Debug — remove after confirming it works

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f"We are ready to go in, {bot.user.name}")


@bot.event
async def on_member_join(member):
    await member.send(f"Welcome to the server{member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} dont use that word")

    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello, {ctx.author.display_name}!")







### !gamble
###





## CHECK ID

@bot.command()
async def userid(ctx):
    user_id = ctx.author.id
    await ctx.send(f"🪪 Your Discord user ID is: `{user_id}`")


bot.run(token, log_handler=handler, log_level=logging.DEBUG)