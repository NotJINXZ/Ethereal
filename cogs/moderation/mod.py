from universal import *

class Moderation(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
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

async def setup(bot):
    await bot.add_cog(Moderation(bot))