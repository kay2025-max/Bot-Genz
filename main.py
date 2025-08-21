
import discord
from discord.ext import commands
import asyncio
import random
import os
import re
from datetime import datetime, timedelta
from discord import app_commands
from config import REACTION_ROLE

# Bot setup with all necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='g!', intents=intents, help_command=None)

def parse_time(time_str):
    """Chuyển đổi chuỗi thời gian thành giây"""

def parse_time(time_str):
    """Chuyển đổi chuỗi thời gian thành giây"""
    time_str = time_str.lower().strip()
    
    # Regex để tìm số và đơn vị
    pattern = r'(\d+)([smhd])'
    matches = re.findall(pattern, time_str)
    
    total_seconds = 0
    for amount, unit in matches:
        amount = int(amount)
        if unit == 's':
            total_seconds += amount
        elif unit == 'm':
            total_seconds += amount * 60
        elif unit == 'h':
            total_seconds += amount * 3600
        elif unit == 'd':
            total_seconds += amount * 86400
    
    return total_seconds if total_seconds > 0 else None

@bot.event
async def on_ready():
    print(f'{bot.user} đã sẵn sàng hoạt động!')
    
    # Thiết lập trạng thái streaming
    activity = discord.Streaming(
        name="/help",
        url="https://www.youtube.com/watch?si=k8w_-I5jc-L-mwxs&v=bJ_N6o6WRM4&feature=youtu.be"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)
    
    try:
        synced = await bot.tree.sync()
        print(f'Đã đồng bộ {len(synced)} slash commands')
    except Exception as e:
        print(f'Lỗi đồng bộ commands: {e}')

# MODERATION COMMANDS

# Slash command: /reactionrole
@bot.tree.command(name="role2", description="Tạo menu reaction role")
async def reactionrole(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Chọn role bằng emoji 🎭",
        description=(
            "🎉 = Giveaway Ping\n"
            "🎮 = Roblox\n"
            "⚔️ = Liên Quân\n"
            "⛏️ = Minecraft\n"
            "🔔 = Update Ping\n"
            "🤝 = Partner Ping"
        ),
        color=discord.Color.green()
    )
    msg = await interaction.channel.send(embed=embed)

    for emoji in REACTION_ROLE.keys():
        await msg.add_reaction(emoji)

    await interaction.response.send_message("✅ Đã tạo reaction role!", ephemeral=True)

# Khi user react
@bot.event
async def on_raw_reaction_add(payload):
    if payload.member.bot:
        return
    guild = bot.get_guild(payload.guild_id)
    role_id = REACTION_ROLE.get(str(payload.emoji))
    if role_id:
        role = guild.get_role(role_id)
        await payload.member.add_roles(role)

# Khi user bỏ react
@bot.event
async def on_raw_reaction_remove(payload):
    guild = bot.get_guild(payload.guild_id)
    member = guild.get_member(payload.user_id)
    role_id = REACTION_ROLE.get(str(payload.emoji))
    if role_id and member:
        role = guild.get_role(role_id)
        await member.remove_roles(role)
        
