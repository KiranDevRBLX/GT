import os
import nextcord
import datetime
import random
import string
import praw
import aiohttp
import requests
import sys
from nextcord import File
from nextcord import Interaction, SlashOption
from nextcord.ext import commands
from server import awake



import pymongo
from pymongo import MongoClient
from urllib.parse import quote_plus
from PIL import Image, ImageDraw, ImageFont
from easy_pil import Editor, load_image_async, Font

reddit = praw.Reddit(client_id = "ugVy84D92RneS2lNI4Vs-Q", client_secret = "5w8VCNzk8CleOu4e62aYfzjgSVKltA", user_agent = "Bro's Bot")

pymongoPass = quote_plus("San143Unk") #os.environ['PymongoPassword']
cluster = MongoClient(f"mongodb+srv://ModeratorTrackway:{pymongoPass}@cluster0.e0rnpzu.mongodb.net/?retryWrites=true&w=majority")
db = cluster["test"]
collection = db["verifies"]

verfprocessChannelId = 1175478491748245605
verifyChannelId = 1123583891916197899
joinandleftChannelId = 1109746973927542854
feedback_channel_id = 1155396865613901837

token = "MTE2NTg4ODcxMzQ3ODM5Mzk1Ng.GCbgQ6.FjunRl00UqXCVjvfFtF69OnqVPCohwC9UTw4JY" #os.environ['BotToken']

activity = nextcord.Activity(type=nextcord.ActivityType.watching, name="Bro's GFX")

intents = nextcord.Intents.default()
intents = nextcord.Intents().all()
bot = commands.Bot(intents=intents, activity=activity)

polls = {}

commandsstated = (
    "**help** \nDisplays help commands.",
    "**ping** \nResponds to you with a pong!",
    "**purge** \nClears specified amount of previous messages.",
    "**announce** \nAnnounce a message with an optional title!",
    "**meme** \nOutputs a random meme from r/memes",
    "**userinfo** \nOutputs information about the mentioned member!"
)

hiddencommands = (
    "**THE FOLLOWING COMMANDS ARE ALL HIDDEN FROM THE DEFAULT HELP**",
    "**verify** \nGives full access to the server when including the correct code sent by the bot, if you haven't gotten a code, try 0000",
    "**verify_steps** \nOutputs the steps needed to verify a user!",
    "**syncdb** \nWhen inputting a member adds them to the database incase something went wrong."
)

logging = True

@bot.event
async def on_ready():
    print(f"{bot.user} is ready!")

@bot.slash_command(name="ping",description="Responds to you with a pong!")
async def hello(interaction: Interaction):
    await interaction.response.send_message(f"Pong!")

@bot.slash_command(name="help", description="Displays help for the Bro's Bot!")
async def help(interaction: Interaction, includehidden=False):
    embed = nextcord.Embed(title="Bro's Bot Help", description="Displays commands for the Bro's Bot!")
    for command in commandsstated:
        embed.add_field(name="", value=command)
    if includehidden != False:
        for hidden in hiddencommands:
            embed.add_field(name="", value=hidden)

    await interaction.response.send_message(embed=embed)


    #for mention in message.mentions:
    #    if mention.id == bot.user.id:
    #        await message.reply("For more info about me use /help")

@bot.slash_command(name="purge", description="Purges channel messages with the amount given.")
async def purge(interaction: nextcord.Interaction, messages: int):
    await interaction.response.defer()
    z = await interaction.channel.purge(limit=messages+1)

@bot.slash_command(name="announce", description="Announce an important message!")
async def announce(interaction: nextcord.Interaction, message: str, title='', image=''):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to use this command!", ephemeral=True)
    else:
        embed = nextcord.Embed(title="", description="✅ Annoucement sent.")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        embed = nextcord.Embed(title=title, description=message, color=nextcord.Color.from_rgb(58,87,233))
        embed.timestamp = nextcord.utils.utcnow()

        embed.set_footer(text="Bro's Bot | Bro's GFX")

        if image != '':
            embed.set_image(image)

        await interaction.channel.send(embed=embed)

@bot.slash_command(name="meme", description="Gets a random meme from r/memes")
async def meme(interaction: nextcord.Interaction):
    subreddit = reddit.subreddit("memes")
    all_subs = []

    top = subreddit.top(limit = 75)

    for submission in top:
        all_subs.append(submission)

    random_sub = random.choice(all_subs)
    name = random_sub.title
    url = random_sub.url

    embed = nextcord.Embed(title = name, description = f'URL: {url}')
    embed.set_image(url = url)
    await interaction.response.send_message(embed=embed)

