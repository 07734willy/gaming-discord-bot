
ROLE_ADMIN = 742906455509696554
ROLE_CHATMOD = 743665413275254837

CHANNEL_GAME_ROLES = 742905506112208897
CHANNEL_GENRE_ROLES = 742905532385460236
CHANNEL_MISC_ROLES = 743618517701492755

CATEGORY_GAMES = 742905018901856347
CATEGORY_GENRES = 742905058676441161


async def check_scope_perms(msg, channels, categories):
	category_id = getattr(getattr(msg, 'category', None), 'id', None)

	return not ((channels or categories) and
		(not channels or msg.channel.id not in channels) and
		(not categories or category_id not in categories))

async def check_role_perms(msg, roles):
	if not roles:
		return True

	for role in msg.author.roles:
		if role.id in roles:
			return True
	return False
