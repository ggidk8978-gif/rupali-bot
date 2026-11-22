import os
import random

import discord
from aiohttp import web
from discord import app_commands
from discord.ext import commands

BOT_NAME = "Rupali"

# The token is NOT written here. Set it as the DISCORD_TOKEN environment variable.
TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise SystemExit("Set the DISCORD_TOKEN environment variable first.")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)


async def start_web_server():
    async def health(_request):
        return web.Response(text=f"{BOT_NAME} is running!")

    app = web.Application()
    app.router.add_get("/", health)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 8080))
    await web.TCPSite(runner, "0.0.0.0", port).start()


@bot.event
async def setup_hook():
    await start_web_server()
    await bot.tree.sync()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name=f"{BOT_NAME} | /help"))


@bot.tree.command(name="ping", description="Check the bot's latency")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"Pong! {round(bot.latency * 1000)}ms")


@bot.tree.command(name="hello", description=f"Say hello to {BOT_NAME}")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"Hey {interaction.user.mention}! I'm {BOT_NAME} 👋"
    )


@bot.tree.command(name="roll", description="Roll a dice")
@app_commands.describe(sides="Number of sides (default 6)")
async def roll(interaction: discord.Interaction, sides: app_commands.Range[int, 2, 1000] = 6):
    await interaction.response.send_message(f"🎲 You rolled **{random.randint(1, sides)}** (d{sides})")


@bot.tree.command(name="8ball", description="Ask the magic 8-ball")
@app_commands.describe(question="Your question")
async def eight_ball(interaction: discord.Interaction, question: str):
    answers = ["Yes!", "No.", "Maybe...", "Definitely!", "Ask again later.", "I doubt it.", "Absolutely not."]
    await interaction.response.send_message(f"🎱 **{question}**\n{random.choice(answers)}")


@bot.tree.command(name="serverinfo", description="Show info about this server")
@app_commands.guild_only()
async def serverinfo(interaction: discord.Interaction):
    g = interaction.guild
    embed = discord.Embed(title=g.name, color=discord.Color.blurple())
    embed.add_field(name="Members", value=g.member_count)
    embed.add_field(name="Created", value=g.created_at.strftime("%b %d, %Y"))
    if g.icon:
        embed.set_thumbnail(url=g.icon.url)
    embed.set_footer(text=BOT_NAME)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="clear", description="Delete recent messages")
@app_commands.describe(amount="How many messages to delete (1-100)")
@app_commands.checks.has_permissions(manage_messages=True)
@app_commands.guild_only()
async def clear(interaction: discord.Interaction, amount: app_commands.Range[int, 1, 100]):
    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=amount)
    await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)


@bot.tree.command(name="help", description="List commands")
async def help_cmd(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"**{BOT_NAME} commands:** /ping, /hello, /roll, /8ball, /serverinfo, /clear",
        ephemeral=True,
    )


@bot.tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        msg = "You don't have permission to use that."
    else:
        msg = "Something went wrong."
        print(error)
    if interaction.response.is_done():
        await interaction.followup.send(msg, ephemeral=True)
    else:
        await interaction.response.send_message(msg, ephemeral=True)


bot.run(TOKEN)
               
