import asyncio
import os
import discord
import time

import database

class Game:
	def __init__(self, bot, message, mode="Default", rounds=2):
		self.bot = bot
		self.players = []
		self.message = message
		self.rounds = rounds
		self.mode = mode
		self.running = True
		self.modes = ["Default", "Use custom prompts"]

	async def get_players(self):
		started = False

		await self.choose_mode()
		startmsg = 'Game starting! Type **"y"** to join! Type **"start"** to start.'
		playermsg = await self.message.channel.send('{}\nPlayers: '.format(startmsg))

		while not started:
			players_str = ""
			msg = await self.bot.wait_for('message')
			if msg.content == "y":
				self.players.append(msg.author)
				for player in self.players:
					players_str += player.mention + " "
				await playermsg.edit(content='{}\nPlayers: {}'.format(startmsg, players_str))
			if msg.content == "start" and self.is_author(msg):
				started = True

	async def start_game(self):
		pass
		#create new round object and go from there

	async def choose_mode(self):
		await self.display_mode_select()

		timer = 30
		timer_message = await self.message.send("{} seconds left!".format(timer))

		while timer > 0:
			await timer_message.edit(content="{} seconds left!".format(timer))
			try:
				msg = await self.bot.wait_for('message', check=self.is_author, timeout=1)
				self.change_mode(msg.content)
				timer = -1
			except asyncio.TimeoutError:
				timer -= 1
			except (IndexError, ValueError):
				await self.message.channel.send("Invalid mode! Please choose from 1-2.")

		await timer_message.edit(content="Time's up!")
		await self.message.channel.send("Game mode is: **{}**".format(self.mode))
		time.sleep(2)

	def change_mode(self, modenumber):
		mode_index = int(modenumber)
		self.mode = self.modes[mode_index-1]

	async def display_mode_select(self):
		modes_output = "**Please select a mode:**\n"
		i = 1
		for mode in self.modes:
			modes_output += "({}) {}\n".format(i, mode)
			i += 1
		await self.message.channel.send(modes_output)

	############### CHECKS #####################

	def is_author(self, ctx):
		return self.message.author ==  ctx.author

class Prompt:
	def __init__(self, author, content):
		pass

class Player:
	def __init__(self, user, score, prompts, images):
		pass

class ImageEntry:
	def __init__(self, author, image, prompt):
		pass

class Round:
	def __init__(self, bot, players):
		pass