@bot.slash_command(name="userinfo", description="Outputs info about mentioned user.")
async def userinfo(interaction: nextcord.Interaction, member: nextcord.Member):
    embed = nextcord.Embed(color=member.color, timestamp=nextcord.utils.utcnow())
    embed.set_author(name=f"User Info - {member}")
    embed.set_thumbnail(url=member.avatar)
    embed.set_footer(text=f"Requested by - {interaction.user}")

    embed.add_field(name="Name: ", value=member.display_name, inline=False)
    embed.add_field(name="Nickname: ", value=member.nick, inline=False)
    embed.add_field(name="ID: ", value=member.id, inline=False)
    embed.add_field(name="Is bot: ", value=member.bot, inline=False)
    embed.add_field(name="Created at: ", value=member.created_at, inline=False)
    embed.add_field(name="Joined at: ", value=member.joined_at, inline=False)

    roles = []
    for role in member.roles:
        if role.name != "everyone":
            roles.append(role.mention)

    b = ", ".join(roles)

    embed.add_field(name=f"Roles({len(roles)}): ", value=''.join([b]), inline=False)
    embed.add_field(name="Top Role: ", value=member.top_role.mention)

    myquery = {"_id": f"{member.id}"}
    mydoc = collection.find(myquery)
    lastBoosted = "Never"
    for x in mydoc:
        print(x["Boosting Since"])
        if x["Boosting Since"] != None:
            if lastBoosted != x["Boosting Since"]:
                lastBoosted = x["Boosting Since"]

    embed.add_field(name="Last Boosted: ", value=lastBoosted)

    await interaction.response.send_message(embed=embed)

@bot.slash_command(name="syncdb", description="Sync database incase someone isnt on there.")
async def syncdb(interaction: nextcord.Interaction, member: nextcord.Member):
    myquery = {"_id": f"{interaction.user.id}"}
    if myquery != None:
        mydict = { "_id": f"{member.id}", "Code": "0000", "Status": f"Verified", "Boosting Since": "Never"}
        x = collection.insert_one(mydict)
        await interaction.response.send_message("User synced successfully!", ephemeral=True)
    else:
        await interaction.response.send_message("User already is synced.", ephemeral=True)

# Cat and Dog

@bot.slash_command(name="cat", description="Gets a random cat image.")
async def cat(ctx: nextcord.Interaction):
    async with aiohttp.ClientSession() as session:
       async with session.get('https://api.thecatapi.com/v1/images/search') as response:
        cat_data = await response.json()
        cat_url = cat_data[0]['url']

        embed = nextcord.Embed(title="Cat", description="Here's a random cat image.", color=nextcord.Color.random())
       embed.set_image(url=cat_url)

       await ctx.send(embed=embed)

@bot.slash_command(name="dog", description="Gets a random dog image.")
async def dog(ctx: nextcord.Interaction):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://dog.ceo/api/breeds/image/random') as response:
            dog_data = await response.json()
            dog_url = dog_data['message']

            embed = nextcord.Embed(title="Dog", description="Here's a random dog image.", color=nextcord.Color.random())
            embed.set_image(url=dog_url)

            await ctx.send(embed=embed)
          
@bot.event
async def on_slash_command_error(interaction: nextcord.Interaction, error):
    if isinstance(error, nextcord.ext.commands.CommandOnCooldown):
        await interaction.response.send_message(error, ephemeral=True)
    else:
        raise error


#Random GIF : Working 

def get_random_gif_url(api_key):
  base_url = "https://api.giphy.com/v1/gifs/random"
  params = {
      "api_key": api_key,
      "tag": "funny",
  }

  response = requests.get(base_url, params=params)

  if response.status_code == 200:
      data = response.json()
      if "data" in data and "images" in data["data"]:
          gif_url = data["data"]["images"]["original"]["url"]
          return gif_url
  return None

@bot.slash_command(name="randomgif", description="Generate a random funny gif")
async def random_gif(ctx):
  api_key = "DQSOa0Y0wbsIAzBli5bxDLoVQFMTrDYx"  # Replace with your Giphy API key
  gif_url = get_random_gif_url(api_key)

  if gif_url:
      await ctx.send(gif_url)
  else:
      await ctx.send("Error fetching the GIF. Please try again.")


  #8 ball : Working


