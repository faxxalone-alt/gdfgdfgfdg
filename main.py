#Credit: Wotax (⚠️Dont Edit)

import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
from flask import Flask
import threading
import aiohttp
from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  

app = Flask(__name__)


load_dotenv()
APPLICATION_ID = os.getenv("APPLICATION_ID")
TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


nomBot = "None"


LANG_NAMES = {
    "en": "English",
    "es": "Spanish",
    "ne": "Nepali",
    "hi": "Hindi",
    "de": "German",
    "it": "Italian",
    "bg": "Bulgarian",
    "gr": "Greek"
}


@app.route('/')
def home():
    global nomBot
    return f"Bot {nomBot} is working"

# Run Flask server
def run_flask():
    app.run(host='0.0.0.0', port=10000)

threading.Thread(target=run_flask).start()

# Bot ready event
@bot.event
async def on_ready():
    global nomBot
    nomBot = f"{bot.user}"
    print(f"✅ Bot is connected as {bot.user}")


@bot.command(name="guilds")
async def show_guilds(ctx):
    guild_names = [f"{i+1}. {guild.name}" for i, guild in enumerate(bot.guilds)]
    guild_list = "\n".join(guild_names)
    await ctx.send(f"The bot is in the following guilds:\n{guild_list}")


@bot.command(name="ID")
async def check_ban_command(ctx):
    content = ctx.message.content
    user_id = content[3:].strip()

    if not user_id.isdigit():
        sent_msg = await ctx.send(f"{ctx.author.mention} ❌ **Invalid UID!**\n➡️ Please use: `!ID 123456789`")
        await sent_msg.delete(delay=6)
        return

    async with ctx.typing():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://checkban-api-wotax.vercel.app/check?uid={user_id}") as resp:
                    if resp.status != 200:
                        sent_msg = await ctx.send(f"{ctx.author.mention} ⚠️ API Error (status {resp.status})")
                        await sent_msg.delete(delay=6)
                        return
                    ban_status = await resp.json()
        except Exception as e:
            sent_msg = await ctx.send(f"{ctx.author.mention} ⚠️ Error:\n```{str(e)}```")
            await sent_msg.delete(delay=6)
            return

        if not ban_status or "nickname" not in ban_status:
            sent_msg = await ctx.send(f"{ctx.author.mention} ❌ **Could not get information. Please try again later.**")
            await sent_msg.delete(delay=6)
            return


        nickname = ban_status.get("nickname", "Unknown")
        level = ban_status.get("level", "N/A")
        region = ban_status.get("region", "N/A")
        ban = ban_status.get("ban_status", "false")
        ban_date = ban_status.get("ban_date", "N/A")
        developer = ban_status.get("developer", "Wotax")

        is_banned = (str(ban).lower() == "true")
        id_str = f"`{user_id}`"

        embed = discord.Embed(
            title="▌ Banned Account 🛑" if is_banned else "▌ Clean Account ✅",
            color=0xFF5F1F if is_banned else 0x1B03A3,
            timestamp=ctx.message.created_at
        )

        embed.description = (
            f"• {'Reason' if is_banned else 'Status'} : "
            f"{'This account was confirmed for using cheats.' if is_banned else 'No sufficient evidence of cheat usage on this account.'}\n"
            f"• Nickname : `{nickname}`\n"
            f"• Player ID : {id_str}\n"
            f"• Region : `{region}`\n"
            f"• Level : {level}"
            f"• Ban Date : {ban_date if is_banned else 'N/A'}\n"
        )

        file = discord.File("assets/banned.gif" if is_banned else "assets/notbanned.gif", filename="status.gif")
        embed.set_image(url="attachment://status.gif")
        embed.set_thumbnail(url=ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url)
        embed.set_footer(text=f"DEVELOPED BY {developer}\nJoin Our Server ❤️ : https://discord.gg/9yCkYfh3Nh")

        await ctx.send(embed=embed, file=file)


@bot.command(name="tr")
async def translate(ctx, lang: str, *, text: str = None):
    if ctx.message.reference and not text:
        ref_msg = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        text = ref_msg.content
    elif not text:
        msg = await ctx.send("❌ Please provide a message or reply to translate.")
        await msg.delete(delay=2)
        return

    try:
        detected_lang_code = detect(text)
        lang_name = LANG_NAMES.get(detected_lang_code, detected_lang_code)
        translator = GoogleTranslator(source="auto", target=lang.lower())
        translated_text = translator.translate(text)
    except Exception as e:
        msg = await ctx.send(f"⚠️ Translation error: {str(e)[:200]}")
        await msg.delete(delay=2)
        return

    embed = discord.Embed(
        description=f"{translated_text[:2000]}",
        color=0x00FFFF
    )
    await ctx.send(embed=embed)


bot.run(TOKEN)

# Credit to Wotax!
# YT: ULTIGER IOS
# DC : Wotax_exe.
