from universal import *
import os, json
from urllib.parse import urlparse

class Whitelisting(commands.GroupCog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.enabled = config.whitelist_enabled # Enable the whitelisting system?
        #self.allowed_servers = []
        self.path = os.path.join(os.getcwd(), "whitelisted.json")
        self.process_server_lock = asyncio.Lock()
    
    
    async def process_server(self, server: discord.Guild, event_type=None):
        try:
            async with self.process_server_lock:
                authorized = self.is_server_authorized(server)
                
                if not authorized and self.enabled:
                    async for entry in server.audit_logs(limit=1, action=discord.AuditLogAction.bot_add):
                        if entry.target.id == self.bot.user.id:
                            added_by = entry.user

                            if event_type == 'join':
                                embed = Embed("error", "Hey there! Unfortunately, your server has not been authorized to use this bot. Please contact our support system if this is an error. Have a nice day!")
                            elif event_type == 'message':
                                embed = Embed("error", "Hey there! It seems that either the whitelisting system has been disabled, or your whitelisted status was revoked, so I left your server. Please contact our support system if this is an error. Have a nice day!")
                            else:
                                raise ValueError("Invalid event type.")

                            embeds = [embed]
                            if config.whitelist_dashboard:
                                embed1 = discord.Embed(title="Whitelist your server!", description=f"To whitelist your server, visit [{urlparse(config.whitelist_dashboard_link).netloc}]({config.whitelist_dashboard_link + '?id={}'.format(server.id)})", color=discord.Color.blurple())
                                embeds.append(embed1)

                            await added_by.send(embeds=embeds)
                            await server.leave()
        except:
            pass # Ignore errors

    def is_server_authorized(self, server):
        with open(self.path, "r") as file:
            data = json.load(file)

        return data.get(str(server.id)) == True if data else False

                    
                    
    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        await self.process_server(guild, event_type='join')

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild:
            await self.process_server(message.guild, event_type='message')

    @commands.hybrid_group(name="whitelist", description="Whitelist a guild!", fallback="add")
    @app_commands.describe(guild_id="The guild id to whitelist.")
    async def whitelist(self, ctx: commands.Context, guild_id: int):
        if ctx.author.id not in config.whitelist_access:
            await ctx.reply(embed=Embed("error", "You do not have permission to perform this command."))
            return
    
        
        with open(self.path) as r:
            try:
                data = json.load(r)
            except json.JSONDecodeError:
                print(f"The file {self.path} is not a valid JSON file.")
                data = {}

        if not any(value == True for value in data.values()):
            data = {}
        
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await ctx.reply(embed=Embed("error", f"Guild {guild_id} is not a valid guild."))
            return
        else:
            data[str(guild.id)] = True
            with open(self.path, "w") as w:
                json.dump(data, w)
            
            await ctx.reply(embed=Embed("success", f"Successfully added guild {guild.name} to the whitelist."))
            return
        
    @whitelist.command(name="remove", description="Unwhitelist a guild.")
    @app_commands.describe(guild_id="The guild id to whitelist.")
    async def whitelist_remove(self, ctx: commands.Context, guild_id: int):
        if ctx.author.id not in config.whitelist_access:
            await ctx.reply(embed=Embed("error", "You do not have permission to perform this command."))
            return
    
        with open(self.path) as r:
            try:
                data = json.load(r)
            except json.JSONDecodeError:
                print(f"The file {self.path} is not a valid JSON file.")
                data = {}

        if not any(value == True for value in data.values()):
            data = {}
        
        guild = self.bot.get_guild(guild_id)
        if guild is None:
            await ctx.reply(embed=Embed("error", f"Guild {guild_id} is not a valid guild."))
            return
        else:
            data.pop(str(guild.id))
            with open(self.path, "w") as w:
                json.dump(data, w)
            
            await ctx.reply(embed=Embed("success", f"Successfully removed guild {guild.name} from the whitelist."))
            return

async def setup(bot):
    await bot.add_cog(Whitelisting(bot))
