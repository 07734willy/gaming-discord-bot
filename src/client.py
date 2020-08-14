from discord.ext.commands import Bot
from tables import ROLE_JOIN_MSGS

class Client(Bot):
	async def on_ready(self):
		print(f"{self.user.name} now connected")

	async def on_message(self, message):
		if message.author == self.user:
			return

		await super().on_message(message)

	async def on_raw_reaction_add(self, payload):
		await self.on_raw_reaction_toggle(payload, active=True)

	async def on_raw_reaction_remove(self, payload):
		await self.on_raw_reaction_toggle(payload, active=False)

	async def on_raw_reaction_toggle(self, payload, active):
		channel = self.get_channel(payload.channel_id)
		msg = await channel.fetch_message(payload.message_id)
		
		if msg.id in ROLE_JOIN_MSGS:
			guild = self.get_guild(payload.guild_id)
			member = guild.get_member(payload.user_id)

			if member == self.user:
				return
			
			role_id = ROLE_JOIN_MSGS[msg.id]
			role = guild.get_role(role_id)

			if active:
				await member.add_roles(role, reason=f"Role self-join from {channel.name}")
			else:
				await member.remove_roles(role, reason=f"Role self-leave from {channel.name}")
