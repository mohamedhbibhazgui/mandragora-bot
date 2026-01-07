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
@client.tree.command(name="bless", description="Send a blessing GIF")
async def bless(interaction: discord.Interaction):
    placeholder_gif = "https://media.tenor.com/placeholder.gif"

    await interaction.response.send_message(
        f"https://tenor.com/view/montgomery-swizzenbocher-iii-gif-15095346273009658011"
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
