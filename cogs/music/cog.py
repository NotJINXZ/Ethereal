from universal import *
import spotipy
from wavelink import Client

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not hasattr(bot, 'lavalink'):
            bot.lavalink = Client(bot=bot, host='localhost', port=2333, rest_uri='http://localhost:2333', password='youshallnotpass')
            bot.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'eu', 'music-node')

        bot.add_listener(self.bot.lavalink.voice_update_handler, 'on_socket_response')

    # Hybrid Command: Join a voice channel
    @commands.hybrid_command()
    async def join(self, ctx: commands.Context):
        try:
            channel = ctx.author.voice.channel
            await ctx.voice_channel.connect()
            await ctx.send("Joined the voice channel!")
        except AttributeError:
            await ctx.send("You are not in a voice channel!")

    # Hybrid Command: Play a song
    @commands.hybrid_command()
    async def play(self, ctx: commands.Context, *, query: str):
        try:
            player = self.bot.lavalink.get_player(ctx.guild.id)

            if not player.is_connected:
                channel = ctx.author.voice.channel
                await ctx.voice_channel.connect()

            tracks = await self.bot.lavalink.get_tracks(query)

            if not tracks:
                return await ctx.send('No results found.')

            embed = discord.Embed(color=discord.Color.blurple())

            if 'list' in query.lower():
                embed.title = 'Search results'
                for track in tracks:
                    embed.add_field(name=track['info']['title'], value=f"[{track['info']['uri']}]({track['info']['uri']})")

                return await ctx.send(embed=embed)

            track = tracks[0]

            player.add(requester=ctx.author.id, track=track)

            if not player.is_playing:
                await player.play()

            await ctx.send(f'Now playing: {track["info"]["title"]}')
        except (AttributeError, discord.ClientException):
            await ctx.send("Not connected to a voice channel. Use !join to summon me!")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

    # Hybrid Command: Disconnect from the voice channel
    @commands.hybrid_command()
    async def leave(self, ctx: commands.Context):
        try:
            await ctx.voice_channel.disconnect()
            await ctx.send("Left the voice channel!")
        except AttributeError:
            await ctx.send("I'm not connected to a voice channel!")

def setup(bot):
    bot.add_cog(Music(bot))