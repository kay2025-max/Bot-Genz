
import discord
from discord.ext import commands
import asyncio
import random
import os
from datetime import datetime, timedelta

# Bot setup with all necessary intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} đã sẵn sàng hoạt động!')
    
    # Thiết lập trạng thái streaming
    activity = discord.Streaming(
        name="YouTube Stream",
        url="https://www.youtube.com/watch?si=k8w_-I5jc-L-mwxs&v=bJ_N6o6WRM4&feature=youtu.be"
    )
    await bot.change_presence(activity=activity, status=discord.Status.online)
    
    try:
        synced = await bot.tree.sync()
        print(f'Đã đồng bộ {len(synced)} slash commands')
    except Exception as e:
        print(f'Lỗi đồng bộ commands: {e}')

# MODERATION COMMANDS

@bot.tree.command(name="mute", description="Tắt tiếng thành viên")
async def mute(interaction: discord.Interaction, member: discord.Member, duration: int = 60, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        until = discord.utils.utcnow() + timedelta(minutes=duration)
        await member.timeout(until, reason=reason)
        
        embed = discord.Embed(
            title="🔇 Thành viên đã bị tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Thời gian:** {duration} phút\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi tắt tiếng: {e}", ephemeral=True)

@bot.tree.command(name="unmute", description="Bỏ tắt tiếng thành viên")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not interaction.user.guild_permissions.moderate_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.timeout(None)
        embed = discord.Embed(
            title="🔊 Đã bỏ tắt tiếng",
            description=f"**Thành viên:** {member.mention}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi bỏ tắt tiếng: {e}", ephemeral=True)

@bot.tree.command(name="kick", description="Đuổi thành viên khỏi server")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.kick_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.kick(reason=reason)
        embed = discord.Embed(
            title="👢 Thành viên đã bị đuổi",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi đuổi thành viên: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Cấm thành viên khỏi server")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.ban(reason=reason)
        embed = discord.Embed(
            title="🔨 Thành viên đã bị cấm",
            description=f"**Thành viên:** {member.mention}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.dark_red()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi cấm thành viên: {e}", ephemeral=True)

@bot.tree.command(name="unban", description="Bỏ cấm thành viên")
async def unban(interaction: discord.Interaction, user_id: str, reason: str = "Không có lý do"):
    if not interaction.user.guild_permissions.ban_members:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        user = await bot.fetch_user(int(user_id))
        await interaction.guild.unban(user, reason=reason)
        embed = discord.Embed(
            title="✅ Đã bỏ cấm thành viên",
            description=f"**Thành viên:** {user.mention}\n**Lý do:** {reason}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi bỏ cấm: {e}", ephemeral=True)

# ROLE MANAGEMENT COMMANDS

@bot.tree.command(name="addrole", description="Thêm role cho thành viên")
async def add_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.add_roles(role)
        embed = discord.Embed(
            title="✅ Đã thêm role",
            description=f"**Thành viên:** {member.mention}\n**Role:** {role.mention}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi thêm role: {e}", ephemeral=True)

@bot.tree.command(name="removerole", description="Xóa role khỏi thành viên")
async def remove_role(interaction: discord.Interaction, member: discord.Member, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        await member.remove_roles(role)
        embed = discord.Embed(
            title="➖ Đã xóa role",
            description=f"**Thành viên:** {member.mention}\n**Role:** {role.mention}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.orange()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi xóa role: {e}", ephemeral=True)

@bot.tree.command(name="autorole", description="Tự động thêm role khi thành viên mới vào server")
async def set_autorole(interaction: discord.Interaction, role: discord.Role):
    if not interaction.user.guild_permissions.manage_roles:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    # Lưu autorole vào file hoặc database (ở đây dùng biến toàn cục đơn giản)
    global autorole_data
    if 'autorole_data' not in globals():
        autorole_data = {}
    
    autorole_data[interaction.guild.id] = role.id
    
    embed = discord.Embed(
        title="🤖 Đã thiết lập Auto Role",
        description=f"**Role:** {role.mention}\n**Server:** {interaction.guild.name}",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)

@bot.event
async def on_member_join(member):
    if 'autorole_data' in globals() and member.guild.id in autorole_data:
        role_id = autorole_data[member.guild.id]
        role = member.guild.get_role(role_id)
        if role:
            try:
                await member.add_roles(role)
            except:
                pass

# MESSAGE MANAGEMENT COMMANDS

@bot.tree.command(name="clear", description="Xóa tin nhắn")
async def clear_messages(interaction: discord.Interaction, amount: int):
    if not interaction.user.guild_permissions.manage_messages:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    if amount > 100:
        await interaction.response.send_message("Không thể xóa quá 100 tin nhắn cùng lúc!", ephemeral=True)
        return
    
    try:
        deleted = await interaction.channel.purge(limit=amount)
        embed = discord.Embed(
            title="🗑️ Đã xóa tin nhắn",
            description=f"**Số lượng:** {len(deleted)} tin nhắn\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, delete_after=5)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi xóa tin nhắn: {e}", ephemeral=True)

# NICKNAME MANAGEMENT

@bot.tree.command(name="nick", description="Đổi biệt danh của thành viên")
async def change_nickname(interaction: discord.Interaction, member: discord.Member, nickname: str = None):
    if not interaction.user.guild_permissions.manage_nicknames:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    try:
        old_nick = member.display_name
        await member.edit(nick=nickname)
        
        embed = discord.Embed(
            title="📝 Đã đổi biệt danh",
            description=f"**Thành viên:** {member.mention}\n**Tên cũ:** {old_nick}\n**Tên mới:** {nickname or member.name}\n**Bởi:** {interaction.user.mention}",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)
    except Exception as e:
        await interaction.response.send_message(f"Lỗi khi đổi biệt danh: {e}", ephemeral=True)

# GIVEAWAY SYSTEM

giveaways = {}

@bot.tree.command(name="giveaway", description="Tạo giveaway")
async def create_giveaway(interaction: discord.Interaction, duration: int, winners: int, prize: str):
    if not interaction.user.guild_permissions.manage_guild:
        await interaction.response.send_message("Bạn không có quyền sử dụng lệnh này!", ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎉 GIVEAWAY 🎉",
        description=f"**Phần thưởng:** {prize}\n**Số người thắng:** {winners}\n**Thời gian:** {duration} phút\n**Để tham gia:** React 🎉",
        color=discord.Color.gold(),
        timestamp=discord.utils.utcnow()
    )
    embed.set_footer(text=f"Kết thúc sau {duration} phút")
    
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()
    await message.add_reaction("🎉")
    
    # Lưu thông tin giveaway
    end_time = discord.utils.utcnow() + timedelta(minutes=duration)
    giveaways[message.id] = {
        'channel_id': interaction.channel.id,
        'prize': prize,
        'winners': winners,
        'end_time': end_time,
        'host': interaction.user.id
    }
    
    # Chờ và kết thúc giveaway
    await asyncio.sleep(duration * 60)
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
                    description=f"**Phần thưởng:** {giveaway_data['prize']}\n**Người thắng:** {', '.join(winner_mentions)}",
                    color=discord.Color.green()
                )
            else:
                embed = discord.Embed(
                    title="🎉 GIVEAWAY KẾT THÚC 🎉",
                    description=f"**Phần thưởng:** {giveaway_data['prize']}\n**Kết quả:** Không đủ người tham gia",
                    color=discord.Color.red()
                )
        else:
            embed = discord.Embed(
                title="🎉 GIVEAWAY KẾT THÚC 🎉",
                description=f"**Phần thưởng:** {giveaway_data['prize']}\n**Kết quả:** Không có ai tham gia",
                color=discord.Color.red()
            )
        
        await channel.send(embed=embed)
        
    except Exception as e:
        print(f"Lỗi khi kết thúc giveaway: {e}")
    
    # Xóa giveaway khỏi dictionary
    del giveaways[message_id]

# HELP COMMAND

@bot.tree.command(name="help", description="Hiển thị danh sách lệnh")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="📚 Danh sách lệnh Bot",
        color=discord.Color.blue()
    )
    
    embed.add_field(
        name="🛡️ Moderation",
        value="`/mute` - Tắt tiếng thành viên\n`/unmute` - Bỏ tắt tiếng\n`/kick` - Đuổi thành viên\n`/ban` - Cấm thành viên\n`/unban` - Bỏ cấm thành viên",
        inline=False
    )
    
    embed.add_field(
        name="👥 Role Management",
        value="`/addrole` - Thêm role\n`/removerole` - Xóa role\n`/autorole` - Thiết lập auto role",
        inline=False
    )
    
    embed.add_field(
        name="💬 Message Management",
        value="`/clear` - Xóa tin nhắn\n`/nick` - Đổi biệt danh",
        inline=False
    )
    
    embed.add_field(
        name="🎉 Giveaway",
        value="`/giveaway` - Tạo giveaway",
        inline=False
    )
    
    await interaction.response.send_message(embed=embed)

import os
bot.run(os.getenv("DISCORD_TOKEN"))