@bot.tree.command(name="mute", description="Tắt tiếng thành viên")
async def mute_slash(interaction: discord.Interaction, member: discord.Member, duration: str = "60m", reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    duration_seconds = parse_time(duration)
    if not duration_seconds:
        await interaction.response.send_message("Định dạng thời gian không hợp lệ! VD: 1m, 1h, 1d", ephemeral=True)
        return
    
    try:
        until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
        await member.timeout(until, reason=reason)
        
        embed = discord.Embed(
            title="🔇 Thành viên đã bị tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Thời gian:** {duration}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi tắt tiếng: {e}", ephemeral=True)

@bot.command(name="mute")
@commands.has_permissions(moderate_members=True)
async def mute_prefix(ctx, member: discord.Member, duration: str = "60m", *, reason: str = "Không có lý do"):
    duration_seconds = parse_time(duration)
    if not duration_seconds:
        await ctx.send("Định dạng thời gian không hợp lệ! VD: 1m, 1h, 1d")
        return
    
    try:
        until = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
        await member.timeout(until, reason=reason)
        
        embed = discord.Embed(
            title="🔇 Thành viên đã bị tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Thời gian:** {duration}\n**Lý do:** {reason}\n**Bởi:** {ctx.author.mention}",
            color=discord.Color.orange(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Lỗi khi tắt tiếng: {e}")

@bot.tree.command(name="unmute", description="Bỏ tắt tiếng thành viên")
async def unmute_slash(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Đã bỏ tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi bỏ tắt tiếng: {e}", ephemeral=True)

@bot.command(name="unmute")
@commands.has_permissions(moderate_members=True)
async def unmute_prefix(ctx, member: discord.Member):
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Đã bỏ tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Bởi:** {ctx.author.mention}",
            color=discord.Color.green(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Lỗi khi bỏ tắt tiếng: {e}")

@bot.tree.command(name="kick", description="Đuổi thành viên khỏi server")
async def kick_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Thành viên đã bị đuổi",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi đuổi thành viên: {e}", ephemeral=True)

@bot.command(name="kick")
@commands.has_permissions(kick_members=True)
async def kick_prefix(ctx, member: discord.Member, *, reason: str = "Không có lý do"):
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Thành viên đã bị đuổi",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {ctx.author.mention}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Lỗi khi đuổi thành viên: {e}")

@bot.tree.command(name="ban", description="Cấm thành viên khỏi server")
async def ban_slash(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Thành viên đã bị cấm",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi cấm thành viên: {e}", ephemeral=True)

@bot.command(name="ban")
@commands.has_permissions(ban_members=True)
async def ban_prefix(ctx, member: discord.Member, *, reason: str = "Không có lý do"):
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Thành viên đã bị cấm",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {ctx.author.mention}",
            color=discord.Color.dark_red(),
            timestamp=discord.utils.utcnow()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await ctx.send(embed=embed)
    except Exception as e:
        await ctx.send(f"Lỗi khi cấm thành viên: {e}")

@bot.tree.command(name="clear", description="Xóa tin nhắn")
async def clear_slash(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    if amount > 1000:
        await interaction.response.send_message("Không thể xóa quá 100 tin nhắn cùng lúc!", ephemeral=True)
        return
    
    try:
        deleted = await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="🗑️ Đã xóa tin nhắn",
            description=f"**Số lượng:** {len(deleted)} tin nhắn\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await interaction.response.send_message(embed=embed, delete_after=5)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi xóa tin nhắn: {e}", ephemeral=True)

@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear_prefix(ctx, amount: int):
    if amount > 100:
        await ctx.send("Không thể xóa quá 1000 tin nhắn cùng lúc!")
        return
    
    try:
        deleted = await ctx.channel.purge(limit=amount + 1)  # +1 để xóa luôn lệnh
        embed = discord.Embed(
            title="🗑️ Đã xóa tin nhắn",
            description=f"**Số lượng:** {len(deleted)-1} tin nhắn\n**Bởi:** {ctx.author.mention}",
            color=discord.Color.red(),
            timestamp=discord.utils.utcnow()
        )
        await ctx.send(embed=embed, delete_after=5)
    except Exception as e:
        await ctx.send(f"Lỗi khi xóa tin nhắn: {e}")

# GIVEAWAY SYSTEM
giveaways = {}

@bot.tree.command(name="giveaway", description="Tạo giveaway")
async def giveaway_slash(interaction: discord.Interaction, duration: str, winners: int, prize: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    duration_seconds = parse_time(duration)
    if not duration_seconds:
        await interaction.response.send_message("Định dạng thời gian không hợp lệ! VD: 1m, 1h, 1d", ephemeral=True)
        return
    
    end_time = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        color=discord.Color.from_rgb(255, 215, 0),
        timestamp=end_time
    )
    embed.add_field(name="🎁 Phần thưởng", value=f"```{prize}```", inline=False)
    embed.add_field(name="👥 Số người thắng", value=f"```{winners} người```", inline=True)
    embed.add_field(name="⏰ Thời gian", value=f"```{duration}```", inline=True)
    embed.add_field(name="🎯 Cách tham gia", value="React 🎉 để tham gia!", inline=False)
    embed.set_footer(text="Kết thúc vào", icon_url=interaction.user.display_avatar.url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1091158456222040196.gif")
    
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🎉")
    
    # Lưu thông tin giveaway
    giveaways[message.id] = {
        'channel_id': interaction.channel.id,
        'prize': prize,
        'winners': winners,
        'end_time': end_time,
        'host': interaction.user.id,
        'duration_seconds': duration_seconds
    }
    
    # Chờ và kết thúc giveaway
    await asyncio.sleep(duration_seconds)
    await end_giveaway(message.id)

@bot.command(name="giveaway")
@commands.has_permissions(manage_guild=True)
async def giveaway_prefix(ctx, duration: str, winners: int, *, prize: str):
    duration_seconds = parse_time(duration)
    if not duration_seconds:
        await ctx.send("Định dạng thời gian không hợp lệ! VD: 1m, 1h, 1d")
        return
    
    end_time = discord.utils.utcnow() + timedelta(seconds=duration_seconds)
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        color=discord.Color.from_rgb(255, 215, 0),
        timestamp=end_time
    )
    embed.add_field(name="🎁 Phần thưởng", value=f"```{prize}```", inline=False)
    embed.add_field(name="👥 Số người thắng", value=f"```{winners} người```", inline=True)
    embed.add_field(name="⏰ Thời gian", value=f"```{duration}```", inline=True)
    embed.add_field(name="🎯 Cách tham gia", value="React 🎉 để tham gia!", inline=False)
    embed.set_footer(text="Kết thúc vào", icon_url=ctx.author.display_avatar.url)
    embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1091158456222040196.gif")
    
    await ctx.message.delete()
    message = await ctx.send(embed=embed)
    await message.add_reaction("🎉")
    
    # Lưu thông tin giveaway
    giveaways[message.id] = {
        'channel_id': ctx.channel.id,
        'prize': prize,
        'winners': winners,
        'end_time': end_time,
        'host': ctx.author.id,
        'duration_seconds': duration_seconds
    }
    
    # Chờ và kết thúc giveaway
    await asyncio.sleep(duration_seconds)
    await end_giveaway(message.id)

async def end_giveaway(message_id):
    if message_id not in giveaways:
        return
    
    giveaway_data = giveaways[message_id]
    channel = bot.get_channel(giveaway_data['channel_id'])
    
    try:
        message = await channel.fetch_message(message_id)
        reaction = discord.utils.get(message.reactions, emoji="🎉")
        
        if reaction and reaction.count > 1:
            users = [user async for user in reaction.users() if not user.bot]
            
            if len(users) >= giveaway_data['winners']:
                winners = random.sample(users, giveaway_data['winners'])
                winner_mentions = [winner.mention for winner in winners]
                
                embed = discord.Embed(
                    title="🎉 GIVEAWAY KẾT THÚC 🎉",
                    color=discord.Color.green(),
                    timestamp=discord.utils.utcnow()
                )
                embed.add_field(name="🎁 Phần thưởng", value=f"```{giveaway_data['prize']}```", inline=False)
                embed.add_field(name="🏆 Người thắng", value='\n'.join(winner_mentions), inline=False)
                embed.set_footer(text="Chúc mừng các bạn đã thắng!")
                embed.set_thumbnail(url="https://cdn.discordapp.com/emojis/1091158456222040196.gif")
                
                await channel.send(f"🎉 Chúc mừng {', '.join(winner_mentions)}! Bạn đã thắng **{giveaway_data['prize']}**!")
            else:
                embed = discord.Embed(
                    title="🎉 GIVEAWAY KẾT THÚC 🎉",
                    description=f"**Phần thưởng:** {giveaway_data['prize']}\n**Kết quả:** Không đủ người tham gia",
                    color=discord.Color.red(),
                    timestamp=discord.utils.utcnow()
                )
        else:
            embed = discord.Embed(
                title="🎉 GIVEAWAY KẾT THÚC 🎉",
                description=f"**Phần thưởng:** {giveaway_data['prize']}\n**Kết quả:** Không có ai tham gia",
                color=discord.Color.red(),
                timestamp=discord.utils.utcnow()
            )
        
        await channel.send(embed=embed)
        
    except Exception as e:
        print(f"Lỗi khi kết thúc giveaway: {e}")
    
    # Xóa giveaway khỏi dictionary
    del giveaways[message_id]

# HELP COMMANDS

@bot.tree.command(name="help", description="Hiển thị danh sách lệnh")
async def help_slash(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🤖 Bot Commands Help",
        description="**Tất cả lệnh đều có thể dùng với `/` hoặc `g!`**",
        color=discord.Color.from_rgb(88, 101, 242),
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(
        name="🛡️ **Moderation Commands**",
        value="```yaml\n" +
              "mute <user> <time> [reason]  : Tắt tiếng thành viên\n" +
              "unmute <user>                : Bỏ tắt tiếng\n" +
              "kick <user> [reason]         : Đuổi thành viên\n" +
              "ban <user> [reason]          : Cấm thành viên\n" +
              "clear <số lượng>             : Xóa tin nhắn```",
        inline=False
    )
    
    embed.add_field(
        name="🎉 **Giveaway Commands**",
        value="```yaml\n" +
              "giveaway <time> <winners> <prize> : Tạo giveaway```",
        inline=False
    )
    
    embed.add_field(
        name="⏰ **Định dạng thời gian**",
        value="```\n" +
              "1s = 1 giây    |  1m = 1 phút\n" +
              "1h = 1 giờ     |  1d = 1 ngày\n" +
              "VD: 30m, 2h, 1d```",
        inline=False
    )
    
    embed.add_field(
        name="📖 **Ví dụ sử dụng**",
        value="```\n" +
              "g!mute @user 30m spam\n" +
              "/giveaway 1h 2 Nitro 1 tháng\n" +
              "g!clear 10```",
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Được yêu cầu bởi {interaction.user.display_name}", icon_url=interaction.user.display_avatar.url)
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="help")
async def help_prefix(ctx):
    embed = discord.Embed(
        title="🤖 Bot Commands Help",
        description="**Tất cả lệnh đều có thể dùng với `/` hoặc `g!`**",
        color=discord.Color.from_rgb(88, 101, 242),
        timestamp=discord.utils.utcnow()
    )
    
    embed.add_field(
        name="🛡️ **Moderation Commands**",
        value="```yaml\n" +
              "mute <user> <time> [reason]  : Tắt tiếng thành viên\n" +
              "unmute <user>                : Bỏ tắt tiếng\n" +
              "kick <user> [reason]         : Đuổi thành viên\n" +
              "ban <user> [reason]          : Cấm thành viên\n" +
              "clear <số lượng>             : Xóa tin nhắn```",
        inline=False
    )
    
    embed.add_field(
        name="🎉 **Giveaway Commands**",
        value="```yaml\n" +
              "giveaway <time> <winners> <prize> : Tạo giveaway```",
        inline=False
    )
    
    embed.add_field(
        name="⏰ **Định dạng thời gian**",
        value="```\n" +
              "1s = 1 giây    |  1m = 1 phút\n" +
              "1h = 1 giờ     |  1d = 1 ngày\n" +
              "VD: 30m, 2h, 1d```",
        inline=False
    )
    
    embed.add_field(
        name="📖 **Ví dụ sử dụng**",
        value="```\n" +
              "g!mute @user 30m spam\n" +
              "/giveaway 1h 2 Nitro 1 tháng\n" +
              "g!clear 10```",
        inline=False
    )
    
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.set_footer(text=f"Được yêu cầu bởi {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
    
    await ctx.send(embed=embed)


import os
bot.run(os.getenv("DISCORD_TOKEN"))
