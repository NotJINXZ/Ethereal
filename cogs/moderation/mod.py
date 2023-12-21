from universal import *
from typing import Union

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_loaded = False
        self.reminder_thread = None
        super().__init__()
    
    # @commands.hybrid_command(name="tempban")
    # @has_permission("ban_members")
    # async def tempban_user(self, ctx: commands.Context, member: discord.Member, duration: str, reason: str = None):
    #     duration_seconds = convert_time(duration)
    #     if duration_seconds is None:
    #         await ctx.reply(embed=Embed("error", "Invalid time format. Please use a valid format like `1h`, `1d`, or `1w`."))
    #         return

    #     await ctx.guild.ban(member, reason=reason)
    #     await ctx.reply(embed=Embed("success", f"{member.mention} has been temporarily banned for `{duration}`. Reason: `{reason}`"))
        
    #     unban_time = asyncio.get_event_loop().time() + duration_seconds
    #     temp_bans = get_temp_bans(ctx.guild.id)
    #     temp_bans.append({"user_id": member.id, "unban_time": unban_time, "reason": reason, "duration": duration})
        
    #     update_temp_bans(ctx.guild.id, temp_bans)
        
    @commands.hybrid_command(name="ban", description="Ban a user from the guild.")
    @has_permission("ban_members")
    @app_commands.describe(member="The member to ban.", reason="The reason for the ban.")
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        if reason is not None: x = f" for: `{reason}`." 
        else: x = "."
        await member.send(embed=Embed("info", f"You were banned from {ctx.guild.name}{x}"))
        await member.ban(reason=reason)

        await ctx.reply(embed=Embed("success", f"Banned {member.mention}{x}"))

    @commands.hybrid_command(name="unban", description="Unban a user from the guild.")
    @has_permission("ban_members")
    @app_commands.describe(user="The user to unban.", reason="The reason for the unban.")
    async def unban(self, ctx: commands.Context, user: discord.User, reason: str = None):
        if reason is not None: x = f" for: `{reason}`." 
        else: x = "."
        try:await user.send(embed=Embed("info", f"You were banned from {ctx.guild.name}{x}"))
        except:pass
        await ctx.guild.unban(user, reason=reason)

        await ctx.reply(embed=Embed("success", f"Unbanned {user.mention}{x}"))

    @commands.hybrid_command(name="kick", description="Kick a user from the guild.")
    @has_permission("kick_members")
    @app_commands.describe(member="The member to kick.", reason="The reason for the kick.")
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        if reason is not None: x = f" for: `{reason}`." 
        else: x = "."
        await member.send(embed=Embed("info", f"You were kicked from {ctx.guild.name}{x}"))
        await member.kick(reason=reason)
        await ctx.reply(embed=Embed("success", f"Kicked {member.mention}{x}"))
        
    @commands.hybrid_command(name="mute", description="Mute a user for a specified amount of time.")
    @has_permission("moderate_members")
    @app_commands.describe(member="The member to mute.", time="The amount of time", reason="The reason for the mute.")
    async def mute(self, ctx: commands.Context, member: discord.Member, time: str, reason: str = None):
        if reason is not None: x = f" for: `{reason}`." 
        else: x = "."
        
        #await member.send(embed=Embed("info", f"You were muted in {ctx.guild.name}{x}"))
        await member.timeout(discord.utils.utcnow() + timedelta(seconds=convert_time(time)), reason=reason)
        await ctx.reply(embed=Embed("success", f"Muted {member.mention}{x}"))
        
    @commands.hybrid_command(name="unmute", description="Unmute a user.")
    @has_permission("moderate_members")
    @app_commands.describe(member="The member to unmute.", reason="The reason for the unmute.")
    async def unmute(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        if reason is not None: x = f" for: `{reason}`." 
        else: x = "."
        
        #await member.send(embed=Embed("info", f"You were muted in {ctx.guild.name}{x}"))
        await member.edit(timed_out_until=None, reason=reason)
        await ctx.reply(embed=Embed("success", f"Unmuted {member.mention}{x}"))
    
    @commands.hybrid_command(name="cleanup", description="Delete messages sent by bots.")
    @app_commands.describe(num="The amount of messages to delete.")
    @has_permission("manage_messages")       
    async def cleanup(self, ctx: commands.Context, num: int):
        def is_bot(message):
            return message.author.bot

        deleted_messages = await ctx.channel.purge(limit=num + 1, check=is_bot)

        await ctx.reply(embed=Embed("success", f"Deleted {len(deleted_messages)} message(s)."))
        
    @commands.hybrid_group(name="thread")
    async def thread(self, ctx: commands.Context):
        return
    
    @thread.command(name="lock")
    @app_commands.describe(thread="The thread to lock.", reason="The reason for the lock.")
    @has_permission("manage_threads")
    async def thread_lock(self, ctx: commands.Context, thread: discord.Thread, reason: str = None):
        await thread.edit(locked=True, reason=reason)
        await ctx.reply(embed=Embed("success", f"Locked thread {thread.mention}."))

    @thread.command(name="unlock")
    @app_commands.describe(thread="The thread to unlock.", reason="The reason for the unlock.")
    @has_permission("manage_threads")
    async def thread_unlock(self, ctx: commands.Context, thread: discord.Thread, reason: str = None):
        await thread.edit(locked=False, reason=reason)
        await ctx.reply(embed=Embed("success", f"Unlocked thread {thread.mention}.")) 
        
    @commands.hybrid_command(name="moveall", description="Move all members in current channel to another channel.")
    @has_permission("administrator")
    async def moveall(self, ctx: commands.Context, old_channel: discord.VoiceChannel, new_channel: discord.VoiceChannel):
        if len(old_channel.members) > 10:
            message = ctx.reply(embed=Embed("info", "Starting to move members, This may take a while."))
        for member in old_channel.members:
            await member.move_to(new_channel, reason="Moveall command.")

        embed = Embed("success", f'Moved all members from {old_channel.mention} to {new_channel.mention}.')
        if message:
            await message.edit(embed=embed)
        else:
            await ctx.reply(embed=embed)
        
    @commands.hybrid_group(name="role", fallback="modify", description="Modify a member's roles")
    @app_commands.describe(member="The member to edit.", role="The role to give/remove.")
    @has_permission("manage_roles")
    async def role(self, ctx: commands.Context, member: discord.Member, role: discord.Role):
        if role in member.roles:
            await member.remove_roles(role, reason="Role command.")
            await ctx.reply(embed=Embed("success", f"Removed the role {role.mention} from {member.mention}."))
        else:
            await member.add_roles(role, reason="Role command.")
            await ctx.reply(embed=Embed("success", f"Added the role {role.mention} to {member.mention}."))
            
    @role.command(name="has", description="Add a role to members with a specific role.")
    @app_commands.describe(role="The role to look for", assign_role="The role to give.")
    @has_permission("manage_roles")
    async def role_has(self, ctx: commands.Context, role: discord.Role, assign_role: discord.Role):
        message = await ctx.reply(embed=Embed("info", "Starting to add roles, This may take a while."))
        added = 0
        for member in ctx.guild.members:
            if role in member.roles:
                await member.add_roles(assign_role, reason="Role has command")
                added += 1

        await message.edit(embed=Embed("success", f"Gave the role {assign_role.mention} to {added} people."))
        
    @role.command(name="has_remove", description="Removes a role from members with a specific role.")
    @app_commands.describe(role="The role to look for", remove_role="The role to remove.")
    @has_permission("manage_roles")
    async def role_hasremove(self, ctx: commands.Context, role: discord.Role, remove_role: discord.Role):
        message = await ctx.reply(embed=Embed("info", "Starting to remove roles, This may take a while."))
        removed = 0
        for member in ctx.guild.members:
            if role in member.roles:
                await member.remove_roles(remove_role, reason="Role has remove command")
                removed += 1

        await message.edit(embed=Embed("success", f"Removed the role {remove_role.mention} from {removed} people."))   
        
    @role.command(name="humans", description="Adds a role to every human in the server.")
    @app_commands.describe(role="The role to add.")
    @has_permission("manage_roles")
    async def role_humans(self, ctx: commands.Context, role: discord.Role):
        message = await ctx.reply(embed=Embed("info", "Starting to add roles, This may take a while."))
        added = 0
        for member in ctx.guild.members:
            if member.bot == False:
                await member.add_roles(role, reason="Role humans command")
                added += 1

        await message.edit(embed=Embed("success", f"Added the role {role.mention} to {added} people."))   

    @role.command(name="humans_remove", description="Removes a role from every human in the server.")
    @app_commands.describe(role="The role to remove.")
    @has_permission("manage_roles")
    async def role_humansremove(self, ctx: commands.Context, role: discord.Role):
        message = await ctx.reply(embed=Embed("info", "Starting to remove roles, This may take a while."))
        removed = 0
        for member in ctx.guild.members:
            if member.bot == False:
                await member.remove_roles(role, reason="Role humans remove command")
                removed += 1

        await message.edit(embed=Embed("success", f"Removed the role {role.mention} from {removed} people."))   
        
    @role.command(name="bots", description="Adds a role to every bot in the server.")
    @app_commands.describe(role="The role to add.")
    @has_permission("manage_roles")
    async def role_bots(self, ctx: commands.Context, role: discord.Role):
        message = await ctx.reply(embed=Embed("info", "Starting to add roles, This may take a while."))
        added = 0
        for member in ctx.guild.members:
            if member.bot == True:
                await member.add_roles(role, reason="Role bots command")
                added += 1

        await message.edit(embed=Embed("success", f"Added the role {role.mention} to {added} bots."))   

    @role.command(name="bots_remove", description="Removes a role from every bot in the server.")
    @app_commands.describe(role="The role to remove.")
    @has_permission("manage_roles")
    async def role_botsremove(self, ctx: commands.Context, role: discord.Role):
        message = ctx.reply(embed=Embed("info", "Starting to remove roles, This may take a while."))
        removed = 0
        for member in ctx.guild.members:
            if member.bot == True:
                await member.remove_roles(role, reason="Role bots remove command")
                removed += 1

        await message.edit(embed=Embed("success", f"Removed the role {role.mention} from {removed} bots."))
        
    @commands.hybrid_group(name="purge", description="Deletes the specified amount of messages from the current channel")
    @app_commands.describe(num="The amount of messages to delete", member="The member to delete messages from.")
    @has_permission("manage_messages")
    async def purge(self, ctx: commands.Context, num: int, member: discord.Member = None):
        if num <= 0:
            await ctx.reply(embed=Embed("error", "Please provide a valid number of messages to purge."))
            return
        limit = min(num + 1, 100)

        def is_target_message(message: discord.Message):
            return (member is None or message.author == member) and not message.pinned
        if member:x=f" from {member.mention}."
        else:x="."
        message = await ctx.reply(embed=Embed("info", f"Deleting {limit} messages{x}"))
        deleted = await ctx.channel.purge(limit=limit, check=is_target_message)

        await message.edit(embed=Embed("success", f"Deleted {len(deleted)} messages.")) 

    @purge.command(name="embeds", description="Deletes messages containing embeds from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_embeds(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: len(msg.embeds) > 0)

    @purge.command(name="files", description="Deletes messages containing files/attachments from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_files(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: msg.attachments or msg.content.startswith("http"))

    @purge.command(name="images", description="Deletes messages containing images (including links) from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_images(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: any(attachment.url.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")) for attachment in msg.attachments))

    # @purge.command(name="contains", description="Deletes messages containing the specified substring from the current channel")
    # @app_commands.describe(num="The amount of messages to delete")
    # @has_permission("manage_messages")
    # async def purge_contains(self, ctx: commands.Context, num: int):
    #     await self.purge_messages(ctx, num, lambda msg: True) 

    @purge.command(name="bots", description="Deletes messages from bots in the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_bots(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: msg.author.bot)

    @purge.command(name="before", description="Deletes messages before the specified message ID from the current channel")
    @app_commands.describe(num="The amount of messages to delete", messagelink="Message ID to delete messages before")
    @has_permission("manage_messages")
    async def purge_before(self, ctx: commands.Context, num: int, messagelink: str):
        await self.purge_before_after(ctx, num, lambda msg: msg.id < int(messagelink))

    @purge.command(name="webhooks", description="Deletes messages from webhooks in the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_webhooks(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: msg.webhook_id is not None)

    @purge.command(name="after", description="Deletes messages after the specified message ID from the current channel")
    @app_commands.describe(num="The amount of messages to delete", messagelink="Message ID to delete messages after")
    @has_permission("manage_messages")
    async def purge_after(self, ctx: commands.Context, num: int, messagelink: str):
        await self.purge_before_after(ctx, num, lambda msg: msg.id > int(messagelink))

    @purge.command(name="startswith", description="Deletes messages that start with the specified substring from the current channel")
    @app_commands.describe(num="The amount of messages to delete", substring="Substring to check if messages start with")
    @has_permission("manage_messages")
    async def purge_startswith(self, ctx: commands.Context, num: int, substring: str):
        await self.purge_messages(ctx, num, lambda msg: msg.content.lower().startswith(substring.lower()))

    @purge.command(name="links", description="Deletes messages containing links from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_links(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: any(url in msg.content.lower() for url in ["http", "https"]))

    @purge.command(name="between", description="Deletes messages between two specified message IDs from the current channel")
    @app_commands.describe(num="The amount of messages to delete", startid="Start message ID", finishid="Finish message ID")
    @has_permission("manage_messages")
    async def purge_between(self, ctx: commands.Context, num: int, startid: int, finishid: int):
        await self.purge_messages(ctx, num, lambda msg: startid < msg.id < finishid)

    @purge.command(name="humans", description="Deletes messages from humans in the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_humans(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: not msg.author.bot)

    @purge.command(name="reactions", description="Deletes messages with reactions from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_reactions(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: len(msg.reactions) > 0)

    @purge.command(name="endswith", description="Deletes messages that end with the specified substring from the current channel")
    @app_commands.describe(num="The amount of messages to delete", substring="Substring to check if messages end with")
    @has_permission("manage_messages")
    async def purge_endswith(self, ctx: commands.Context, num: int, substring: str):
        await self.purge_messages(ctx, num, lambda msg: msg.content.lower().endswith(substring.lower()))

    @purge.command(name="emoji", description="Deletes messages containing emojis from the current channel")
    @app_commands.describe(num="The amount of messages to delete")
    @has_permission("manage_messages")
    async def purge_emoji(self, ctx: commands.Context, num: int):
        await self.purge_messages(ctx, num, lambda msg: any(char.isemoji() for char in msg.content))

    @purge.command(name="mentions", description="Deletes messages with mentions for a specific member from the current channel")
    @app_commands.describe(num="The amount of messages to delete", member="Member to filter messages for")
    @has_permission("manage_messages")
    async def purge_mentions(self, ctx: commands.Context, num: int, member: discord.Member):
        await self.purge_messages(ctx, num, lambda msg: member.mention in msg.content)

    @purge.command(name="upto", description="Deletes messages up to the specified message ID from the current channel")
    @app_commands.describe(num="The amount of messages to delete", messagelink="Message ID to delete messages up to")
    @has_permission("manage_messages")
    async def purge_upto(self, ctx: commands.Context, num: int, messagelink: str):
        await self.purge_before_after(ctx, num, lambda msg: msg.id <= int(messagelink))

    async def purge_messages(self, ctx: commands.Context, num: int, check):
        def is_target_message(message: discord.Message):
            return check(message) and not message.pinned

        await ctx.reply(f"Deleting {num} messages...")

        deleted = await ctx.channel.purge(limit=num, check=is_target_message)

        await ctx.send(embed=Embed("success", f"Deleted {len(deleted)} messages."))

    async def purge_before_after(self, ctx: commands.Context, num: int, check):
        def is_target_message(message: discord.Message):
            return check(message) and not message.pinned

        await ctx.reply(f"Deleting {num} messages...")

        deleted = await ctx.channel.purge(limit=num, before=ctx.message, check=is_target_message)

        await ctx.send(embed=Embed("success", f"Deleted {len(deleted)} messages."))

    @commands.hybrid_command("nuke", description="Clone the current channel")
    @app_commands.describe(channel="The channel to clone.")
    @has_permission("administrator")
    async def clone(self, ctx: commands.Context, channel: Union[discord.TextChannel, discord.ForumChannel, discord.StageChannel, discord.VoiceChannel]):
        new_channel = await channel.clone()
        await new_channel.move(category=channel.category)
        await channel.delete(reason="Cloned channel")
          

    # def cog_unload(self):
    #     if self.reminder_thread:
    #         self.reminder_thread.cancel()

    # def start_reminder_thread(self):
    #     self.reminder_thread = self.bot.loop.create_task(self.check_reminders_thread())

    # async def check_reminders_thread(self):
    #     while not self.bot.is_closed():
    #         for user in users_collection.find():
    #             user_id = user["user_id"]
    #             reminders = get_reminders(user_id)
    #             for reminder_info in reminders.copy():
    #                 if asyncio.get_event_loop().time() >= reminder_info['reminder_time']:
    #                     member = self.bot.get_user(user_id)
    #                     if member:
    #                         await member.send(embed=Embed("info", f"Reminder: {reminder_info['message']}"))
    #                     reminders.remove(reminder_info)
    #                     update_reminders(user_id, reminders)

    #         await asyncio.sleep(5)


    # @commands.Cog.listener()
    # async def on_ready(self):
    #     if not self.cog_loaded:
    #         self.cog_loaded = True
    #         self.start_reminder_thread()


    # @commands.hybrid_command(name="reminder")
    # async def set_reminder(self, ctx: commands.Context, duration: str, *, message: str):
    #     # Convert time string to seconds
    #     duration_seconds = convert_time(duration)
    #     if duration_seconds is None:
    #         await ctx.reply(embed=Embed("error", "Invalid time format. Please use a valid format like `1h`, `1d`, or `1w`."))
    #         return
        
    #     reminder_time = asyncio.get_event_loop().time() + duration_seconds
    #     reminders = get_reminders(ctx.author.id)
    #     reminders.append({"reminder_time": reminder_time, "message": message, "duration": duration})
        
    #     update_reminders(ctx.author.id, reminders)
    #     await ctx.reply(embed=Embed("success", f"Reminder set for {duration} from now: {message}"))



async def setup(bot):
    await bot.add_cog(Moderation(bot))