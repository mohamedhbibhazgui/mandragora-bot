import discord
import random
import os
import json
import re
import datetime
from discord import app_commands
from discord.ext import tasks
from PIL import Image, ImageDraw
import aiohttp
import io

#test
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")
PURGE_CHANNEL_ID = 1346807075153645681  # <-- channel to wipe weekly
DATA_FILE = "dm_blocked.json"
STONE_FILE = "stone_leaderboard.json"
HUG_BACKGROUND_URL = (
    "https://media.discordapp.net/attachments/1462490936490856582/"
    "1462490937073729780/Mandra_Hug2.jpeg"
)

intents = discord.Intents.default()
intents.message_content = True
INSULTS = [
    "stinky",
    "cringe",
    "lame",
    "embarrassing",
    "unwashed",
    "terminally online",]
GOON_MESSAGES = [
    "good idea baws",
    "aye boss",
    "sounds right, baws",
    "whatever you say, baws",
    "you got it, boss",
    "yeah yeah, makes sense baws",]

last_random_send = None
ALLOWED_ROLE_IDS = {
    1315105809658544209,
    1395006533347180624,
    1315090029982384169,
    1345758044499476501,
    1385296517975375993,
    1315091467127230534,
    1315102680775135324,
    1238573370220740729,
    1346800838491897891,
    1315094176072732723,
}
ROLE_CHANNEL_MAP = {
    # channel_id : role_id
    1346808567130230804: 1315105809658544209,  # teal
    1395007020163268669: 1395006533347180624,  # yellow/orange
    1346809772070141952: 1315090029982384169,  # green
    1346806389359775846: 1345758044499476501,  # grey
    1346807075153645681: 1385296517975375993,  # blue
    1346806767228555345: 1315091467127230534,  # purple
    1346806929065771072: 1315102680775135324,  # red
    1368902634437738617: 1238573370220740729,  # guides
    1346806389359775846: 1346800838491897891,  #black
    1346807075153645681: 1315094176072732723, #Blue
    
    
}

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
# /stone
@client.tree.command(name="stone", description="Attempt to stone another user")
@app_commands.describe(user="User to stone")
async def stone(interaction: discord.Interaction, user: discord.User):
    brick_gif = "https://tenor.com/view/cat-throwing-brick-brick-cat-gif-9142560192559212520"
    parry_gif = "https://tenor.com/view/ultrakill-funny-cat-cat-parry-explode-gif-12515622299668151985"

    stoner_id = str(interaction.user.id)
    target_id = str(user.id)

    if random.choice([True, False]):
        client.stone_data[target_id] = client.stone_data.get(target_id, 0) + 1
        save_stone_data(client.stone_data)

        await interaction.response.send_message(
            f"{interaction.user.name} stones {user.name}\n{brick_gif}",
            allowed_mentions=discord.AllowedMentions.none()
        )
    else:
        client.stone_data[stoner_id] = client.stone_data.get(stoner_id, 0) + 1
        save_stone_data(client.stone_data)

        await interaction.response.send_message(
            f"{interaction.user.mention} you got parried!\n{parry_gif}"
        )
