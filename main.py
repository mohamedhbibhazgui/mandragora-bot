import discord
import random
import os
import datetime
import json
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

DATA_FILE = "dm_blocked.json"

intents = discord.Intents.default()
intents.message_content = True

# ─────────────────────────────
# Role ↔ Channel mapping
# ─────────────────────────────
ROLE_CHANNELS = {
    "teal": {
        "channel_id": 1346808567130230804,
        "role_id": 1315105809658544209,
    },
    "yellow_orange": {
        "channel_id": 1395007020163268669,
        "role_id": 1395006533347180624,
    },
    "green": {
        "channel_id": 1346809772070141952,
        "role_id": 1315090029982384169,
    },
    "grey": {
        "channel_id": 1346806389359775846,
        "role_id": 1345758044499476501,
    },
    "blue": {
        "channel_id": 1346807075153645681,
        "role_id": 1385296517975375993,
    },
    "purple": {
        "channel_id": 1346806767228555345,
        "role_id": 1315091467127230534,
    },
    "red": {
        "channel_id": 1346806929065771072,
        "role_id": 1315102680775135324,
    },
    "guides": {
        "channel_id": 1368902634437738617,
        "role_id": 1238573370220740729,
    },
}

INSULTS = [
    "stinky",
    "cringe",
    "lame",
    "embarrassing",
    "unwashed",
    "terminally online",
]

# ─────────────────────────────
# Persistence helpers
# ─────────────────────────────
def load_blocked_users():
    if not os.path.exists(DATA_FILE):
        return set()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except Exception:
        return set()

def save_blocked_users(blocked_users):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(list(blocked_users), f)

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.dm_blocked_users = load_blocked_users()

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Loaded {len(self.dm_blocked_users)} blocked users")

client = MyClient()

# ─────────────────────────────
# /bless
# ─────────────────────────────
@client.tree.command(name="bless", description="Send a blessing GIF via DM")
@app_commands.describe(user="User to bless")
async def bless(interaction: discord.Interaction, user: discord.User):
    gif = (
        "https://tenor.com/view/"
        "mandragora-mandragora-arknights-gif-12377204109633212970"
    )

    if user.id in client.dm_blocked_users:
        await interaction.response.send_message(
            "This user has disabled blessing DMs.",
            ephemeral=True
        )
        return

    try:
        await user.send(
            f"You have been blessed by {interaction.user.display_name}\n{gif}"
        )
        await interaction.response.send_message(
            f"Blessing sent to {user.mention}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "I can't DM this user.",
            ephemeral=True
        )

# ─────────────────────────────
# /blockbless
# ─────────────────────────────
@client.tree.command(name="blockbless", description="Prevent blessing DMs")
async def blockbless(interaction: discord.Interaction):
    client.dm_blocked_users.add(interaction.user.id)
    save_blocked_users(client.dm_blocked_users)
    await interaction.response.send_message(
        "Blessing DMs disabled.",
        ephemeral=True
    )

# ─────────────────────────────
# /allowbless
# ─────────────────────────────
@client.tree.command(name="allowbless", description="Allow blessing DMs")
async def allowbless(interaction: discord.Interaction):
    client.dm_blocked_users.discard(interaction.user.id)
    save_blocked_users(client.dm_blocked_users)
    await interaction.response.send_message(
        "Blessing DMs enabled.",
        ephemeral=True
    )

# ─────────────────────────────
# /insult (ROLE-CHAOS COMMAND)
# ─────────────────────────────
@client.tree.command(
    name="insult",
    description="Spread chaos between two colors"
)
@app_commands.describe(
    source="Who said it",
    target="Who is being insulted"
)
async def insult(
    interaction: discord.Interaction,
    source: discord.Role,
    target: discord.Role
):
    # Must be used in a mapped channel
    channel_data = next(
        (v for v in ROLE_CHANNELS.values()
         if v["channel_id"] == interaction.channel_id),
        None
    )

    if channel_data is None:
        await interaction.response.send_message(
            "You can't use this command in this channel.",
            ephemeral=True
        )
        return

    # User must have the role for this channel
    if not any(
        role.id == channel_data["role_id"]
        for role in interaction.user.roles
    ):
        await interaction.response.send_message(
            "You don't belong to this color.",
            ephemeral=True
        )
        return

    if source.id == target.id:
        await interaction.response.send_message(
            "Source and target must be different roles.",
            ephemeral=True
        )
        return

    insult_word = random.choice(INSULTS)

    await interaction.response.send_message(
        f"Hey **{target.name}**, **{source.name}** called you **{insult_word}**"
    )

# ─────────────────────────────
# Message listener (unchanged)
# ─────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    TARGET_USER_ID = 644586863881093120
    TARGET_USER_MENTION = f"<@{TARGET_USER_ID}>"

    if message.author.id == TARGET_USER_ID:
        if random.randint(1, 75) == 1:
            await message.channel.send("Go white boy Go")

    if random.randint(1, 300) == 1:
        await message.channel.send(
            f"{TARGET_USER_MENTION}\n"
            "https://media.discordapp.net/attachments/"
            "1346809772070141952/1354376217410670698/"
            "SPOILER_picmix.com_12527279.gif"
        )

    msg = message.content.lower()

    if "victorian cuisine" in msg:
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/"
            "cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/"
            "https/i.imgur.com/exNU6Rf.mp4"
        )

    if "hatto" in msg.split():
        await message.channel.send(
            "https://media.discordapp.net/attachments/"
            "1432125742396735532/1453363990511091762/hatto.jpg"
        )

client.run(TOKEN)
