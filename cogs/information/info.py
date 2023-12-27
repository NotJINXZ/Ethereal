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
    @commands.guild_only()
    async def emoji(self, ctx: commands.Context, emoji: discord.Emoji):
        with Image.open(requests.get(emoji.url, stream=True).raw) as img:
            img = img.resize((256, 256))
            
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            
            img_bytes.seek(0)
        
        await ctx.reply(embed=Embed("success", f"Here's the emoji: {emoji}"), file=discord.File(img_bytes, filename=f"{(emoji.name).format(' ', '')}.png"))

    @emoji.command(name="remove", description="Removes emote from server.", aliases=["delete"])
    @app_commands.describe(emoji="The emoji to remove.")
    @commands.guild_only()
    @has_permission("manage_expressions")
    async def emoji_remove(self, ctx: commands.Context, emoji: discord.Emoji):
        await emoji.delete(reason="Emoji remove command.")
        await ctx.reply(embed=Embed("success", f"Deleted emoji **{emoji.name}**."))
        

    @commands.hybrid_command(name="osu", description="Retrieve simple OSU! profile information.")
    @app_commands.describe(username="The username to lookup", game="The game to load stats for.")
    @commands.guild_only()
    async def osu(self, ctx: commands.Context, username: str, game: str):
        games = ['std', 'taiko', 'ctb', 'mania']
        if game.lower() not in games:
            await ctx.reply(embed=Embed(f'Error: Invalid game mode. Allowed game modes are: {", ".join(f"`{game}`")}'))
            return
        
        api_url = f'https://osu.ppy.sh/api/get_user?u={username}&m={game}&k={config.osu}'
        
        response = requests.get(api_url)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                user_data = data[0]
                embed0 = Embed("success", "Successfully fetched profile.")
                embed = discord.Embed(title="OSU! Profile Information", color=discord.Color.green())
                
                fields = [
                    ("Username", user_data['username'], True),
                    ("User ID", user_data['user_id'], True),
                    ("PP", user_data['pp_raw'], True),
                    ("Join Date", user_data['join_date'], True),
                    ("Count 300", user_data['count300'], True),
                    ("Count 100", user_data['count100'], True),
                    ("Count 50", user_data['count50'], True),
                    ("Playcount", user_data['playcount'], True),
                    ("Ranked Score", user_data['ranked_score'], True),
                    ("Total Score", user_data['total_score'], True),
                    ("PP Rank", user_data['pp_rank'], True),
                    ("Level", user_data['level'], True),
                    ("Accuracy", user_data['accuracy'], True),
                    ("Count Rank SS", user_data['count_rank_ss'], True),
                    ("Count Rank SSH", user_data['count_rank_ssh'], True),
                    ("Count Rank S", user_data['count_rank_s'], True),
                    ("Count Rank SH", user_data['count_rank_sh'], True),
                    ("Count Rank A", user_data['count_rank_a'], True),
                    #("Country", user_data['country'], True),
                    ("Total Seconds Played", user_data['total_seconds_played'], True),
                    ("PP Country Rank", user_data['pp_country_rank'], True)
                ]
                
                # events = user_data.get('events', [])
                # if events:
                #     event_text = "\n\n**Events:**\n"
                #     for event in events:
                #         event_text += f"**{event['date']}**: {event['display_html']}\n"
                #     fields.append(("Events", event_text, False))
                
                for name, value, inline in fields:
                    embed.add_field(name=name, value=value, inline=inline)
                
                await ctx.reply(embeds=[embed0, embed])
            else:
                await ctx.reply(embed=Embed("error", "User not found."))
        else:
            await ctx.reply(embed=Embed("error", "Failed to retrieve OSU! profile information. Please try again later."))


async def setup(bot):
    await bot.add_cog(Information(bot))