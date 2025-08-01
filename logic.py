from bot_instance import bot
from config import *
from datetime import datetime
from db import dirty_users,buffer_db,connect_db,retrieve,create_temp_user,update_db_loop,shutdown
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from emoji_map import armor, axes, minions, pets, wood, wood_id
import items_map
import json
import math
import psycopg2
from psycopg2 import Error
import random


from ui_helpers import (
    vote_button_callback,
    lb_button_callback,
    forage_button_callback,
    profile_button_callback,
    log_totals_callback,
    shop_button_callback,
    shop_inventory_callback,
    sell_inventory_callback,
    shop_axe_callback,
    shop_armor_callback,
    shop_pet_callback,
    pet_menu_callback,
    shop_minion_callback,
    minion_slot_view_callback,
)

from view import create_view


@commands.has_role("Owner")
@app_commands.default_permissions()
@bot.tree.command(name='sync',description='Sync slash commands')
async def sync(interaction: discord.Interaction):
    if not discord.utils.get(interaction.user.roles, name="Owner"):
        await interaction.response.send_message("❌ You do not have permission to run this command.", ephemeral=True)
        return
    await bot.tree.sync()
    bot_commands = await bot.tree.fetch_commands()
    await interaction.response.send_message(f"{interaction.user.name} has run /sync. {len(bot_commands)} commands synced to tree.")

@commands.has_role("Owner")
@app_commands.default_permissions()
@app_commands.describe(confirm="Type 'TRUNCATE' to confirm this dangerous action",token="Enter TRUNCATE TOKEN to use this command")
@bot.tree.command(name='truncate', description='[WARNING] Truncate ENTIRE forager.stats table!')
async def truncate(interaction: discord.Interaction, confirm: str, token: str):
    if not discord.utils.get(interaction.user.roles, name="Owner"):
        await interaction.response.send_message("❌ You do not have permission to run this command.", ephemeral=True,delete_after=15)
        return

    if confirm != "TRUNCATE":
        await interaction.response.send_message("❌ Cancelled: You must type `TRUNCATE` exactly to proceed.", ephemeral=True, delete_after=15)
        return
    if token != TRUNCATE:
        await interaction.response.send_message("❌ Cancelled: **AUTHORIZATION TOKEN INVALID**.", ephemeral=True, delete_after=15)
        return

    try:
        conn = connect_db()
        exe = conn.cursor()
        exe.execute("SELECT COUNT(*) FROM stats;")
        count = exe.fetchone()[0]

        exe.execute("TRUNCATE stats RESTART IDENTITY;")
        conn.commit()

        await interaction.response.send_message(f"✅ Successfully truncated `stats`. {count} records deleted.")

    except psycopg2.Error as error:
        await interaction.response.send_message(f"❌ An error occurred while truncating the database:\n```{error}```",ephemeral=False)
    finally:
        exe.close()
        conn.close()
    
async def _create_account_logic(interaction: discord.Interaction):
    try:
        conn = connect_db()
        exe = conn.cursor()
        exe.execute("SELECT * FROM stats WHERE dc_id=%s", (interaction.user.id,))
        result = exe.fetchone()

        if not result:
            init_query = """INSERT INTO stats (dc_id, dc_username, xp, balance, axe_type, armor_type, pet_type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            exe.execute(init_query, (interaction.user.id, interaction.user.name, 0, 0, 'None', 'None', 'None'))
            conn.commit()
        else:
            await interaction.response.send_message("User already exists.",ephemeral=True)     
    except psycopg2.Error as error:
        await interaction.followup.send(f"An error occurred while creating your account: {error}")
    finally:
        exe.close()
        conn.close() 

@bot.tree.command(name="create_account", description="Creates user account. (Accounts created automatically)")
async def create_acc(interaction: discord.Interaction):
    await _create_account_logic(interaction)

async def bug_report_logic(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(content=f":heart: Thank you **{interaction.user.name}** for reporting a bug.",ephemeral=True)
    with open('dev_notes/bug_reports.txt', 'a') as file:
        file.write(f"Date: {datetime.now()} | User: {interaction.user.name}({interaction.user.id}): {message}\n")

@bot.tree.command(name='bug_report',description='Report bugs here. Only use this for legitimate bug reports.')
@app_commands.describe(message='Please describe the bug.')
async def bug_report(interaction: discord.Interaction, message:str):
    await bug_report_logic(interaction, message)


async def help_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if not result:
        await _create_account_logic(interaction)

    bot_commands = await bot.tree.fetch_commands()
    command_list = "\n".join(f"``{i+1}. {cmd}``" for i, cmd in enumerate(bot_commands))
    help_embed = discord.Embed(
        title="Welcome to Foraging Bot",
        description=f"""
``Available Commands``
**{command_list}**
**[Vote now!](https://www.top.gg)** and receive a temporary 2x wood multiplier""",
        timestamp=datetime.now(),
        color=discord.Color.purple()
    )
    help_embed.set_author(name=interaction.user)
    view = create_view([
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Shop", "style": discord.ButtonStyle.gray, "emoji": "🛒", "callback": shop_button_callback},
    {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback},
    {"label": "Vote", "emoji": "<a:Vote:1383117707519459418>", "url": "https://www.top.gg/"}

])
    
    await interaction.response.send_message(embed=help_embed, view=view, ephemeral=True)

@bot.tree.command(name='help',description="Get a list of available commands.")
async def help_cmd(interaction: discord.Interaction):
    await help_logic(interaction)


async def vote_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
        
    if not result:
        await _create_account_logic(interaction)
    
    vote_embed = discord.Embed(
        title="Please vote for Foraging Bot",
        description=f"""
Coming Soon!
**[Vote now!](https://www.top.gg)** and receive a temporary 2x wood multiplier""",
        timestamp=datetime.now()
    )
    vote_embed.set_author(name=interaction.user)
    view = create_view([
    {"label": "Vote", "emoji": "<a:Vote:1383117707519459418>", "url": "https://www.top.gg/"},
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback},
    {"label": "Shop", "style": discord.ButtonStyle.gray, "emoji": "🛒", "callback": shop_button_callback},
])
    
    await interaction.response.send_message(embed=vote_embed, view=view, ephemeral=True,delete_after=20)

@bot.tree.command(name='vote',description="Vote for Foraging Bot!")
async def vote(interaction: discord.Interaction):
    await vote_logic(interaction)


