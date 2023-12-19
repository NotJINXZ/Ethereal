from universal import *

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.cog_loaded = False
        self.reminder_thread = None
        super().__init__()
    
    @commands.hybrid_command(name="tempban")
    @has_permission("ban_members")
    async def tempban_user(self, ctx: commands.Context, member: discord.Member, duration: str, reason: str = None):
        duration_seconds = convert_time(duration)
        if duration_seconds is None:
            await ctx.reply(embed=Embed("error", "Invalid time format. Please use a valid format like `1h`, `1d`, or `1w`."))
            return

        await ctx.guild.ban(member, reason=reason)
        await ctx.reply(embed=Embed("success", f"{member.mention} has been temporarily banned for `{duration}`. Reason: `{reason}`"))
        
        unban_time = asyncio.get_event_loop().time() + duration_seconds
        temp_bans = get_temp_bans(ctx.guild.id)
        temp_bans.append({"user_id": member.id, "unban_time": unban_time, "reason": reason, "duration": duration})
        
        update_temp_bans(ctx.guild.id, temp_bans)
        
    @commands.hybrid_command(name="ban", description="Ban a user from the guild.")
    @has_permission("ban_members")
    @app_commands.describe(member="The member to ban.", reason="The reason for the ban.")
    async def ban(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await member.ban(delete_message_days=None, delete_message_seconds=120, reason=reason)
        if reason is not None: x = f" for {reason}." 
        else: x = ""
        await ctx.reply(embed=Embed("success", f"Banned {member.mention}{x}"))

    @commands.hybrid_command(name="kick", description="Kick a user from the guild.")
    @has_permission("kick_members")
    @app_commands.describe(member="The member to kick.", reason="The reason for the kick.")
    async def kick(self, ctx: commands.Context, member: discord.Member, reason: str = None):
        await member.kick(reason=reason)
        if reason is not None: x = f" for {reason}." 
        else: x = ""
        await ctx.reply(embed=Embed("success", f"Kicked {member.mention}{x}"))
       
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