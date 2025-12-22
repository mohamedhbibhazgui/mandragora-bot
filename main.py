import discord
import random
intents = discord.Intents.default()
intents.message_content = True
class MyClient(discord.Client):
    async def on_ready(self):
        print(f"Logged in as {self.user}")
client = MyClient(intents=intents)
@client.event
async def on_message(message):
    username = str(message.author).split('#')[0]
    user_message = str(message.content)
    if message.author == client.user:
         return
    if user_message.lower()=='testing':
        await message.channel.send("The flesh I have been granted pains me.")
    if (random.randint(1,999)==2):
        await message.channel.send("https://media.discordapp.net/attachments/1346809772070141952/1354376217410670698/SPOILER_picmix.com_12527279.gif?ex=6949ae65&is=69485ce5&hm=bb3a94baa8c36ddb9db012cb721b06321c136909fd6609e95c2e9ca1be168d5c&=&width=620&height=620")


client.run("DISCORD_TOKEN")
