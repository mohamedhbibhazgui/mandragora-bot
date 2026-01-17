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
# /bless command
# ─────────────────────────────
@client.tree.command(name="bless", description="Send a blessing GIF via DM")
@app_commands.describe(user="User to bless")
async def bless(interaction: discord.Interaction, user: discord.User):
    placeholder_gif = (
        "https://tenor.com/view/"
        "mandragora-mandragora-arknights-gif-12377204109633212970"
    )

    blesser = interaction.user

    if user.id in client.dm_blocked_users:
        await interaction.response.send_message(
            "This user has disabled blessing DMs.",
            ephemeral=True
        )
        return

    try:
        await user.send(
            f"You have been blessed by {blesser.display_name}\n{placeholder_gif}"
        )

        await interaction.response.send_message(
            f"Blessing sent to {user.mention}",
            ephemeral=True
        )

    except discord.Forbidden:
        await interaction.response.send_message(
            "I can't DM this user (DMs disabled by Discord).",
            ephemeral=True
        )

    except Exception:
        await interaction.response.send_message(
            "Failed to send blessing.",
            ephemeral=True
        )

# ─────────────────────────────
# /blockbless command
# ─────────────────────────────
@client.tree.command(
    name="blockbless",
    description="Prevent the bot from DMing you blessings"
)
async def blockbless(interaction: discord.Interaction):
    client.dm_blocked_users.add(interaction.user.id)
    save_blocked_users(client.dm_blocked_users)

    await interaction.response.send_message(
        "The bot will no longer DM you blessings.",
        ephemeral=True
    )

# ─────────────────────────────
# /allowbless command
# ─────────────────────────────
@client.tree.command(
    name="allowbless",
    description="Allow the bot to DM you blessings again"
)
async def allowbless(interaction: discord.Interaction):
    client.dm_blocked_users.discard(interaction.user.id)
    save_blocked_users(client.dm_blocked_users)

    await interaction.response.send_message(
        "The bot can DM you blessings again.",
        ephemeral=True
    )

# ─────────────────────────────
# Message listener
# ─────────────────────────────
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    TARGET_USER_ID = 644586863881093120
    TARGET_USER_MENTION = f"<@{TARGET_USER_ID}>"

    # ─────────────────────────────
    # 1/75 chance (specific user)
    # ─────────────────────────────
    if message.author.id == TARGET_USER_ID:
        if random.randint(1, 75) == 1:
            await message.channel.send(
                "Go white boy Go"
            )

    # ─────────────────────────────
    # 1/300 chance (any user, tags target user)
    # ─────────────────────────────
    if random.randint(1, 300) == 1:
        await message.channel.send(
            f"{TARGET_USER_MENTION}\n"
            "https://media.discordapp.net/attachments/"
            "1346809772070141952/1354376217410670698/"
            "SPOILER_picmix.com_12527279.gif"
        )

    # ─────────────────────────────
    # Keyword triggers
    # ─────────────────────────────
    user_message = message.content.lower()

    if "victorian cuisine" in user_message:
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/"
            "cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/"
            "https/i.imgur.com/exNU6Rf.mp4"
        )

    if "hatto" in user_message.split():
        await message.channel.send(
            "https://media.discordapp.net/attachments/"
            "1432125742396735532/1453363990511091762/hatto.jpg"
        )

client.run(TOKEN)