from datetime import datetime
import discord
from discord.ui import View, Button

from datetime import datetime
import discord

async def leaderboard_logic(interaction: discord.Interaction, callback: None, page=1):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if not result:
        await _create_account_logic(interaction)

    top_10 = ""
    if page == 1:
        get_query = "SELECT dc_username FROM stats ORDER BY game_level DESC, xp DESC LIMIT 10;"
        sort = "Level"
    elif page == 2:
        get_query = """SELECT dc_username FROM stats ORDER BY balance DESC LIMIT 10;"""
        sort = "Balance"
    else:
        get_query = """SELECT dc_username FROM stats ORDER BY logs DESC LIMIT 10;"""
        sort = "Total Logs Collected"
    conn = connect_db()
    exe = conn.cursor()
    exe.execute(get_query)
    top = exe.fetchall()
    exe.close()
    conn.close()
    top_10 = ""
    for i, user in enumerate(top, start=1):
        username = user[0]  # Extract the string from the tuple
        top_10 += f"**{i}.** {username}\n"
    
    lb_embed= discord.Embed(
        title=f"🏆 Foraging Bot Leaderboard",
        description=f"""Top 10 by {sort}
        {top_10}
        **[Vote now!](https://www.top.gg)** and receive a temporary 2x wood multiplier""",
        timestamp=datetime.now()
        )
    lb_embed.set_author(name=interaction.user)

    view = create_view([
            {"label": "Leaderboard - Game Level","style": discord.ButtonStyle.green,"emoji": "🏆","callback": lb_button_callback, "disabled": page == 1, "kwargs": {'page': 1}},
            {"label": "Leaderboard - Balance","style": discord.ButtonStyle.green,"emoji": "🏆","callback": lb_button_callback, "disabled": page == 2, "kwargs": {'page':2}},
            {"label": "Leaderboard - Logs Collected","style": discord.ButtonStyle.green,"emoji": "🏆","callback": lb_button_callback, "disabled": page == 3, "kwargs": {'page':3}},
            {"label": "Chop Tree","style": discord.ButtonStyle.green,"emoji": "🌳","callback": forage_button_callback},
            {"label": "Profile Stats","style": discord.ButtonStyle.blurple,"emoji": "📄","callback": profile_button_callback},
            {"label": "Shop","style": discord.ButtonStyle.gray,"emoji": "🛒","callback": shop_button_callback}
        ])

    if callback is None:
        await interaction.response.send_message(embed=lb_embed, view=view, ephemeral=True, delete_after=30)
    else:
        await interaction.response.defer()
        await interaction.edit_original_response(embed=lb_embed, view=view)   

@bot.tree.command(name='leaderboard',description="View Top Foragers!")
async def leaderboard(interaction: discord.Interaction):
    await leaderboard_logic(interaction, callback=None)

def xp_for_level(level, base_xp=100, growth_rate=1.3):
    """Calculate XP required to advance FROM this level to the next"""
    return int(base_xp * (growth_rate ** (level - 1)))

async def check_level_up(current_level, current_xp, base_xp=100, growth_rate=1.3):
    """Check if user should level up and return updated stats"""
    leveled_up = False
    while True:
        xp_needed_for_next_level = xp_for_level(current_level, base_xp, growth_rate)
        
        if current_xp >= xp_needed_for_next_level:
            current_level += 1
            current_xp -= xp_needed_for_next_level
            leveled_up = True
        else:
            break
    
    xp_to_next = xp_for_level(current_level, base_xp, growth_rate)
    
    return current_level, current_xp, xp_to_next, leveled_up

async def forage_logic(interaction: discord.Interaction, callback: None):
    user_id = interaction.user.id
    
    await interaction.response.defer(ephemeral=True)
    result = await retrieve(interaction)
    if not result:
        await _create_account_logic(interaction)

    if not user_id in buffer_db:
        await create_temp_user(interaction)
        
    user_data = buffer_db[user_id]
    log_types = ['acacia', 'birch', 'dark_oak', 'oak', 'jungle', 'spruce']
    log_picked = random.choice(log_types)
    logs_broken = random.randint(1, 10)
                       
    if user_data['axe_type'] != 'None':
         logs_broken *= math.floor(items_map.ITEMS['axe_type'][user_data['axe_type']]['power'] / 10)
    xp_gain = 75 * logs_broken if random.random() < 0.05 else random.randint(1, 5) * logs_broken

    pet_type = buffer_db[user_id]['pet_type']
    pet_data = buffer_db[user_id]['pets_inv'].get(pet_type)

    if pet_data:
        pet_level = pet_data.get('pet_level', 0)
        xp_gain *= round(items_map.ITEMS['pet_type'][pet_type]['xp_boost'] * (1.05 + ((pet_level - 1) / 100) * (5.0 - 1.05)))

    user_data["logs"] += logs_broken
    user_data["total_logs"] += logs_broken
    user_data[log_picked] += logs_broken
    user_data[f"total_{log_picked}"] += logs_broken

    #Apply xp to self + check if self levels up
    user_data['xp'] += xp_gain
    new_level, remaining_xp, xp_to_next, leveled_up = await check_level_up(
        user_data['game_level'], user_data['xp'])
    user_data['game_level'] = new_level
    user_data['xp'] = remaining_xp

    #Apply xp to current pet + check if pet levels up
    if user_data['pet_type'] != 'None':
        user_data['pets_inv'][user_data['pet_type']]['pet_xp'] += xp_gain

        new_pet_level, remaining_pet_xp, pet_xp_to_next, pet_leveled_up = await check_level_up(
            user_data['pets_inv'][user_data['pet_type']]['pet_level'], user_data['pets_inv'][user_data['pet_type']]['pet_xp'])
        
        user_data['pets_inv'][user_data['pet_type']]['pet_level'] = new_pet_level
        user_data['pets_inv'][user_data['pet_type']]['pet_xp'] = remaining_pet_xp

    if leveled_up:
        user_data['balance'] += 100 * user_data['game_level']
    dirty_users.add(user_id)
    
    forage_embed = discord.Embed(
        title="Foraging Results",
        description=(
            f"You broke **{logs_broken} {'dark oak' if log_picked == 'dark_oak' else log_picked} {'logs' if logs_broken>1 else 'log'}** and gained **{xp_gain} XP**!\n"
            f"{f'🎉 **You leveled up to level {user_data['game_level']}!** 🎉\nYou received **{100*user_data['game_level']}** coins!\n' if leveled_up else ''}"
            f"{f'🎉 **Your {user_data['pet_type']} leveled up to level {user_data['pets_inv'][user_data['pet_type']]['pet_level']}!** 🎉\n' if user_data['pet_type'] != 'None' and pet_leveled_up else ''}"
            f"Level: {user_data['game_level']} | XP to level {user_data['game_level']+1}: [{user_data['xp']}/{xp_to_next}]"),
        color=0x00CC00,
        timestamp=datetime.now())

    url = f"https://cdn.discordapp.com/emojis/{wood_id[log_picked]}.png"
    forage_embed.set_thumbnail(url=url)
    forage_embed.set_author(name=interaction.user)
    view = create_view([
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Sell Items", "style": discord.ButtonStyle.gray, "emoji": "💵", "callback": sell_inventory_callback},
    {"label": "Shop", "style": discord.ButtonStyle.danger, "emoji": "🛒", "callback": shop_button_callback},
    {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback}
])
    if callback is None:
        await interaction.followup.send(embed=forage_embed, view=view, ephemeral=True)
    else:
        await interaction.edit_original_response(embed=forage_embed, view=view)
            

