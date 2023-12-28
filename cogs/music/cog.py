import asyncio
from typing import cast
from universal import *
import wavelink

class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.skip_votes = {}

    async def setup_hook(self) -> None:
        nodes = [wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")]
        await wavelink.Pool.connect(nodes=nodes, client=self.bot, cache_capacity=100)

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload) -> None:
        print(f"Wavelink Node connected: {payload.node!r} | Resumed: {payload.resumed}")

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            return

        track: wavelink.Playable = payload.track

        embed = discord.Embed(title="Now Playing", description=f"__**{track.title}**__ by **{track.author}**")

        if track.artwork:
            embed.set_image(url=track.artwork)

        await player.home.send(embed=embed)
            
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before, after):
        try:
            if member.id == self.bot.user.id:
                if before.channel is None and after.channel is not None:
                    await member.edit(deafen=True)        
        except discord.errors.Forbidden:
            pass

    @commands.hybrid_command(name="play", description="Play audio via LavaLink")
    @commands.guild_only()
    @app_commands.describe(query="The query to search for.")
    async def play(self, ctx: commands.Context, *, query: str) -> None:
        player: wavelink.Player
        player = cast(wavelink.Player, ctx.voice_client)

        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)
            except AttributeError:
                await ctx.reply(embed=Embed("error", "Please join a voice channel first before using this command."))
                return
            except discord.ClientException:
                await ctx.reply(embed=Embed("error", "I was unable to join this voice channel. Please try again."))
                return

        player.autoplay = wavelink.AutoPlayMode.enabled

        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            message = await ctx.reply(embed=Embed("error", f"You can only play songs in {player.home.mention}, as the player has already started there."))
            return

        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            message = await ctx.reply(embed=Embed("error", f"{ctx.author.mention} - Could not find any tracks with that query. Please try again."))
            return

        if isinstance(tracks, wavelink.Playlist):
            added: int = await player.queue.put_wait(tracks)
            message = await ctx.reply(embed=Embed("success", f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue."))
        else:
            track: wavelink.Playable = tracks[0]
            await player.queue.put_wait(track)
            message = await ctx.reply(embed=Embed("success", f"Added **`{track}`** to the queue."))

        if not player.playing:
            await player.play(player.queue.get(), volume=30)

        try:
            await asyncio.sleep(15)
            await message.delete()
            await ctx.message.delete()
        except discord.HTTPException:
            pass

    @commands.hybrid_command(name="skip", description="Call a vote skip or forcefully skip the current song.")
    async def skip(self, ctx: commands.Context, force: bool = False) -> None:
        player: wavelink.Player = ctx.voice_client

        if not player:
            return await ctx.reply(embed=Embed("error", "I'm not connected to a voice channel."))

        if not force and ctx.channel.id in self.skip_votes:
            return await ctx.reply(embed=Embed("info", "A vote skip is in progress. Use `skip force=True` to force skip the track."))

        if ctx.author.guild_permissions.administrator:
            await player.skip(force=True)
            return await ctx.message.add_reaction(success_emoji)

        if ctx.author.id in self.skip_votes.get(ctx.channel.id, set()):
            return await ctx.send("You have already voted to skip this track in this channel.")

        self.skip_votes.setdefault(ctx.channel.id, set()).add(ctx.author.id)

        channel_members = [
            member for member in ctx.author.voice.channel.members if not member.bot
        ]
        required_votes = int(0.75 * len(channel_members))

        if len(self.skip_votes.get(ctx.channel.id, set())) >= required_votes:
            await player.skip(force=True)
            await ctx.message.add_reaction(success_emoji)
            self.skip_votes.pop(ctx.channel.id, None)
            return await ctx.send(embed=Embed("info", "Vote to skip succeeded! The track has been skipped."))
        else:
            await ctx.reply(embed=Embed("info", f"Vote to skip registered. {len(self.skip_votes.get(ctx.channel.id, set()))}/{required_votes} votes received."))

    @commands.hybrid_command(name="nightcore", description="Enable nightcore mode on the current player. (Higher pitch and speed)")
    async def nightcore(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=1.2, speed=1.2, rate=1)
        await player.set_filters(filters)

        await ctx.message.add_reaction(success_emoji)

    @commands.hybrid_command(name="toggle", aliases=["pause", "resume"], description="Pause/Resume playback of the player.")
    @commands.guild_only()
    async def pause_resume(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.pause(not player.paused)
        await ctx.message.add_reaction(success_emoji)

    @commands.hybrid_command(name="volume", description="Set the current volume of the player.")
    @commands.guild_only()
    @app_commands.describe(value="The volume to set.")
    async def volume(self, ctx: commands.Context, value: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.set_volume(value)
        await ctx.reply(embed=Embed("success", f"Set volume to {value}."))

    @commands.hybrid_command(name="disconnect", description="Disconnect the player from the current channel.", aliases=["dc", "stop"])
    @commands.guild_only()
    async def disconnect(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        await player.disconnect()
        await ctx.reply(embed=Embed("success", f"Adios 👋"))
        
    @commands.hybrid_command(name="queue", description="View the current queue.")
    @commands.guild_only()
    async def queue(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.queue:
            return await ctx.reply(embed=Embed("error", "The queue is empty."))

        queue_info = "\n".join(f"**{index + 1}.** {track}" for index, track in enumerate(player.queue))
        await ctx.reply(embed=Embed("info", f"**Current Queue:**\n{queue_info}"))

    @commands.hybrid_command(name="shuffle", description="Shuffle the current queue.")
    @commands.guild_only()
    async def shuffle(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.queue:
            return await ctx.reply(embed=Embed("error", "The queue is empty."))

        player.queue.shuffle()
        await ctx.message.add_reaction(success_emoji)

    def format_time(seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

    @commands.hybrid_command(name="np", description="Show information about the currently playing track with current time and progress bar.")
    @commands.guild_only()
    async def now_playing(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.current:
            return await ctx.reply(embed=Embed("error", "No track is currently playing."))

        track: wavelink.Playable = player.current
        position = player.position
        duration = track.length

        progress_bar_length = 20
        progress_bar = int(progress_bar_length * (position / duration))
        progress = f"{'=' * progress_bar}>{'.' * (progress_bar_length - progress_bar)}"

        embed = discord.Embed(title="Now Playing", description=f"__**{track.title}**__ by **{track.author}**\n\n"
                                                              f"**Time:** {self.format_time(position)} / {self.format_time(duration)}\n"
                                                              f"**Progress:** [{progress}]")
        if track.artwork:
            embed.set_image(url=track.artwork)

        await ctx.reply(embed=embed)

    @commands.hybrid_command(name="resetfilter", description="Reset any applied filters on the player.")
    @commands.guild_only()
    async def reset_filter(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.reset()
        await player.set_filters(filters)
        await ctx.message.add_reaction(success_emoji)
    
    @commands.hybrid_command(name="restart", description="Restart the current song.")
    @commands.guild_only()
    async def restart(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.current:
            return await ctx.reply(embed=Embed("error", "No track is currently playing."))

        await player.seek(0)
        await ctx.message.add_reaction(success_emoji)
        
    @commands.hybrid_command(name="bassboost", description="Apply bass boost filter to the player.")
    @commands.guild_only()
    async def bass_boost(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.equalizer.set(0, 0.5)
        await player.set_filters(filters)
        await ctx.message.add_reaction(success_emoji)
        
    @commands.hybrid_command(name="trebleboost", description="Apply treble boost filter to the player.")
    @commands.guild_only()
    async def treble_boost(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.equalizer.set(0, 1.5)
        await player.set_filters(filters)
        await ctx.message.add_reaction(success_emoji)

    @commands.hybrid_command(name="vaporwave", description="Apply vaporwave filter to the player.")
    @commands.guild_only()
    async def vaporwave(self, ctx: commands.Context) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player:
            return

        filters: wavelink.Filters = player.filters
        filters.timescale.set(pitch=0.5, speed=0.5, rate=1)
        await player.set_filters(filters)
        await ctx.message.add_reaction(success_emoji)
        
    @commands.hybrid_command(name="skipto", description="Skip to a specific song in the queue.")
    @commands.guild_only()
    @app_commands.describe(index="The index of the song in the queue to skip to.")
    async def skip_to(self, ctx: commands.Context, index: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.queue:
            return await ctx.reply(embed=Embed("error", "The queue is empty."))

        if not (1 <= index <= player.queue.length):
            return await ctx.reply(embed=Embed("error", "Invalid index. Please provide a valid index in the queue."))

        await player.queue.skip_to(index - 1)
        await ctx.message.add_reaction(success_emoji)

    @commands.hybrid_command(name="move", description="Move a song to the top of the queue.")
    @commands.guild_only()
    @app_commands.describe(index="The index of the song in the queue to move to the top.")
    async def move(self, ctx: commands.Context, index: int) -> None:
        player: wavelink.Player = cast(wavelink.Player, ctx.voice_client)
        if not player or not player.queue:
            return await ctx.reply(embed=Embed("error", "The queue is empty."))

        if not (1 <= index <= player.queue.length):
            return await ctx.reply(embed=Embed("error", "Invalid index. Please provide a valid index in the queue."))

        await player.queue.move_to_top(index - 1)
        await ctx.message.add_reaction(success_emoji)

async def setup(bot):
    cog = Music(bot)
    await bot.add_cog(cog)
    await asyncio.create_task(cog.setup_hook())
