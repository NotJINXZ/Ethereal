from universal import *
from PIL import Image
import requests
import io


class Information(commands.GroupCog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        super().__init__()
        
    @commands.hybrid_group(name="emoji", description="Returns a large emoji or server emote", fallback="view")
    @app_commands.describe(emoji="The emoji to view.")
    async def emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        with Image.open(requests.get(emoji.url, stream=True).raw) as img:
            img = img.resize((256, 256))
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            img_bytes.seek(0)
        
        await ctx.reply(embed=Embed("success", f"Here's the emoji: {emoji}"), file=discord.File(img_bytes, filename=f"{(emoji.name).format(' ', '')}.png"))

    @emoji.command(name="remove", description="Removes emote from server.")
    @app_commands.describe(emoji="The emoji to remove.")
    @has_permission("manage_expressions")
    async def emoji_remove(self, ctx: commands.Context, emoji: discord.Emoji):
        await emoji.delete(reason="Emoji remove command.")
        await ctx.reply(embed=Embed("success", f"Deleted emoji **{emoji.name}**."))
        
        

async def setup(bot):
    await bot.add_cog(Information(bot))