@bot.slash_command(name="8ball", description="Ask the magic 8-ball a question")
async def eight_ball(ctx, question: str):
    # Check for specific keywords in the question to tailor responses
    positive_keywords = ["good", "yes", "certain", "likely", "definitely", "sure"]
    negative_keywords = ["no", "not", "doubt", "unlikely", "never"]

    # Generate a response based on the presence of keywords
    if any(keyword in question.lower() for keyword in positive_keywords):
        response = random.choice([
            "Absolutely!",
            "Certainly!",
            "Without a doubt!",
            "Yes, definitely!",
            "You can count on it!"
        ])
    elif any(keyword in question.lower() for keyword in negative_keywords):
        response = random.choice([
            "Nope.",
            "Don't count on it.",
            "Very doubtful.",
            "I wouldn't bet on it.",
            "Not likely."
        ])
    else:
        response = random.choice([
            "I'm not sure, ask again later.",
            "I'm afraid I don't have a clear answer for that.",
            "The future is uncertain.",
            "It's hard to say.",
            "I'll leave that for you to figure out."
        ])

    await ctx.send(f"**Question:** {question}\n**Answer:** {response}")


#Random Quote : Working

@bot.slash_command(name="randomquote", description="Get a random quote")
async def random_quote(ctx: commands.Context):
    try:
        quote = get_random_quote()

        if quote:
            embed = nextcord.Embed(
                title="Random Quote",
                description=f'"{quote["quote"]}" - {quote["author"]}',
                color=0x3498db,
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("Error fetching the quote. Please try again.")
    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send(f"An error occurred while processing the request: {e}")

def get_random_quote():
    url = "http://api.quotable.io/random"
    response = requests.get(url)

    if response.status_code == 200:
        quote_data = response.json()
        return {"quote": quote_data["content"], "author": quote_data["author"]}
    else:
        print(f"API request failed with status code {response.status_code}")
        return None

#Eojify : Working

@bot.slash_command(name="emojify", description="Convert text to letter emojis")
async def emojify(ctx: commands.Context, *, text: str):
    emoji_mapping = {
        "a": ":regional_indicator_a:", "b": ":regional_indicator_b:", "c": ":regional_indicator_c:",
        "d": ":regional_indicator_d:", "e": ":regional_indicator_e:", "f": ":regional_indicator_f:",
        "g": ":regional_indicator_g:", "h": ":regional_indicator_h:", "i": ":regional_indicator_i:",
        "j": ":regional_indicator_j:", "k": ":regional_indicator_k:", "l": ":regional_indicator_l:",
        "m": ":regional_indicator_m:", "n": ":regional_indicator_n:", "o": ":regional_indicator_o:",
        "p": ":regional_indicator_p:", "q": ":regional_indicator_q:", "r": ":regional_indicator_r:",
        "s": ":regional_indicator_s:", "t": ":regional_indicator_t:", "u": ":regional_indicator_u:",
        "v": ":regional_indicator_v:", "w": ":regional_indicator_w:", "x": ":regional_indicator_x:",
        "y": ":regional_indicator_y:", "z": ":regional_indicator_z:",
        "0": ":zero:", "1": ":one:", "2": ":two:", "3": ":three:", "4": ":four:",
        "5": ":five:", "6": ":six:", "7": ":seven:", "8": ":eight:", "9": ":nine:",
        " ": "   "  # Replace a single space with three spaces
    }

    emojified_text = "".join(emoji_mapping.get(char.lower(), char) for char in text)
    await ctx.send(emojified_text)

# TRANSLATE : TEST

@bot.command(name="translate", aliases=["tr"], help="Translate text to a target language.")
async def translate(ctx, target_language: str, *, text_to_translate: str):
    translator = Translator()

    try:
        translation = translator.translate(text_to_translate, dest=target_language)
        translated_text = translation.text

        embed = nextcord.Embed(
            title="Translation Result",
            description=f"**Original Text:** {text_to_translate}\n**Translated Text:** {translated_text}",
            color=0x3498db  # You can customize the color
        )
        await ctx.send(embed=embed)

    except Exception as e:
        print(f"An error occurred: {e}")
        await ctx.send("Translation failed. Please try again.")

#Joke

@bot.slash_command(name='joke', description='Get a random joke')
async def joke(interaction: nextcord.Interaction):
    joke_setup, joke_delivery = await fetch_joke()

    if joke_setup is not None and joke_delivery is not None:
        embed = nextcord.Embed(title='Random Joke', color=0x007dff)  # Yellow color
        embed.add_field(name='Setup', value=joke_setup, inline=False)
        embed.add_field(name='Delivery', value=joke_delivery, inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("Failed to fetch a joke. Please try again later.")

async def fetch_joke():
    async with aiohttp.ClientSession() as session:
        async with session.get('https://v2.jokeapi.dev/joke/Any') as response:
            if response.status == 200:
                data = await response.json()
                return data.get('setup', ''), data.get('delivery', '')
            else:
                return None, None
            
#verification


def RandomNum():
    return str(random.randint(1000, 9999))

def RandomLetter():
    val = ''.join(random.choice(string.ascii_letters) for x in range(5))
    return val

@bot.event
async def on_member_join(member: nextcord.Member):
    channel = bot.get_channel(joinandleftChannelId)

    background = Editor(f'assets/welcome.png')
    if member.avatar is None:
      profile_image = Editor(f'assets/default_pfp.png')
    else:
      profile_image = await load_image_async(str(member.avatar))

    profile = Editor(profile_image).resize((300, 300)).circle_image()

    poppins = Font.poppins(size=50, variant="bold")
    poppins_stroke = Font.poppins(size=52, variant="bold")
    poppins_small = Font.poppins(size=60, variant="light")
    poppins_s_stroke = Font.poppins(size=62, variant="light")

    background.paste(profile, (650, 180))
    background.ellipse((650, 180), 300, 300, outline="white", stroke_width=5)

    discriminator = ""
    if int(member.discriminator) != 0:
        discriminator = f"#{member.discriminator}"

    background.text((800, 520), f"WELCOME TO {member.guild.name}", color="black", font=poppins_stroke, align="center")
    background.text((800, 600), f"{member.name}{discriminator}", color="black", font=poppins_s_stroke, align="center")

    background.text((800, 520), f"WELCOME TO {member.guild.name}", color="white", font=poppins, align="center")
    background.text((800, 600), f"{member.name}{discriminator}", color="white", font=poppins_small, align="center")

    file = File(fp=background.image_bytes, filename="assets/welcome.png")

    await channel.send(f"{member.mention} joined the server!", file=file)
    role = nextcord.utils.get(member.guild.roles, name="Unverified")
    await member.add_roles(role)

    code = RandomNum()
    mydict = { "_id": f"{member.id}", "Code": f"{code}", "Status": f"Not Verified", "Boosting Since": "Never"}
    x = collection.insert_one(mydict)

    width = 130
    height = 100
    message = code
    font = ImageFont.truetype("fonts/marola.ttf", size=30)

    img = Image.new("RGB", (width, height), color="black")
    imgDraw = ImageDraw.Draw(img)
    imgDraw.text((10, 10), message, fill="gray", font=font)

    img.save(f'captchas/{code}.png')

    await member.send(f"Welcome to the server! Verify yourself by typing /verify <code> in the <#{verifyChannelId}> channel.", file=nextcord.File(f'captchas/{code}.png', spoiler=True))
    os.remove(f'captchas/{code}.png')

@bot.event
async def on_member_remove(member: nextcord.Member):
    channel = bot.get_channel(joinandleftChannelId)
    collection.delete_one({"_id": f"{member.id}"})

@bot.slash_command(name="verify", description="Verify yourself to get access to the server")
async def verify(interaction: Interaction, code: str):
    myquery = {"_id": f"{interaction.user.id}"}
    mydoc = collection.find(myquery)
    for x in mydoc:
        if code == x["Code"]:
            await interaction.response.send_message(f"Successfully Verified {interaction.user.mention}!", ephemeral=True)
            collection.update_one(myquery, {"$set": {"Status": "Verified"}})
            role = nextcord.utils.get(interaction.guild.roles, name="Verified")
            await interaction.user.add_roles(role)
            role = nextcord.utils.get(interaction.guild.roles, name="Unverified")
            await interaction.user.remove_roles(role)
        else:
            await interaction.response.send_message("Failed to verify.\nCheck your code and try again.", ephemeral=True)

@bot.slash_command(name="verify_steps", description="Send embed of verification steps.")
async def verify_steps(interaction: Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You are not authorized to use this command!", ephemeral=True)
    else:
        embed = nextcord.Embed(title="How to verify ✔", description="Follow the steps below to verify and get full access to the server!")
        embed.add_field(name="It's pretty simple", value=f"After joining the server you should get a DM from {bot.user.mention} giving you a code, use that code here: <#{verifyChannelId}> by typing the following command: /verify <code>")
        await interaction.response.send_message(embed=embed)

bot.run(token=token)
