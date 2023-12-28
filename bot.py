import discord
from discord import app_commands
from discord.ext import commands
from config import Config
from universal import *
from database import *
import os
import subprocess
import signal

ethereal = commands.Bot(command_prefix=None, intents=discord.Intents.all())

ethereal.command_prefix = get_prefix
ethereal.owner_id = 1037376739296432210

@ethereal.event
async def on_ready():
    print(f'Logged in as {ethereal.user.name}')

    for foldername, subfolders, filenames in os.walk("cogs"):
        for filename in filenames:
            if filename.endswith(".py"):
                cog_path = os.path.join(foldername, filename)
                cog_name = os.path.splitext(os.path.relpath(cog_path, start="cogs"))[0].replace(os.path.sep, '.')

                try:
                    await ethereal.load_extension(f'cogs.{cog_name}')
                    print(f'Loaded cog: {cog_name}')
                except Exception as e:
                    print(f'Failed to load cog {cog_name}: {type(e).__name__} - {e}')

    
@ethereal.event
async def on_command_error(ctx: commands.Context, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.reply(embed=Embed("error", error))
        return
    elif isinstance(error, commands.CommandError):
        if "Missing Permissions" in str(error):
            await ctx.reply(embed=Embed("error", "I am missing permissions."))
            return

    
    await ctx.reply(embed=Embed("error", str(error) .capitalize()))

@ethereal.event
async def on_guild_join(guild: discord.Guild):
    init_server(guild.id)

@ethereal.event
async def on_message(message: discord.Message):
    if not message.author.bot:
        init_user(message.author.id)
        
    await ethereal.process_commands(message)


@ethereal.command(name="sync", description="Sync all slash commands.")
async def sync(ctx: commands.Context):
    if ctx.author.id != ethereal.owner_id:
        await ctx.reply(embed=Embed("error", "You do not own this bot."))
        return
    try:
        msg = await ctx.reply("Syncing...")
        print("Syncing...")
        synced = await ethereal.tree.sync()
        await msg.edit(content=f"Synced! {len(synced)} commands synced.")
        print(f"Synced! {len(synced)} commands synced.")
    except Exception as e:
        await ctx.reply(content=f"Error: {e}")
        print(f"Error: {e}")
    

if __name__ == "__main__":
    if config.whitelist_dashboard:
        import backend.server
        process_thread = threading.Thread(target=backend.server.start)
        process_thread.start()
        # process_thread.join()

    ethereal.run(config.token)

    print("Program exited.")