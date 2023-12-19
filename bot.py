import discord
from discord import app_commands
from discord.ext import commands
from config import Config
from universal import *
from database import *
import os

ethereal = commands.Bot(command_prefix=None, intents=discord.Intents.all())

ethereal.command_prefix = get_prefix

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

@ethereal.event
async def on_guild_join(guild: discord.Guild):
    init_server(guild.id)

# @ethereal.command(name='setprefix')
# @has_permission("manage_guild")
# async def set_prefix(ctx, new_prefix):
#     custom_prefixes[ctx.guild.id] = new_prefix
#     await ctx.send(f'Prefix set to: `{new_prefix}`')

# @ethereal.hybrid_command(name="prefix")
# @has_permission("manage_guild")
# async def changeprefix(ctx: commands.Context, prefix: str):
#     custom_prefixes[ctx.guild.id] = prefix
#     await ctx.reply(f'Prefix set to: `{prefix}`')   

@ethereal.command(name="sync", description="Sync all slash commands.")
async def sync(ctx: commands.Context):
    try:
        msg = await ctx.reply("Syncing...")
        print("Syncing...")
        synced = await ethereal.tree.sync()
        await msg.edit(content=f"Synced! {len(synced)} commands synced.")
        print(f"Synced! {len(synced)} commands synced.")
    except Exception as e:
        await ctx.reply(content=f"Error: {e}")
        print(f"Error: {e}")

# @ethereal.command(name='example')
# async def example_command(ctx):
#     prefix = ctx.prefix
#     await ctx.send(f'This is an example command! Prefix for this guild is: `{prefix}`')
    
if __name__ == "__main__":
    ethereal.run(Config().token)