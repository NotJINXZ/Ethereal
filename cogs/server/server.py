from universal import *

class Server(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
        
    @commands.hybrid_group(fallback="view")
    async def prefix(self, ctx: commands.Context):
        await ctx.reply(embed=Embed("info", f"The server prefix is: `{get_prefix(self.bot, ctx.message)}`."))
    
    @prefix.command(name="set")
    @has_permission("administrator")
    async def set_prefix(self, ctx: commands.Context, prefix: str):
        update_value(ctx.guild.id, "prefix", str(prefix))
        await ctx.reply(embed=Embed("success", f"Prefix updated to `{prefix}`."))
    
    @prefix.command(name="remove")
    @has_permission("administrator")
    async def remove_prefix(self, ctx: commands.Context):
        update_value(ctx.guild.id, "prefix", None)
        await ctx.reply(embed=Embed("success", "Removed prefix. To re-set it, use slash commands."))
    
    
    
    @commands.hybrid_group(fallback="view")
    @has_permission("manage_guild")
    async def settings(self, ctx: commands.Context):
        await ctx.reply(embed=Embed("info", "Coming Soon!"))

    @settings.command(name="modlogs")
    @has_permission("manage_guild")
    async def set_modlogs(self, ctx: commands.Context, channel: discord.TextChannel):
        update_value(ctx.guild.id, "modlogs", channel.id)
        await ctx.reply(embed=Embed("success", f"Set moderation logs to {channel.mention}."))

    # @settings.command(name="staff")
    # @has_permission("manage_guild")
    # async def settings(self, ctx: commands.Context, role: discord.Role):
    #     update_value(ctx.guild.id, "staff_role", role.id)
    #     await ctx.reply(embed=Embed("success", f"Set staff role to {role.mention}."))

    # @settings.command(name="invokebanmessage")
    # @has_permission("manage_guild")
    # async def settings(self, ctx: commands.Context, message: str):
    #     update_value(ctx.guild.id, "invokebanmessage", )
    #     await ctx.reply(embed=Embed("success", f"Set staff role to {role.mention}."))
    
    @commands.command(name="unpin", description="Unpin a message.")
    @has_permission("manage_messages")
    async def unpin(self, ctx: commands.Context):
        if not ctx.message.reference:
            await ctx.reply(embed=Embed("error", "You did not reply to a message."))
            return
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await message.unpin(reason=f"Message unpinned via @{ctx.author.name}")
        
        await ctx.reply(embed=Embed("approve", "Unpinned message."))
    
    @commands.command(name="pin", description="Pin a message.")
    @has_permission("manage_messages")
    async def pin(self, ctx: commands.Context, message: str = None):
        if message:
            pass
        
        
        if not ctx.message.reference:
            await ctx.reply(embed=Embed("error", "You did not reply to a message."))
            return
        
        message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        await message.unpin(reason=f"Message unpinned via @{ctx.author.name}")
        
        await ctx.reply(embed=Embed("approve", "Unpinned message."))
    
        

async def setup(bot):
    await bot.add_cog(Server(bot))