@bot.tree.command(name='forage', description='Begins foraging')
async def forage_command(interaction: discord.Interaction):
    await forage_logic(interaction, callback=None)

async def profile_logic(interaction: discord.Interaction, callback: None):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    
    if not result:
        await _create_account_logic(interaction)

    _, _, xp_to_next, _ = await check_level_up(
        result['game_level'], result['xp'])
    
    profile_embed = discord.Embed(
        title="**Profile Stats**",
        description=f"""
**Purse**: ${result['balance']:,}\n**Bank**: Coming Soon!
Current level: **{result['game_level']}** | Next Level: **{result['xp']}/{xp_to_next}**
""",
        color=0x0000CC,
        timestamp=datetime.now()
    )
    profile_embed.set_author(name=interaction.user)
    profile_embed.set_thumbnail(url=interaction.user.display_avatar)

    view = create_view([
    [{"label": "View Log Totals", "style": discord.ButtonStyle.blurple, "emoji": f"{wood['oak']}", "callback": log_totals_callback},
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Shop", "style": discord.ButtonStyle.danger, "emoji": "🛒", "callback": shop_button_callback},
    {"label": "Leaderboard", "style": discord.ButtonStyle.blurple, "emoji": "🏆", "callback": lb_button_callback}],
    [{"label": "GitHub", "emoji": "<a:github:1387274840154701874>", "url": "https://github.com/ocrxn/Foraging-Bot"},
    {"label": "Vote", "style": discord.ButtonStyle.danger, "emoji": "<a:Vote:1383117707519459418>", "callback": vote_button_callback}]
])
    if callback is None:
        await interaction.response.send_message(embed=profile_embed, view=view, ephemeral=True,delete_after=120)
    else:
        await interaction.response.defer()
        await interaction.edit_original_response(embed=profile_embed, view=view)
    

@bot.tree.command(name='profile', description='Display Profile Stats')
async def profile_command(interaction: discord.Interaction):
    await profile_logic(interaction, callback=None)

async def log_totals_logic(interaction: discord.Interaction):
    await interaction.response.defer()
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    if not result:
        await _create_account_logic(interaction)
    
    def fmt_block(icon, name, current, total):
        return(f"{icon} **{name} Logs**: {str(current).rjust(5)}\n"
        f"🏆 **Total {name} Collected**: {str(total).rjust(5)}"
)
    lines = [
        f"**Logs in Inventory**: {str(result["logs"]).rjust(5)}\n**🏆All Time Logs Collected**: {str(result["total_logs"]).rjust(5)}",
        fmt_block(f"{wood['acacia']}", "Acacia", result["acacia"], result["total_acacia"]),
        fmt_block(f"{wood['birch']}", "Birch", result["birch"], result["total_birch"]),
        fmt_block(f"{wood['dark_oak']}", "Dark Oak", result["dark_oak"], result["total_dark_oak"]),
        fmt_block(f"{wood['jungle']}", "Jungle", result["jungle"], result["total_jungle"]),
        fmt_block(f"{wood['oak']}", "Oak", result["oak"], result["total_oak"]),
        fmt_block(f"{wood['spruce']}", "Spruce", result["spruce"], result["total_spruce"]),
]
    totals_embed = discord.Embed(
        title=f"Logs Collected Stats\n{wood['acacia']}{wood['birch']}{wood['dark_oak']}{wood['jungle']}{wood['oak']}{wood['spruce']}",
        description="\n\n".join(lines),
        color=0x0000CC,
        timestamp=datetime.now()
    )
    totals_embed.set_thumbnail(url=interaction.user.display_avatar)
    totals_embed.set_author(name=interaction.user)

    view = create_view([
    {"label": "Back to Profile", "style": discord.ButtonStyle.secondary, "emoji": "🔙", "callback": profile_button_callback},
])
    await interaction.edit_original_response(embed=totals_embed, view=view)

