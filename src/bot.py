from client import Client
from tables import ROLE_JOIN_MSGS
from permissions import *
from discord import PermissionOverwrite
from discord.errors import NotFound
from contextlib import suppress
import re
import os

TOKEN = os.getenv("DISCORD_TOKEN3")
COMMAND_PREFIX = ["/"]

client = Client(command_prefix=COMMAND_PREFIX)

MAX_NAME_LEN = 32

def command(name, roles=None, channels=None, categories=None, delete_parent=False):
	def decorator(func):
		async def f(ctx, *args, **kwargs):
			channel = ctx.channel
			if not await check_scope_perms(ctx.message, channels, categories):
				return
			if not await check_role_perms(ctx.message, roles):
				await channel.send("You do not have permissions to run this command")
				return

			try:
				await func(ctx, *args, **kwargs)
			except Exception as e:
				await channel.send(str(e))
				await ctx.message.add_reaction(u"\u274C")
			else:
				with suppress(NotFound):
					await ctx.message.add_reaction(u"\u2705")
					if delete_parent:
						await ctx.message.delete(delay=3)
		return client.command(name=name)(f)
	return decorator
					
@command(name='say')
async def say(ctx, *args):
	text = ctx.message.content.split(maxsplit=1)[1]
	await ctx.channel.send(text)

@command(name='deletemsg', roles=[ROLE_ADMIN])
async def deletemsg(ctx, count):
	async for msg in ctx.channel.history(limit=int(count) + 1):
		await msg.delete()

@command(name='addgame', roles=[ROLE_ADMIN], channels=[CHANNEL_GAME_ROLES], delete_parent=True)
async def addgame(ctx, *args):
	category = client.get_channel(CATEGORY_GAMES)
	await add_pair(ctx, category)

@command(name='addgenre', roles=[ROLE_ADMIN], channels=[CHANNEL_GENRE_ROLES], delete_parent=True)
async def addgame(ctx, *args):
	category = client.get_channel(CATEGORY_GENRES)
	await add_pair(ctx, category)

async def add_pair(ctx, category):
	name_raw = ctx.message.content.split(maxsplit=1)[1].strip(' -_')
	name = re.sub(r"[^\w\-_]", "", name_raw.replace(" ", "-")).lower()

	if len(name) > MAX_NAME_LEN:
		await ctx.channel.send(f"Name must no longer than {MAX_NAME_LEN} characters")
		return
	
	role = await ctx.guild.create_role(name=name, mentionable=True)

	chatmod_role = ctx.guild.get_role(ROLE_CHATMOD)

	overwrites = {
		ctx.guild.default_role: PermissionOverwrite(read_messages=False),
		role: PermissionOverwrite(read_messages=True),
		chatmod_role: PermissionOverwrite(read_messages=True),
	}
	channel = await category.create_text_channel(name, overwrites=overwrites)

	text = f" - {name_raw}"
	await create_rolejoin(ctx, role, text)

async def create_rolejoin(ctx, role, text):
	msg = await ctx.channel.send(text)
	ROLE_JOIN_MSGS[msg.id] = role.id
	await msg.add_reaction(u"\U0001F44D")


@command(name='rolejoin', roles=[ROLE_ADMIN], delete_parent=True)
async def rolejoin(ctx, *args):
	text = ctx.message.content.split(maxsplit=2)[2]
	roles = ctx.message.role_mentions
	
	if len(roles) != 1:
		ctx.channel.send("You must specify exactly one role")
		return

	role = roles[0]

	await create_rolejoin(ctx, role, text)







async def rolejoin_old(ctx, *args):
	await rich_send(ctx.channel, "React to any of the following messages to join the corresponding role")

	for role in ctx.message.role_mentions:
		msg = await rich_send(ctx.channel, f" - {role.mention}")
		ROLE_JOIN_MSGS[msg.id] = role.id
		await msg.add_reaction(u"\U0001F44D")

async def suggest(ctx, *args):
	length_limit = 30
	suggestion = ctx.message.content.split(maxsplit=1)[1]
	title = re.sub(r"[^\w\-]", "", re.sub(r" +", "-", suggestion)) # alphanumeric + "_" and "-"

	if len(title) > length_limit:
		await rich_send(ctx.channel, f"Project title must be no more than {length_limit} characters")
		return

	category = client.get_channel(CATEGORY_PROJECTS)
	project_channel = await category.create_text_channel(title)

	await rich_send(project_channel,
f"This channel is for discussion of the {project_channel.name} project. Here you can hash out requirements, scope, etc., \
before diving into the project itself and writing any code. \n\
Refer to the channels under `Help` and `Templates` for info on setting up your team \
using any of our provided templates. Of course, they are entirely optional, and exist solely \
to help you team get started.")
	
	msg = await rich_send(ctx.channel, f"React to this message to vote for \"{title}\". Checkout {project_channel.mention} for discussion")
	await msg.add_reaction(u"\U0001F44D")

client.run(TOKEN)
