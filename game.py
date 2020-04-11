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
				self.players.append(Player(msg.author))
				for player in self.players:
					players_str += player.user.mention + " "
				await playermsg.edit(content='{}\nPlayers: {}'.format(startmsg, players_str))
			if msg.content == "start" and self.is_author(msg):
				started = True

	async def start_game(self):
		for i in range(self.rounds):
			new_round = Round(self.bot, self.message, self.players)
			await new_round.start_round()

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

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
	##################### CHECKS #####################
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

	def is_author(self, ctx):
		return self.message.author ==  ctx.author #move all checks out after

	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#
	#################   END CHECKS   #################
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~#

class Prompt:
	def __init__(self, content, author=None):
		self.content = content
		self.author = author

class Player:
	def __init__(self, user):
		self.user = user
		self.score = 0
		self.prompt = ""
		self.image = ""

class ImageEntry:
	def __init__(self, author, image, prompt):
		pass

class Round:
	def __init__(self, bot, message, players, prompts_table="defaultprompts"):
		self.bot = bot
		self.message = message
		self.players = players
		self.prompts_table = prompts_table
		self.prompts = []
		self.images = []

	async def start_round(self):
		await self.create_prompt_list()
		await self.get_all_images()

	async def create_prompt_list(self):
		await self.perform_player_check()

		for player in self.players:
			prompt = database.get_random_prompt()

			while prompt in self.prompts:
				prompt = database.get_random_prompt()
			self.prompts.append(Prompt(prompt))
			player.prompt = prompt

	async def perform_player_check(self):
		if not len(self.players) <= database.get_db_count(self.prompts_table):
			self.prompts_table = "defaultprompts"
			await self.message.send("There are more users than prompts! Switching to default prompt list...")

	async def get_image_via_dm(self, player):
		fluff = "**" + ("#" * len(player.prompt)) + "**\n" #just fluff to go around the prompt
		bolded_prompt = "**{}**".format(player.prompt)
		prompt_with_fluff = fluff + bolded_prompt + "\n" + fluff #combine the fluff and prompt
		dm_message = await player.user.send("Your prompt is:\n{}Draw something now!".format(prompt_with_fluff))

		def is_author_dm_with_image(ctx):
			return ctx.channel == dm_message.channel and ctx.attachments

		submitted = False
		timer = 60
		timer_message = await player.user.send("{} seconds left!".format(timer))

		while timer > 0:
			await timer_message.edit(content="{} seconds left!".format(timer))
			try:
				msg = await self.bot.wait_for('message', check=is_author_dm_with_image, timeout=1)
				player.image = await msg.attachments[0].to_file()
				await player.user.send("Image submitted! Please return to main chat.")
				timer = -1 #is this really necesary?
			except asyncio.TimeoutError:
				timer -= 1
			except (discord.HTTPException, discord.Forbidden, discord.NotFound):
				await player.user.send("Could not download image! Place try again.")

	async def get_all_images(self):
		await self.message.channel.send("Prompts have been sent to all players. **Check your DM's now!**")
		events = []
		for player in self.players:
			events.append(self.get_image_via_dm(player))
			# await self.get_image_via_dm(player)
		results = await asyncio.gather(*events) #run through a list of functions to get them to get multiple messages

