import discord
from discord import app_commands
from discord.ext import commands
from database import *
import re
import asyncio
import threading
from datetime import timedelta
from config import Config
config = Config()

def get_prefix(bot, message: discord.Message):
    if message.guild:
        custom = get_value(message.guild.id, "prefix")
        if custom:
            return custom
        return config.prefix
    else:
        return config.prefix

def has_permission(permission_names):
    if not isinstance(permission_names, (list, str)):
        raise ValueError("Permission names should be a string or a list of strings.")

    if isinstance(permission_names, str):
        permission_names = [permission_names]

    async def predicate(ctx: commands.Context = None, interaction: discord.Interaction = None):
        missing_permissions = [perm for perm in permission_names if not getattr(ctx.author.guild_permissions, perm, False)]

        if not missing_permissions:
            return True
        else:
            formatted_permissions = [perm.replace('_', ' ').title() for perm in missing_permissions]
            formatted_permissions_str = ", ".join(f"`{perm}`" for perm in formatted_permissions)
            raise commands.CheckFailure(f"You do not have the {formatted_permissions_str} permission(s).")

    return commands.check(predicate)

def Embed(type: str, description: str, **kwargs):
    valid_types = ["info", "warn", "error", "success"]

    if type.lower() not in valid_types:
        raise ValueError("Invalid type for embed.")

    data = {
        "info": {"emoji": "", "color": discord.Color.blurple()},
        "warn": {"emoji": "<:warning:1186447712246321222> ", "color": discord.Color.yellow()},
        "error": {"emoji": "<:deny:1186447716608376868> ", "color": discord.Color.red()},
        "success": {"emoji": "<:approve:1186447714175701043> ", "color": discord.Color.green()}
    }

    data[type].update(kwargs)
    
    embed = discord.Embed(description=f"{data[type]['emoji']}{description}", color=data[type]['color'])
    return embed


def convert_time(time_str):
    time_regex = re.compile(r'(?:(\d+)w)?(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?')
    match = time_regex.match(time_str)

    if match:
        weeks, days, hours, minutes, seconds = map(lambda x: int(x) if x else 0, match.groups())
        total_seconds = weeks * 604800 + days * 86400 + hours * 3600 + minutes * 60 + seconds
        return total_seconds
    return None

success_emoji = discord.PartialEmoji(name="approve", id=1186447714175701043)
error_emoji = discord.PartialEmoji(name="deny", id=1186447716608376868)
warn_emoji = discord.PartialEmoji(name="warning", id=1186447712246321222)