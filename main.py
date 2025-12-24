import discord
import random
import os
import datetime
TOKEN = os.getenv("DISCORD_TOKEN")
if not TOKEN:
    raise RuntimeError("DISCORD_TOKEN is missing")
intents = discord.Intents.default()
intents.message_content = True
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
client = MyClient(intents=intents)

# store last time the random message was sent
last_random_send = None

@client.event
async def on_message(message):
    global last_random_send
    if message.author == client.user:
        return
    user_message = message.content.lower()

    #fuckass command requested by newspaper
    if user_message == 'victorian cuisine':
        await message.channel.send(
            "https://images-ext-1.discordapp.net/external/cgUQPEYpzmj7jm5D1R1lwVw_OHlHeaVU4XdY1W8E8T8/https/i.imgur.com/exNU6Rf.mp4"
        )

    #random roll (1 / 999 chance) to send some bullshit
    if random.randint(1, 100) == 2:
        now = datetime.datetime.utcnow()
        # check weekly cooldown
        if (
            last_random_send is None
            or now - last_random_send >= datetime.timedelta(days=7)
        ):
            await message.channel.send("BORN TO CAST - VICTORIA IS A FUCK 鬼神 Kill Em All 1091 I am rock cat 410,757,864,530 DEAD VICTORIANS")
            last_random_send = now
    #another command requested by newspaper
    if user_message == "hatto":
        await message.channel.send(
            "https://media.discordapp.net/attachments/1432125742396735532/1453363990511091762/hatto.jpg"
        )
client.run(TOKEN)