@client.tree.command(name="hug", description="Hug another user")
@app_commands.describe(user="User to hug")
async def hug(interaction: discord.Interaction, user: discord.User):
    await interaction.response.defer()

    background_path = os.path.join(os.path.dirname(__file__), "Mandra_Hug2.jpeg")

    if not os.path.exists(background_path):
        await interaction.followup.send("Hug image missing on server.")
        return

    avatar_url = user.display_avatar.replace(size=256, format="png").url

    headers = {
        "User-Agent": "DiscordBot (Mandrabot)"
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(avatar_url) as av_resp:
            if av_resp.status != 200:
                await interaction.followup.send("Failed to load avatar.")
                return
            avatar_bytes = await av_resp.read()

    # Open images
    background = Image.open(background_path).convert("RGBA")
    avatar = Image.open(io.BytesIO(avatar_bytes)).convert("RGBA")

    # Sizes (locked in)
    avatar_size = 210
    outline_size = 6

    avatar = avatar.resize((avatar_size, avatar_size))

    # ---- CREATE BLACK OUTLINE ----
    total_size = avatar_size + outline_size * 2

    outline = Image.new("RGBA", (total_size, total_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(outline)
    draw.ellipse(
        (0, 0, total_size, total_size),
        fill=(0, 0, 0, 255)
    )

    # Circular avatar mask
    mask = Image.new("L", (avatar_size, avatar_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, avatar_size, avatar_size), fill=255)
    avatar.putalpha(mask)

    # Paste avatar onto outline
    outline.paste(avatar, (outline_size, outline_size), avatar)

    # ---- POSITION (TINY LOWER + LEFT) ----
    bg_w, bg_h = background.size
    position = (
        (bg_w - total_size) // 2 - 15,   # ← left
        (bg_h - total_size) // 2 + 145,  # ↓ lower
    )

    background.paste(outline, position, outline)

    # Send result
    buffer = io.BytesIO()
    background.save(buffer, format="PNG")
    buffer.seek(0)

    await interaction.followup.send(
        file=discord.File(buffer, filename="hug.png")
    )




# /stoneboard
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
        try:
            user = await client.fetch_user(int(user_id))
            name = user.name if user.discriminator != "0" else user.name
        except Exception:
            name = f"Unknown User ({user_id})"

        lines.append(f"**{i}.** {name} — **{points}**")

    await interaction.response.send_message(
        "🪨 **STONING LEADERBOARD** 🪨\n" + "\n".join(lines)
    )
# role_id -> channel_id
ROLE_TO_CHANNEL = {role: channel for channel, role in ROLE_CHANNEL_MAP.items()}


@client.tree.command(name="insult", description="Insult another role in their channel")
@app_commands.describe(role="Role to insult")
async def insult(interaction: discord.Interaction, role: discord.Role):
    member = interaction.user

    # Determine role1 (caller role)
    caller_role = None
    for r in member.roles:
        if r.id in ROLE_TO_CHANNEL:
            caller_role = r
            break

    if caller_role is None:
        await interaction.response.send_message(
            "You don't have permission to insult anyone.",
            ephemeral=True
        )
        return

    # Validate target role
    if role.id not in ROLE_TO_CHANNEL:
        await interaction.response.send_message(
            "That role cannot be insulted.",
            ephemeral=True
        )
        return

    if role.id == caller_role.id:
        await interaction.response.send_message(
            "You can't insult your own role.",
            ephemeral=True
        )
        return

    target_channel_id = ROLE_TO_CHANNEL[role.id]
    target_channel = interaction.guild.get_channel(target_channel_id)

    if target_channel is None:
        await interaction.response.send_message(
            "Target channel not found.",
            ephemeral=True
        )
        return

    insult = random.choice(INSULTS)

    await target_channel.send(
        f"{role.name}, {caller_role.name} called you **{insult}**."
    )

    await interaction.response.send_message(
        f"Insult delivered to {target_channel.mention}.",
        ephemeral=True
    )
@client.tree.command(name="mandrapet", description="mandra pet")
async def mandrapet(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://media.discordapp.net/attachments/1462490936490856582/1462491111921549573/MANDY_SMILE_TRANS.gif"
    )
@client.tree.command(name="pillar", description="pillar")
async def pillar(interaction: discord.Interaction):
    await interaction.response.send_message(
        "https://media.discordapp.net/attachments/586588921614303233/1446964632970596372/10N04_Mandragora.gif"
    )

# Message listener
@client.event
async def on_message(message):
    global last_random_send

    if message.author == client.user:
        return

    if message.author.id == 644586863881093120:
        if random.randint(1, 100) == 1:
            await message.channel.send("go white boy go")

    if contains_goon(message.content):
        await message.channel.send(random.choice(GOON_MESSAGES))

    user_message = message.content.lower()

    if user_message == 'victorian cuisine':
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/https/i.imgur.com/exNU6Rf.mp4"
        )

    if random.randint(1, 999) == 2:
        now = datetime.datetime.utcnow()
        if (
            last_random_send is None
            or now - last_random_send >= datetime.timedelta(days=7)
        ):
            await message.channel.send(
                "BORN TO CAST VICTORIA IS A FUCK 鬼神 Kill Em All 1091 "
                "I am rock cat410,757,864,530 DEAD VICTORIANS"
            )
            last_random_send = now

    if random.randint(1, 1000) == 1:
        await message.channel.send(
            "<@644586863881093120>\n"
            "https://media.discordapp.net/attachments/1346809772070141952/1354376217410670698/"
            "SPOILER_picmix.com_12527279.gif?ex=696defa5&is=696c9e25&hm="
            "3ab21403e0ea38f6f5bd1227a646a312b8da8968a7e929f3f0aa8dad20705668&=&width=620&height=620"
        )

    if user_message == "hatto":
        await message.channel.send(
            "https://media.discordapp.net/attachments/1432125742396735532/1453363990511091762/hatto.jpg"
        )
@tasks.loop(hours=168)  # 7 days
async def weekly_purge():
    channel = client.get_channel(PURGE_CHANNEL_ID)

    if channel is None:
        print("failed at censoring the bl*es")
        return

    deleted = 0

    async for message in channel.history(limit=None, oldest_first=True):
        try:
            await message.delete()
            deleted += 1
        except discord.Forbidden:
            print("the bl*es won.")
            return
        except discord.HTTPException:
            pass  # rate limits / already deleted

    print(f"blues: deleted {deleted} messages")
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # --- NEW: Respond to mentions ---
    if client.user.mentioned_in(message):
        # Choose a random response from your GOON_MESSAGES or a new list
        responses = [
            "You rang, baws?",
            "I'm here, what's up baws ?",
            "Direct orders only, baws.",
            "Always here baws"
        ]
        await message.channel.send(random.choice(responses))
client.run(TOKEN)