async def shop_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if not result:
        await _create_account_logic(interaction)
    
    shop_embed = discord.Embed(
        title="Shop Menu",
        description=f"""Items to purchase.
1. Axe Upgrades (Current: {axes[result['axe_type']] if result['axe_type'] != 'None' else ''}**{result["axe_type"]}**)
2. Armor Upgrades (Current: {armor[result['armor_type']] if result['armor_type'] != 'None' else ''}**{result["armor_type"]}**)
3. Pet Upgrades (Current: {f'{pets[result['pet_type']] if result['pet_type'] != 'None' else 'None'} **{result['pet_type']}**'})
4. Minion Upgrades (Current: **NONE**)
P.S. Voting gives you a temporary 2x wood multiplier
        """,
    timestamp=datetime.now()
    )
    shop_embed.set_author(name=interaction.user)
    row1 = [
        {"label": "Axes", "style": discord.ButtonStyle.blurple, "emoji": f"{axes['diamond_axe']}", "callback": shop_axe_callback},
        {"label": "Armor", "style": discord.ButtonStyle.blurple, "emoji": f"{armor['diamond_armor']}", "callback": shop_armor_callback},
        {"label": "Pets", "style": discord.ButtonStyle.blurple, "emoji": pets.get(result.get("pet_type"), "📄"), "callback": shop_pet_callback},
        {"label": "Minions", "style": discord.ButtonStyle.blurple, "emoji": f"{minions['Oak_I']}", "callback": shop_minion_callback, "args": [{"index": 0}]}
    ]
    row2=[
        {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
        {"label": "Sell Items", "style": discord.ButtonStyle.gray, "emoji": "💵", "callback": sell_inventory_callback},
        {"label": "Inventory", "style": discord.ButtonStyle.secondary, "emoji": "💼", "callback": shop_inventory_callback},
        {"label": "Profile", "style": discord.ButtonStyle.secondary, "emoji": "📄", "callback": profile_button_callback}
    ]
    rows = [row1,row2]
    view = create_view(rows)
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

@bot.tree.command(name='shop', description='Open Shop Menu')
async def shop_command(interaction: discord.Interaction):
    await shop_logic(interaction)

async def shop_inventory_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    
    if not result:
        await _create_account_logic(interaction)
    
    shop_embed = discord.Embed(
        title="Inventory Menu",
        description=f"""
1. Upgrade Inventory
P.S. Voting gives you a temporary 2x wood multiplier
        """,
    timestamp=datetime.now()
    )

    view = create_view([
{"label": "Upgrade Inventory", "style": discord.ButtonStyle.gray, "emoji": "⬆️", "callback": shop_button_callback},        
{"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def sell_inventory_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    lines = [
    (f'1. {wood['logs']} Sell All', result['logs']),
    (f'2. {wood['acacia']} Sell Acacia', result['acacia']),
    (f'3. {wood['birch']} Sell Birch', result['birch']),
    (f'4. {wood['dark_oak']} Sell Dark Oak', result['dark_oak']),
    (f'5. {wood['jungle']} Sell Jungle', result['jungle']),
    (f'6. {wood['oak']} Sell Oak', result['oak']),
    (f'7. {wood['spruce']} Sell Spruce', result['spruce']),
]
    desc = ""
    for left_text, count in lines:
        right_text = f"({count:,} logs: ${count*2:,})"
        total_dots = 80
        desc += f"{left_text:.<{total_dots}}**{right_text}**"+'\n'
    sell_embed = discord.Embed(
            title="Sell Wood Menu",
            description=f"""{desc}
P.S. Voting gives you a temporary 2x wood multiplier
            """,
        timestamp=datetime.now()
        )
    view = create_view([
    {"label": "Sell ALL", "style": discord.ButtonStyle.gray, "emoji": f"{wood['logs']}", 'disabled': result['logs']<1, 'kwargs': {"sell_type": 'logs'}},
    {"label": "Sell Acacia", "style": discord.ButtonStyle.gray, "emoji": f"{wood['acacia']}", 'disabled': result['acacia']<1, 'kwargs': {"sell_type": 'acacia'}},
    {"label": "Sell Birch", "style": discord.ButtonStyle.gray, "emoji": f"{wood['birch']}", 'disabled': result['birch']<1, 'kwargs': {"sell_type": 'birch'}},
    {"label": "Sell Dark Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['dark_oak']}", 'disabled': result['dark_oak']<1, 'kwargs': {"sell_type": 'dark_oak'}},
    {"label": "Sell Jungle", "style": discord.ButtonStyle.gray, "emoji": f"{wood['jungle']}", 'disabled': result['jungle']<1, 'kwargs': {"sell_type": 'jungle'}},
    {"label": "Sell Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['oak']}", 'disabled': result['oak']<1, 'kwargs': {"sell_type": 'oak'}},
    {"label": "Sell Spruce", "style": discord.ButtonStyle.gray, "emoji": f"{wood['spruce']}", 'disabled': result['spruce']<1, 'kwargs': {"sell_type": 'spruce'}},        
    {"label": "Back to [Shop - Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=sell_embed,view=view,ephemeral=True,delete_after=60)

async def shop_axe_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    
    if not result:
        await _create_account_logic(interaction)
    
    item_label = items_map.ITEMS['axe_type']

    max_name_width = max(len(f"{axes[axe]} {axe.replace('_', ' ').title()}") for axe in axes.keys())

    shop_embed = discord.Embed(
        title="Purchase Axes",
        description=f"""Current Axe: **{result["axe_type"].replace('_',' ').title()}**
1. {axes['wooden_axe']} **Wooden Axe**{' ' * (max_name_width - len(f'{axes['wooden_axe']} Wooden Axe'))}   • Price: ${item_label['wooden_axe']['cost']:,} {f'⚡Power: {item_label['wooden_axe']['power']/10}':>30}
2. {axes['stone_axe']} **Stone Axe**{' ' * (max_name_width - len(f'{axes['stone_axe']} Stone Axe'))}   • Price: ${item_label['stone_axe']['cost']:,} {f'⚡Power: {item_label['stone_axe']['power']/10}':>30}
3. {axes['iron_axe']} **Iron Axe**{' ' * (max_name_width - len(f'{axes['iron_axe']} Iron Axe'))}   • Price: ${item_label['iron_axe']['cost']:,} {f'⚡Power: {item_label['iron_axe']['power']/10}':>28}
4. {axes['gold_axe']} **Gold Axe**{' ' * (max_name_width - len(f'{axes['gold_axe']} Gold Axe'))}   • Price: ${item_label['gold_axe']['cost']:,} {f'⚡Power: {item_label['gold_axe']['power']/10}':>26}
5. {axes['diamond_axe']} **Diamond Axe**{' ' * (max_name_width - len(f'{axes['diamond_axe']} Diamond Axe'))}   • Price: ${item_label['diamond_axe']['cost']:,} {f'⚡Power: {item_label['diamond_axe']['power']/10}':>18}
6. {axes['netherite_axe']} **Netherite Axe**{' ' * (max_name_width - len(f'{axes['netherite_axe']} Netherite Axe'))}   • Price: ${item_label['netherite_axe']['cost']:,} {f'⚡Power: {item_label['netherite_axe']['power']/10}':>18}
7. {axes['mythic_axe']} **Mythic Axe**{' ' * (max_name_width - len(f'{axes['mythic_axe']} Mythic Axe'))}   • Price: ${item_label['mythic_axe']['cost']:,} {f'⚡Power: {item_label['mythic_axe']['power']/10}':>17}
P.S. Voting gives you a temporary 2x wood multiplier
        """,
        timestamp=datetime.now()
    )

    view = create_view([                             
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['wooden_axe']}", "item_type": "axe_type", "item_name": "wooden_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['stone_axe']}", "item_type": "axe_type", "item_name": "stone_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['iron_axe']}", "item_type": "axe_type", "item_name": "iron_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['gold_axe']}", "item_type": "axe_type", "item_name": "gold_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['diamond_axe']}", "item_type": "axe_type", "item_name": "diamond_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['netherite_axe']}", "item_type": "axe_type", "item_name": "netherite_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['mythic_axe']}", "item_type": "axe_type", "item_name": "mythic_axe"},
{"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def shop_armor_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    
    if not result:
        await _create_account_logic(interaction)
    
    price_label = items_map.ITEMS['armor_type']
    shop_embed = discord.Embed(
        title="Purchase Armor",
        description=f"""Items to purchase.
1. {armor['leather_armor']} **Leather Armor | Price: ${price_label['leather_armor']['cost']:,}**
2. {armor['chainmail_armor']} **Chainmail Armor | Price: ${price_label['chainmail_armor']['cost']:,}**
3. {armor['iron_armor']} **Iron Armor | Price: ${price_label['iron_armor']['cost']:,}**
4. {armor['gold_armor']} **Gold Armor | Price: ${price_label['gold_armor']['cost']:,}**
5. {armor['diamond_armor']} **Diamond Armor | Price: ${price_label['diamond_armor']['cost']:,}**
6. {armor['netherite_armor']} **Netherite Armor | Price: ${price_label['netherite_armor']['cost']:,}**
7. {armor['mythic_armor']} **Mythic Armor | Price: ${price_label['mythic_armor']['cost']:,}**
P.S. Voting gives you a temporary 2x wood multiplier
        """,
        timestamp=datetime.now()
    )

    view = create_view([
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['leather_armor']}", "item_type": "armor_type", "item_name": "leather_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['chainmail_armor']}", "item_type": "armor_type", "item_name": "chainmail_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['iron_armor']}", "item_type": "armor_type", "item_name": "iron_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['gold_armor']}", "item_type": "armor_type", "item_name": "gold_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['diamond_armor']}", "item_type": "armor_type", "item_name": "diamond_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['netherite_armor']}", "item_type": "armor_type", "item_name": "netherite_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['mythic_armor']}", "item_type": "armor_type", "item_name": "mythic_armor"},
{"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)


async def shop_pet_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    
    if not result:
        await _create_account_logic(interaction)
    
    tier_order = ["COMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"]
    items_dict = items_map.ITEMS["pet_type"]
    current_page = 0

    def make_embed(page):
        tier = tier_order[page]
        desc = f"**{tier} Pets**\n"
        pets_on_page = []
        for pet_name, pet_data in items_dict.items():
            if pet_data["tier"] == tier:
                desc += f"- {pet_name} (Cost: ${pet_data['cost']:,})\n"
                pets_on_page.append(pet_name)
        shop_embed = discord.Embed(title="Purchase Pets", description=desc, timestamp=datetime.now())
        shop_embed.set_footer(text=f"Page {page + 1} of {len(tier_order)}")
        return shop_embed, pets_on_page

    def make_buttons(pets_list):
        row1 = [
            {"label": "", "style": discord.ButtonStyle.blurple, "emoji": "⬅️", "callback": left_callback},
            {"label": "", "style": discord.ButtonStyle.blurple, "emoji": "➡️", "callback": right_callback}
        ]
        buttons = []
        for pet_name in pets_list:
            buttons.append({
                "label": f"Buy {pet_name}",
                "style": discord.ButtonStyle.blurple,
                "emoji": f"{pets[pet_name]}",
                "disabled": pet_name in result['pets_inv'],
                'kwargs': {
                    "item_type": 'pet_type',
                    "item_name": pet_name,
                    "current_page": nonlocal_current_page["page"]
                }
            })
        
        rows = [row1]
        for i in range(0, len(buttons), 5):
            rows.append(buttons[i:i+5])
        rows.append([({"label": "Your Pets", "style": discord.ButtonStyle.green, "emoji": "📄", "callback": pet_menu_callback}),
                    ({"label": "Back to [Shop: Main]", "style": discord.ButtonStyle.danger, "emoji": "🔙", "callback": shop_button_callback})])
        
        return rows


    shop_embed, current_pets = make_embed(current_page)
    nonlocal_current_page = {"page": current_page}

    async def left_callback(interaction: discord.Interaction):
        nonlocal_current_page["page"] = (nonlocal_current_page["page"] - 1) % len(tier_order)
        new_embed, new_pets = make_embed(nonlocal_current_page["page"])
        new_view = create_view(make_buttons(new_pets))
        await interaction.response.edit_message(embed=new_embed, view=new_view)

    async def right_callback(interaction: discord.Interaction):
        nonlocal_current_page["page"] = (nonlocal_current_page["page"] + 1) % len(tier_order)
        new_embed, new_pets = make_embed(nonlocal_current_page["page"])
        new_view = create_view(make_buttons(new_pets))
        await interaction.response.edit_message(embed=new_embed, view=new_view)

    view = create_view(make_buttons(current_pets))
    
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True, delete_after=60)


