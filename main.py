import discord
import random
import os
import datetime
from discord import app_commands

TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")

intents = discord.Intents.default()
intents.message_content = True

class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged in as {self.user}")

client = MyClient()

@client.tree.command(name="dm", description="Send a DM to a user")
@app_commands.describe(
    user="User to DM",
    message="Message to send"
)
async def dm(
    interaction: discord.Interaction,
    user: discord.User,
    message: str
):
    try:
        await user.send(message)
        await interaction.response.send_message(
            f"✅ DM sent to {user.mention}",
            ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "I can't DM this user (DMs disabled).",
            ephemeral=True
        )
    except Exception:
        await interaction.response.send_message(
            "Failed to send DM.",
            ephemeral=True
        )

last_random_send = None

@client.event
async def on_message(message):
    global last_random_send

    if message.author == client.user:
        return

    user_message = message.content.lower()

    if "victorian cuisine" in user_message:
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/https/i.imgur.com/exNU6Rf.mp4"
        )

    if random.randint(1, 100) == 2:
        now = datetime.datetime.utcnow()
        if (
            last_random_send is None
            or now - last_random_send >= datetime.timedelta(days=7)
        ):
            await message.channel.send(
                "BORN TO CAST - VICTORIA IS A FUCK 鬼神 Kill Em All 1091 I am rock cat 410,757,864,530 DEAD VICTORIANS"
            )
            last_random_send = now

    if "hatto" in message.content.lower().split():
        await message.channel.send(
            "https://media.discordapp.net/attachments/1432125742396735532/1453363990511091762/hatto.jpg"
        )



client.run(TOKEN)





