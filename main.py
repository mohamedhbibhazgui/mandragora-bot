import discord
import random
import os
import json
import re
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

DATA_FILE = "dm_blocked.json"
STONE_FILE = "stone_leaderboard.json"

intents = discord.Intents.default()
intents.message_content = True

# ─────────────────────────────
# Insults
# ─────────────────────────────
INSULTS = [
    "stinky",
    "cringe",
    "lame",
    "embarrassing",
    "unwashed",
    "terminally online",
]

# ─────────────────────────────
# Mob goon messages
# ─────────────────────────────
GOON_MESSAGES = [
    "good idea baws",
    "aye boss",
    "sounds right, baws",
    "whatever you say, baws",
    "you got it, boss",
    "yeah yeah, makes sense baws",
]
last_random_send = None
# ─────────────────────────────
# Allowed color roles
# ─────────────────────────────
ALLOWED_ROLE_IDS = {
    1315105809658544209,
    1395006533347180624,
    1315090029982384169,
    1345758044499476501,
    1385296517975375993,
    1315091467127230534,
    1315102680775135324,
    1238573370220740729,
}

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

def load_stone_data():
    if not os.path.exists(STONE_FILE):
        return {}
    try:
        with open(STONE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_stone_data(data):
    with open(STONE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# ─────────────────────────────
# Goon detection
# ─────────────────────────────
def contains_goon(text: str) -> bool:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)

    if "goon" in text:
        return True

    words = text.split()
    for i in range(len(words) - 1):
        if words[i] == "go" and words[i + 1] == "on":
            return True

    return False

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.dm_blocked_users = load_blocked_users()
        self.stone_data = load_stone_data()

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        print(f"Loaded {len(self.dm_blocked_users)} blocked users")

client = MyClient()

# ─────────────────────────────
# /stone
# ─────────────────────────────
@client.tree.command(name="stone", description="Attempt to stone another user")
@app_commands.describe(user="User to stone")
async def stone(interaction: discord.Interaction, user: discord.User):
    brick_gif = "https://tenor.com/view/cat-throwing-brick-brick-cat-gif-9142560192559212520"
    parry_gif = "https://tenor.com/view/ultrakill-funny-cat-cat-parry-explode-gif-12515622299668151985"

    stoner_id = str(interaction.user.id)
    target_id = str(user.id)

    if random.choice([True, False]):
        # Brick hits
        client.stone_data[target_id] = client.stone_data.get(target_id, 0) + 1
        save_stone_data(client.stone_data)

        await interaction.response.send_message(
            f"{interaction.user.mention} stones {user.mention} 🧱\n{brick_gif}"
        )
    else:
        # Parried
        client.stone_data[stoner_id] = client.stone_data.get(stoner_id, 0) + 1
        save_stone_data(client.stone_data)

        await interaction.response.send_message(
            f"{interaction.user.mention} you got parried! 🛡️\n{parry_gif}"
        )

# ─────────────────────────────
# /stoneboard
# ─────────────────────────────
@client.tree.command(name="stoneboard", description="View the stoning leaderboard")
async def stoneboard(interaction: discord.Interaction):
    if not client.stone_data:
        await interaction.response.send_message(
            "No one has been stoned yet.",
            ephemeral=True
        )
        return

    sorted_board = sorted(
        client.stone_data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    lines = []
    for i, (user_id, points) in enumerate(sorted_board[:10], start=1):
        lines.append(f"**{i}.** <@{user_id}> — **{points}**")

    await interaction.response.send_message(
        "🪨 **STONING LEADERBOARD** 🪨\n" + "\n".join(lines)
    )

# ─────────────────────────────
# Message listener
# ─────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if contains_goon(message.content):
        await message.channel.send(random.choice(GOON_MESSAGES))
    user_message = message.content.lower()

    #fuckass command requested by newspaper
    if user_message == 'victorian cuisine':
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/https/i.imgur.com/exNU6Rf.mp4"
        )

    #random roll (1 / 999 chance) to send some bullshit
    if random.randint(1, 999) == 2:
        now = datetime.datetime.utcnow()
        # check weekly cooldown
        if (
            last_random_send is None
            or now - last_random_send >= datetime.timedelta(days=7)
        ):
            await message.channel.send("BORN TO CAST VICTORIA IS A FUCK 鬼神 Kill Em All 1091 I am rock cat410,757,864,530 DEAD VICTORIANS")
            last_random_send = now
    #another command requested by newspaper
    if user_message == "hatto":
        await message.channel.send(
            "https://media.discordapp.net/attachments/1432125742396735532/1453363990511091762/hatto.jpg"
        )
client.run(TOKEN)
