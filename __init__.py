import asyncio
import os
import discord
from discord.ext import commands

import game

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')

@bot.event
async def on_ready():
	print('Logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')

@bot.event
async def on_message(message):
	if message.author.id == bot.user.id:
		return
	await bot.process_commands(message)

@bot.command(name='startgame')
async def start_drawful_game(ctx, rounds=2):
	session = game.Game(bot, ctx, rounds=int(rounds))
	while session.running:
			await session.get_players()

bot.run(os.environ["DRAWFUL_TOKEN"])