async def pet_menu_logic(interaction: discord.Interaction):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if isinstance(result.get('pets_inv'), str):
        result['pets_inv'] = json.loads(result['pets_inv'])

    if not result:
        await _create_account_logic(interaction)

    pet_lines = "\n".join(
        f"{pets.get(pet, '')} {pet}: Level {data['pet_level']} ({data['pet_xp']} XP)"
        for pet, data in result['pets_inv'].items())
      
    shop_embed = discord.Embed(
        title="Your Owned Pets",
        description="**No owned pets.** Purchase a pet add it to your collection." if result['pet_type'] == 'None' else f"""
    **Current Pet: {pets[result['pet_type']]} [Lvl {result['pets_inv'][result['pet_type']]['pet_level']}] {result['pet_type']}**
    **{pet_lines}**
    P.S. Voting gives you a temporary 2x wood multiplier
        """,
        timestamp=datetime.now()
    )


    view = create_view([
{"label": "Back to [Shop: Pets]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_pet_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def pet_autocomplete_logic(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if isinstance(result.get('pets_inv'), str):
        result['pets_inv'] = json.loads(result['pets_inv'])
        
    return [
        app_commands.Choice(name=name, value=name)
        for name in result['pets_inv'].keys()
        if current.lower() in name.lower()][:25]

async def equip_pet_logic(interaction: discord.Interaction, pet_name: str):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
        await create_temp_user(interaction)

    if pet_name in result['pets_inv'].keys():
        buffer_db[interaction.user.id]['pet_type'] = pet_name
        dirty_users.add(interaction.user.id)

        await interaction.response.send_message(
            content=f"You equipped {pets.get(pet_name, pet_name)} [Lvl {result['pets_inv'][result['pet_type']]['pet_level']}] {pet_name}!", ephemeral=True)
    else:
        await interaction.response.send_message(
            content=f"Something went wrong.", ephemeral=True)

@bot.tree.command(name='equip_pet', description='Enter name of pet to equip.')
@app_commands.describe(message='Equip pet...')
@app_commands.autocomplete(message=pet_autocomplete_logic)
async def equip_pet(interaction: discord.Interaction, message: str):
    await equip_pet_logic(interaction, message)


async def shop_minion_logic(interaction: discord.Interaction, start_page=0):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if isinstance(result.get('minions'), str):
        result['minions'] = json.loads(result['minions'])

    if not result:
        await _create_account_logic(interaction)

    minion_data = result['minions']
    minion_slots = list(minion_data.items())
    per_page = 5
    total_pages = max(1, (len(minion_slots) + per_page - 1) // per_page)
    current_page = {"index": start_page}

    def make_embed(page: int):
        start = page * per_page
        end = start + per_page
        slot_entries = minion_slots[start:end]

        desc = ""
        for idx, (slot, placed) in enumerate(slot_entries, start=start + 1):
            desc += f"**Slot {idx}**: {placed if placed != 'None' else '*Empty*'}\n"

        embed = discord.Embed(
            title="Minions Menu",
            description=f"""{desc}
**Total Minion Slots: {len(minion_data)}**
**Minions Placed: {len([m for m in minion_data.values() if m != 'None'])}**
P.S. Voting gives you a temporary 2x wood multiplier.
""",
        timestamp=datetime.now()
        )
        embed.set_footer(text=f"Page {page + 1} of {total_pages}")
        return embed

    def button_rows():
        start = current_page["index"] * per_page
        end = start + per_page
        slot_entries = minion_slots[start:end]

        row1 = [{"label": "", "style": discord.ButtonStyle.blurple, "emoji": "⬅️", "callback": left_callback},
             {"label": "", "style": discord.ButtonStyle.blurple, "emoji": "➡️", "callback": right_callback}]
        buttons = []
        for slot, placed in slot_entries:
            buttons.append({
                "label": f"Slot {slot}: {placed if placed != 'None' else 'Empty'}",
                "style": discord.ButtonStyle.blurple,
                "emoji": f"{'◻' if placed == 'None' else f'{minions['Acacia_I']}'}",
                "item_name": f"{slot}",
                "callback": minion_slot_view_callback,
                "args": [slot, current_page]
            })
        rows = [row1]
        for i in range(0, len(buttons), 5):
            rows.append(buttons[i:i+5])
        
        rows.append([
            {"label": "Purchase Additional Minion Slot", "style": discord.ButtonStyle.green, "emoji": "⬆️", "item_type": 'Minion_Type', 'item_name':'slot_costs', 'disabled': len(result["minions"])>=25},
            {"label": "Profile Stats", "style": discord.ButtonStyle.gray, "emoji": "📄", "callback": profile_button_callback},
            {"label": "Back to [Shop: Main]", "style": discord.ButtonStyle.danger, "emoji": "🔙", "callback": shop_button_callback}])
        
        return rows

    async def left_callback(interaction: discord.Interaction):
        current_page["index"] = (current_page["index"] - 1) % total_pages
        new_embed = make_embed(current_page["index"])
        await interaction.response.edit_message(embed=new_embed, view=create_view(button_rows()))

    async def right_callback(interaction: discord.Interaction):
        current_page["index"] = (current_page["index"] + 1) % total_pages
        new_embed = make_embed(current_page["index"])
        await interaction.response.edit_message(embed=new_embed, view=create_view(button_rows()))


    await interaction.response.send_message(embed=make_embed(current_page["index"]), view=create_view(button_rows()), ephemeral=True, delete_after=60)
    

async def minion_slot_view_logic(interaction: discord.Interaction, slot_name, current_page):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)

    if isinstance(result.get('minions'), str):
        result['minions'] = json.loads(result['minions'])

    minion = result["minions"].get(slot_name, "None")

    if minion == "None":
        embed = discord.Embed(
            title=f"Minion Slot {slot_name}: Empty",
            description=f"No minion is placed here.\nWould you like to purchase one?",
            color=discord.Color.dark_red()
        )
        view = create_view([
            [{"label": "Acacia I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Acacia_I']}", "item_type": "Minion_Type", "item_name": 'Acacia I', "current_page": current_page},
            {"label": "Birch I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Birch_I']}", "callback": profile_button_callback},
            {"label": "Dark Oak I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Dark_Oak_I']}", "callback": profile_button_callback}],

            [{"label": "Jungle I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Jungle_I']}", "callback": profile_button_callback},
            {"label": "Oak I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Oak_I']}", "callback": profile_button_callback},
            {"label": "Spruce I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Spruce_I']}", "callback": profile_button_callback}],

            [{"label": "Back", "style": discord.ButtonStyle.gray, "emoji": "↩️", "callback": shop_minion_callback, "args": [current_page]}]
        ])
        await interaction.response.edit_message(embed=embed, view=view)
    else:
        embed = discord.Embed(
            title=f"{minion} — Slot: {slot_name}",
            description=f"""**Level:** {minion['level']}
**Stored Logs:** {minion['storage']}
**XP:** {minion['xp']} / {minion['xp_needed']}
""",
            color=discord.Color.green(),
            timestamp=datetime.now()
        )
        view = create_view([[
            {"label": "Back", "style": discord.ButtonStyle.gray, "emoji": "↩️", "callback": shop_minion_callback, "args": [current_page]}
        ]])
        await interaction.response.edit_message(embed=embed, view=view)




async def is_downgrade(interaction, result, item_type, item_name):
    tier_list = list(items_map.ITEMS[item_type].keys())    
    player_current_item = result[item_type]

    if player_current_item == "None":
        return
    player_index = tier_list.index(player_current_item)
    item_index = tier_list.index(item_name)
    
    return player_index > item_index

async def purchase_item(interaction: discord.Interaction, item_type:str, item_name: str, current_page=2):
    await interaction.response.defer()
    if interaction.user.id not in buffer_db:
        await create_temp_user(interaction)
    result = buffer_db[interaction.user.id]

    if not result:
        await _create_account_logic(interaction)
    
    item_info = items_map.ITEMS.get(item_type, {}).get(item_name)

    if not item_info:
        await interaction.followup.send("This item doesn't exist.", ephemeral=True)
        return

    if item_type == "pet_type":
        cost = item_info["cost"]

        if item_name in buffer_db[interaction.user.id]['pets_inv']:
            await interaction.edit_original_response(content=f"You already own this pet.")
            return

        if result["balance"] < cost:
            await interaction.edit_original_response(content=f"❌ Not enough coins! You need {cost:,}.")
            return

        result['pets_inv'][item_name] = {"pet_level": 0, "pet_xp": 0}
        result['pet_type'] = item_name
        result['balance'] -= cost

        tier_order = ["COMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"]
        items_dict = items_map.ITEMS["pet_type"]
        def make_embed(page):
            tier = tier_order[page]
            desc = f"**{tier} Pets**\n"
            pets_on_page = []
            for pet_name, pet_data in items_dict.items():
                if pet_data["tier"] == tier:
                    desc += f"- {pet_name} (Cost: ${pet_data['cost']:,})\n"
                    pets_on_page.append(pet_name)
            shop_embed = discord.Embed(title="Purchase Pets", description=desc, timestamp=datetime.now())
            shop_embed.set_footer(text=f"Page {page + 1} of {len(tier_order)}")
            return shop_embed, pets_on_page
        
        nonlocal_current_page = {"page": current_page}

        async def left_callback(interaction: discord.Interaction):
            nonlocal_current_page["page"] = (nonlocal_current_page["page"] - 1) % len(tier_order)
            new_embed = make_embed(nonlocal_current_page["page"])[0]
            pets = [pet for pet, data in items_dict.items() if data["tier"] == tier_order[nonlocal_current_page["page"]]]
            new_view = create_view(make_buttons(pets))
            await interaction.response.edit_message(embed=new_embed, view=new_view)

        async def right_callback(interaction: discord.Interaction):
            nonlocal_current_page["page"] = (nonlocal_current_page["page"] + 1) % len(tier_order)
            new_embed = make_embed(nonlocal_current_page["page"])[0]
            pets = [pet for pet, data in items_dict.items() if data["tier"] == tier_order[nonlocal_current_page["page"]]]
            new_view = create_view(make_buttons(pets))
            await interaction.response.edit_message(embed=new_embed, view=new_view)

        # --- Button builder ---
        def make_buttons(pets_list):
            row1 = [
                {"label": "", "style": discord.ButtonStyle.blurple, "emoji": "⬅️", "callback": left_callback},
                {"label": "", "style": discord.ButtonStyle.blurple, "emoji": "➡️", "callback": right_callback}
            ]

            buttons = [{
                "label": f"Buy {pet}",
                "style": discord.ButtonStyle.blurple,
                "emoji": pets[pet],
                "item_type": "pet_type",
                "item_name": pet,
                "disabled": pet in result["pets_inv"],
                "kwargs": {
                    "item_type": "pet_type",
                    "item_name": pet,
                    "current_page": current_page
                }
            } for pet in pets_list]

            rows = [row1]
            for i in range(0, len(buttons), 5):
                rows.append(buttons[i:i+5])

            rows.append([
                {"label": "Your Pets", "style": discord.ButtonStyle.green, "emoji": "📄", "callback": pet_menu_callback},
                {"label": "Back to [Shop: Main]", "style": discord.ButtonStyle.danger, "emoji": "🔙", "callback": shop_button_callback}
            ])

            return rows

        shop_embed, pets_on_page = make_embed(current_page)

        new_view = create_view(make_buttons(pets_on_page))

        await interaction.edit_original_response(content=f"✅ You purchased {pets[item_name]} {item_name} for ${item_info['cost']:,}!",view=new_view)




    elif item_type == "Minion_Type" and item_name == "slot_costs":

        if isinstance(result.get('minions'), str):
            result['minions'] = json.loads(result['minions'])
        
        current_slots = len(result["minions"])
        cost_list = item_info

        if current_slots >= len(cost_list):
            await interaction.edit_original_response(content="❌ You have reached the max number of minion slots!")
            return
        cost = cost_list[current_slots]
        if result["balance"] < cost:
            await interaction.edit_original_response(content=f"❌ Not enough coins! You need {cost:,}.")
            return

        result["minions"][current_slots+1] = 'None'
        result["balance"] -= cost

        item_info = items_map.ITEMS.get('Minion_Type', {}).get("slot_costs")
        current_slots = len(result["minions"])
        shop_embed = discord.Embed(
            title="Minions Menu",
            description=f"""**Total Minion Slots: {len(result['minions'].keys())}**
        **Minions Placed: {len([placed for placed in result['minions'].values() if placed != 'None'])}**
        1. Purchase Additional Minion Slot: **{f'[Price: {item_info[current_slots]}]' if current_slots < 25 else '✅ ALL SLOTS UNLOCKED'}**
        2. View Current Minions
        P.S. Voting gives you a temporary 2x wood multiplier
                """,
            )

        view = create_view([
        {"label": "Purchase Additional Minion Slot", "style": discord.ButtonStyle.green, "emoji": "👷", "item_type": 'Minion_Type', 'item_name':'slot_costs'},
        {"label": "View Current Minions", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": shop_minion_callback},
        {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback},
        {"label": "Back to [Shop: Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
        ])
        await interaction.edit_original_response(embed=shop_embed, view=view, content=f"✅ Slot unlocked! Total slots: {len(result['minions'])}")
    
    elif item_type == "Minion_Type":
        if isinstance(result.get('minions'), str):
            result['minions'] = json.loads(result['minions'])
        
        embed = discord.Embed(
            title=f"Minion Slot {0}: Empty",
            description=f"No minion is placed here.\nWould you like to purchase one?\n{current_page}",
            color=discord.Color.dark_red()
        )
        view = create_view([
            [{"label": "Acacia I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Acacia_I']}", "item_type": "Minion_Type", "item_name": 'Acacia I'},
            {"label": "Birch I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Birch_I']}", "callback": profile_button_callback},
            {"label": "Dark Oak I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Dark_Oak_I']}", "callback": profile_button_callback}],

            [{"label": "Jungle I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Jungle_I']}", "callback": profile_button_callback},
            {"label": "Oak I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Oak_I']}", "callback": profile_button_callback},
            {"label": "Spruce I", "style": discord.ButtonStyle.green, "emoji": f"{minions['Spruce_I']}", "callback": profile_button_callback}],

            [{"label": "Back", "style": discord.ButtonStyle.gray, "emoji": "↩️", "callback": shop_minion_callback, "args": [current_page]}]
        ])
        await interaction.edit_original_response(embed=embed, view=view)

    elif item_type == "axe_type" or item_type == "armor_type":
        cost = item_info["cost"]
        required_current = item_info["required_current"]
        current_item = result[item_type]
        if await is_downgrade(interaction, result, item_type, item_name):
            await interaction.edit_original_response(content="You already own a higher-tier version of this item!")
            return

        if current_item == item_name:
            await interaction.edit_original_response(content=f"You already own **{item_name}**.")
            return
        
        if current_item != required_current:
            await interaction.edit_original_response(content=f"You must own **{required_current}** to purchase **{item_name}**")
            return
        if result["balance"] < cost:
            await interaction.edit_original_response(content=f"You need {cost} coins to purchase **{item_name}**. You only have {result['balance']}")
            return
        result[item_type] = item_name
        result["balance"] -= cost
        await interaction.edit_original_response(content=f"You purchased {item_name} for ${cost:,.2f}.")
    else:
        await interaction.edit_original_response("Unknown item type.", ephemeral=True)
        return
        
    dirty_users.add(interaction.user.id)

async def sell_inventory(interaction: discord.Interaction, sell_type:str, amount=None):
    await interaction.response.defer()
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
        await create_temp_user(interaction)

    if not result:
        await _create_account_logic(interaction)

    lines = [
    (f'1. {wood['logs']} Sell ALL', result['logs']),
    (f'2. {wood['acacia']} Sell Acacia', result['acacia']),
    (f'3. {wood['birch']} Sell Birch', result['birch']),
    (f'4. {wood['dark_oak']} Sell Dark Oak', result['dark_oak']),
    (f'5. {wood['jungle']} Sell Jungle', result['jungle']),
    (f'6. {wood['oak']} Sell Oak', result['oak']),
    (f'7. {wood['spruce']} Sell Spruce', result['spruce']),
]
    desc = ""
    for left_text, count in lines:
        right_text = f"({count:,} | ${count*2:,})"
        total_dots = 80 - len(left_text) - len(right_text)
        desc += f"{left_text}{'.'*total_dots}{right_text}\n"
    profit = result[sell_type]*2
    if amount == 'all':
        amount = result['sell_type']

    if sell_type == "logs":
        amount = result['logs']
        total = result[sell_type]*2
        buffer_db[interaction.user.id]['logs'] = 0
        for log in wood_id:
            buffer_db[interaction.user.id][log] = 0
    elif amount:
        total = amount*2
        buffer_db[interaction.user.id]['logs'] -= amount
        buffer_db[interaction.user.id][sell_type] -= amount
    else:
        total = result[sell_type]*2
        buffer_db[interaction.user.id][sell_type] = 0

    buffer_db[interaction.user.id]['balance'] += total
    dirty_users.add(interaction.user.id)
    sell_embed = discord.Embed(
        title="Sell Wood Menu",
        description=f"""```💵 You sold {amount if amount else 0} {sell_type if sell_type != 'logs' else ''} logs for ${profit:,}.```
    {desc}
    P.S. Voting gives you a temporary 2x wood multiplier
                """,
        timestamp=datetime.now()
    )

    view = create_view([
    {"label": "Sell ALL", "style": discord.ButtonStyle.gray, "emoji": f"{wood['logs']}", 'disabled': result['logs']<1, 'kwargs': {"sell_type": 'logs'}},
    {"label": "Sell Acacia", "style": discord.ButtonStyle.gray, "emoji": f"{wood['acacia']}", 'disabled': result['acacia']<1, 'kwargs': {"sell_type": 'acacia'}},
    {"label": "Sell Birch", "style": discord.ButtonStyle.gray, "emoji": f"{wood['birch']}", 'disabled': result['birch']<1, 'kwargs': {"sell_type": 'birch'}},
    {"label": "Sell Dark Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['dark_oak']}", 'disabled': result['dark_oak']<1, 'kwargs': {"sell_type": 'dark_oak'}},
    {"label": "Sell Jungle", "style": discord.ButtonStyle.gray, "emoji": f"{wood['jungle']}", 'disabled': result['jungle']<1, 'kwargs': {"sell_type": 'jungle'}},
    {"label": "Sell Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['oak']}", 'disabled': result['oak']<1, 'kwargs': {"sell_type": 'oak'}},
    {"label": "Sell Spruce", "style": discord.ButtonStyle.gray, "emoji": f"{wood['spruce']}", 'disabled': result['spruce']<1, 'kwargs': {"sell_type": 'spruce'}},        
    {"label": "Back to [Shop - Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])

    await interaction.edit_original_response(embed=sell_embed,view=view)

async def sell_logic(interaction: discord.Interaction,sell_type, amount):
    await sell_inventory(interaction,sell_type, amount)

@bot.tree.command(name='sa',description='Sell all logs.')
async def sell_all(interaction: discord.Interaction):
    await sell_logic(interaction,sell_type='logs',amount='all')


async def sell_autocomplete(interaction: discord.Interaction, current: str):
    user_id = interaction.user.id
    result = buffer_db.get(user_id) or await retrieve(interaction)
    if not result:
        await _create_account_logic(interaction)

    return [
        app_commands.Choice(name=name, value=name)
        for name in ['acacia','birch','dark_oak','jungle','oak','spruce']
        if current.lower() in name.lower()][:25]

@bot.tree.command(name='sell',description='Sell your logs here...')
@app_commands.describe(sell_type="Enter Log Type or [all]: ",amount="Enter Log Total or [0 for max]: ")
@app_commands.autocomplete(sell_type=sell_autocomplete)
async def sell(interaction: discord.Interaction, sell_type:str, amount:int):
    await sell_logic(interaction, sell_type, amount)