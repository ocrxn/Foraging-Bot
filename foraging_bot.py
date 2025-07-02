import os
import ast
import discord
from discord import app_commands
from dotenv import load_dotenv
import random
from discord.ext import commands
from discord.ui import Button, View
import mysql.connector
from mysql.connector import Error
from collections import defaultdict
import json
import signal
import sys
import time
import threading
from datetime import datetime
import asyncio
from functools import partial
import items
from emoji_map import axes,armor,wood,wood_id,pets

load_dotenv()
HOST = os.getenv('host_token')
USER = os.getenv('user_token')
PASSWORD = os.getenv('password_token')
DATABASE = os.getenv('database_token')
TOKEN = os.getenv('my_token')
GUILD = os.getenv('my_guild')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="---IDONTLISTENTOPREFIXES---", intents=intents)

#=======================================================
#==================== ✅ BEGIN DATABASE ✅ ====================
#=======================================================
def connect_db():
        return mysql.connector.connect(host=HOST,user=USER,password=PASSWORD,database=DATABASE)

async def retrieve(interaction):
    try:
        conn = connect_db()
        exe = conn.cursor(dictionary=True)
        exe.execute("SELECT * FROM forager.stats WHERE dc_id=%s", (interaction.user.id,))
        result = exe.fetchone()
        if result:
            pets_inv_raw = result['pets_inv']
            if not pets_inv_raw:
                result['pets_inv'] = {}
            else:
                result['pets_inv'] = json.loads(pets_inv_raw)
        return result
    except mysql.connector.Error as error:
        await interaction.followup.send(f"An error occurred while retrieving data: {error}")
    finally:
        exe.close()
        conn.close()

buffer_db = {}
dirty_users = set()
async def create_temp_user(interaction, game_level=0, xp=0,balance=0,
                     Axe_Type="None", Armor_Type="None", Pet_Type="None", logs=0,acacia=0,birch=0,dark_oak=0,
                     jungle=0,oak=0,spruce=0,total_logs=0,total_acacia=0,total_birch=0,total_dark_oak=0,total_jungle=0,total_oak=0,total_spruce=0):
    try:
        result = await retrieve(interaction)
        if result:
            buffer_db[interaction.user.id] = {
                "dc_id": result["dc_id"],
                "game_level": result["game_level"],
                "xp": result['xp'],
                "balance": int(result["balance"]),
                "Axe_Type": result["Axe_Type"],
                "Armor_Type": result["Armor_Type"],
                "Pet_Type": result["Pet_Type"],
                "pets_inv": json.loads(result['pets_inv']) if isinstance(result['pets_inv'], str) else (result['pets_inv'] or {}),
                "logs": result["logs"],
                "acacia": result["acacia"],
                "birch": result["birch"],
                "dark_oak": result["dark_oak"],
                "jungle": result["jungle"],
                "oak": result["oak"],
                "spruce": result["spruce"],
                "total_logs": result["total_logs"],
                "total_acacia": result["total_acacia"],
                "total_birch": result["total_birch"],
                "total_dark_oak": result["total_dark_oak"],
                "total_jungle": result["total_jungle"],
                "total_oak": result["total_oak"],
                "total_spruce": result["total_spruce"]
        }
        else:
            buffer_db[interaction.user.id] = {
                "dc_id": interaction.user.id,
                "game_level": game_level,
                "xp": xp,
                "balance": balance,
                "Axe_Type": Axe_Type,
                "Armor_Type": Armor_Type,
                "Pet_Type": Pet_Type,
                "pets_inv": {},
                "logs": logs,
                "acacia": acacia,
                "birch": birch,
                "dark_oak": dark_oak,
                "jungle": jungle,
                "oak": oak,
                "spruce": spruce,
                "total_logs": total_logs,
                "total_acacia": total_acacia,
                "total_birch": total_birch,
                "total_dark_oak": total_dark_oak,
                "total_jungle": total_jungle,
                "total_oak": total_oak,
                "total_spruce": total_spruce
        }
    except Error:
        print(f"Error while creating temp user: {Error}")

def signal_handler(sig, frame):
    print(f"Signal received: {sig}")
    loop = asyncio.get_event_loop()
    loop.create_task(shutdown())

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

update_task = None
stop_event = asyncio.Event()

async def update_db_loop():
    buffer_query = """UPDATE forager.stats SET
                dc_id = %(dc_id)s,
                game_level = %(game_level)s,
                xp = %(xp)s,
                balance = %(balance)s,
                Axe_Type = %(Axe_Type)s,
                Armor_Type = %(Armor_Type)s,
                Pet_Type = %(Pet_Type)s,
                pets_inv = %(pets_inv)s,
                logs = %(logs)s,
                acacia = %(acacia)s,
                birch = %(birch)s,
                dark_oak = %(dark_oak)s,
                jungle = %(jungle)s,
                oak = %(oak)s,
                spruce = %(spruce)s,
                total_logs = %(total_logs)s,
                total_acacia = %(total_acacia)s,
                total_birch = %(total_birch)s,
                total_dark_oak = %(total_dark_oak)s,
                total_jungle = %(total_jungle)s,
                total_oak = %(total_oak)s,
                total_spruce = %(total_spruce)s
                WHERE dc_id = %(dc_id)s
        """
    try:
        while not stop_event.is_set():
            conn = None
            exe = None
            try:
                if dirty_users:
                    conn = connect_db()
                    exe = conn.cursor()
                    dirty_values = []
                    for user_id in dirty_users:
                        user_copy = buffer_db[user_id].copy()

                        if isinstance(user_copy.get('pets_inv'), dict):
                            user_copy['pets_inv'] = json.dumps(user_copy['pets_inv'])
                        dirty_values.append(user_copy)
                    exe.executemany(buffer_query, dirty_values)
                    conn.commit()
                    dirty_users.clear()
                    print(f"[update_db_loop] 🟢 Database updated at {datetime.now()}")
                    
                else:
                    print(f"[update_db_loop] 🟡 Buffer empty. Timestamp: {datetime.now()}")
                    
            except Exception as e:
                print(f"[update_db_loop] 🔴 WARNING: DB update failed at {datetime.now()}: {e}")
            if exe:
                exe.close()
            if conn:
                conn.close()
            await asyncio.sleep(60)
    except asyncio.CancelledError:
        pass
    finally:
        conn = None
        exe = None
        try:
            if stop_event.is_set():
                conn = connect_db()
                exe = conn.cursor()
                dirty_values = []
                for user_id in dirty_users:
                    user_copy = buffer_db[user_id].copy()

                    if isinstance(user_copy.get('pets_inv'), dict):
                        user_copy['pets_inv'] = json.dumps(user_copy['pets_inv'])
                    dirty_values.append(user_copy)
                exe.executemany(buffer_query, dirty_values)
                conn.commit()
                dirty_users.clear()
                buffer_db.clear() #Cleans the entire buffer on program kill 
                print(f"[update_db_loop] Failsafe update complete at {datetime.now()}.")
        except Exception as e:
            print(f"[update_db_loop] Final DB update failed: {e}")
        finally:
            if exe:
                exe.close()
            if conn:
                conn.close()

async def shutdown():
    print("🔻 Shutdown initiated...\n🔻 Triggering failsafe update...")
    stop_event.set()
    if update_task:
        update_task.cancel()
        try:
            await update_task
        except asyncio.CancelledError:
            pass
    await bot.close()
    print("✅ Bot closed cleanly.")  
#=======================================================
#==================== 🔺 END DATABASE 🔺 ====================
#=======================================================


user_ui_state = {}
  
#=======================================================
#==================== ✅ BEGIN SLASH COMMANDS ✅ ====================
#=======================================================
#Sync command to update bot tree (Owner role required)
@commands.has_role("Owner")
@app_commands.default_permissions()
@bot.tree.command(name='sync',description='Sync slash commands')
async def sync(interaction: discord.Interaction):
    await bot.tree.sync()
    commands = await bot.tree.fetch_commands()
    await interaction.response.send_message(f"{interaction.user.name} has run /sync. {len(commands)} commands synced to tree.")
    
async def bug_report_logic(interaction: discord.Interaction, message:str):
    await interaction.response.send_message(content=f":heart: Thank you **{interaction.user.name}** for reporting a bug.",ephemeral=True)
    with open('dev_notes/bug_reports.txt', 'a') as bug_report:
        bug_report.write(f"Date: {datetime.now()} | User: {interaction.user.name}({interaction.user.id}): {message}\n")

@bot.tree.command(name='bug_report',description='Report bugs here. Only use this for legitimate bug reports.')
@app_commands.describe(message='Please describe the bug.')
async def bug_report(interaction: discord.Interaction, message:str):
    await bug_report_logic(interaction, message)


async def vote_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
        
    if not result:
        await interaction.response.send_message("Welcome to Foraging Bot.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
    else:
        vote_embed = discord.Embed(
            title="Please vote for Foraging Bot",
            description=f"""
Coming Soon!
**[Vote now!](https://www.top.gg)** and receive a temporary 2x wood multiplier""",
        )

        view = create_view([
    {"label": "Vote", "emoji": "<a:Vote:1383117707519459418>", "url": "https://www.top.gg/"},
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback},
    {"label": "Shop", "style": discord.ButtonStyle.gray, "emoji": "🛒", "callback": shop_button_callback},
])
        vote_embed.set_footer(text='Made by ocrxn')
        vote_embed.set_author(name=interaction.user)
        await interaction.response.send_message(embed=vote_embed, view=view, ephemeral=True,delete_after=6)

@bot.tree.command(name='vote',description="Vote for Foraging Bot!")
async def vote(interaction: discord.Interaction):
    await vote_logic(interaction)

@bot.tree.command(name="create_account", description="Creates user account.")
async def create_acc(interaction: discord.Interaction):
    try:
        conn = connect_db()
        exe = conn.cursor()
        exe.execute("SELECT * FROM forager.stats WHERE dc_id=%s", (interaction.user.id,))
        result = exe.fetchone()

        if not result:
            await interaction.response.defer(thinking=True)
            init_query = """INSERT INTO forager.stats (dc_id, dc_username, game_level, xp, balance, Axe_Type, Armor_Type, Pet_Type)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            exe.execute(init_query, (interaction.user.id, interaction.user.name, 0, 0, 0, 'None', 'None', 'None'))
            conn.commit()  
            await interaction.followup.send(content="Account created successfully.",ephemeral=True)
        else:
            await interaction.response.send_message("User already exists.",ephemeral=True)     
    except mysql.connector.Error as error:
        await interaction.followup.send(f"An error occurred while creating your account: {error}")
    finally:
        exe.close()
        conn.close() 

def xp_for_level(level, base_xp=100, growth_rate=1.3):
    """Calculate XP required to advance FROM this level to the next"""
    return int(base_xp * (growth_rate ** (level - 1)))

async def check_level_up(current_level, current_xp, base_xp=100, growth_rate=1.3):
    """Check if user should level up and return updated stats"""
    leveled_up = False
    
    # Keep checking for level ups (in case of multiple levels gained)
    while True:
        xp_needed_for_next_level = xp_for_level(current_level, base_xp, growth_rate)
        
        if current_xp >= xp_needed_for_next_level:
            current_level += 1
            current_xp -= xp_needed_for_next_level
            leveled_up = True
        else:
            break
    
    # Calculate XP needed for next level
    xp_to_next = xp_for_level(current_level, base_xp, growth_rate)
    
    return current_level, current_xp, xp_to_next, leveled_up

async def forage_logic(interaction: discord.Interaction, callback: None):
    user_id = interaction.user.id

    if not user_id in buffer_db:
        result = await retrieve(interaction)
        if not result:
            await interaction.response.send_message("You do not have an account.\nTry running **/create_account** first.",ephemeral=True,delete_after=15)
            return
        await create_temp_user(interaction)
    user_data = buffer_db[user_id]
    log_types = ['acacia', 'birch', 'dark_oak', 'oak', 'jungle', 'spruce']
    log_picked = random.choice(log_types)
    logs_broken = int(random.randint(1, 10) * items.ITEMS['Axe_Type'][user_data['Axe_Type']]['power']) // 10
    xp_gain = 75 * logs_broken if random.random() < 0.05 else random.randint(1, 5) * logs_broken

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
    if user_data['Pet_Type'] != 'None':
        user_data['pets_inv'][user_data['Pet_Type']]['pet_xp'] += xp_gain

        new_pet_level, remaining_pet_xp, pet_xp_to_next, pet_leveled_up = await check_level_up(
            user_data['pets_inv'][user_data['Pet_Type']]['pet_level'], user_data['pets_inv'][user_data['Pet_Type']]['pet_xp'])
        
        user_data['pets_inv'][user_data['Pet_Type']]['pet_level'] = new_pet_level
        user_data['pets_inv'][user_data['Pet_Type']]['pet_xp'] = remaining_pet_xp

    if leveled_up:
        user_data['balance'] += 100 * user_data['game_level']
    dirty_users.add(user_id)
    
    forage_embed = discord.Embed(
        title="Foraging Results",
        description=(
            f"You broke **{logs_broken} {'dark oak' if log_picked == 'dark_oak' else log_picked} {'logs' if logs_broken>1 else 'log'}** and gained **{xp_gain} XP**!\n"
            f"{f'🎉 **You leveled up to level {user_data['game_level']}!** 🎉\nYou received **{100*user_data['game_level']}** coins!\n' if leveled_up else ''}"
            f"{f'🎉 **Your {user_data['Pet_Type']} leveled up to level {user_data['pets_inv'][user_data['Pet_Type']]['pet_level']}!** 🎉\n' if pet_leveled_up else ''}"
            f"Level: {user_data['game_level']} | XP to level {user_data['game_level']+1}: [{user_data['xp']}/{xp_to_next}]"
        ),color=0x00CC00)

    url = f"https://cdn.discordapp.com/emojis/{wood_id[log_picked]}.png"
    forage_embed.set_thumbnail(url=url)
    forage_embed.set_footer(text='Made by ocrxn')
    forage_embed.set_author(name=interaction.user)
    view = create_view([
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Sell Items", "style": discord.ButtonStyle.gray, "emoji": "💵", "callback": sell_inventory_callback},
    {"label": "Shop", "style": discord.ButtonStyle.danger, "emoji": "🛒", "callback": shop_button_callback},
    {"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback}
])
    if callback is None:
        await interaction.response.send_message(embed=forage_embed, view=view, ephemeral=True)
    else:
        await interaction.response.defer()
        await interaction.edit_original_response(embed=forage_embed, view=view)
            

@bot.tree.command(name='forage', description='Begins foraging')
async def forage_command(interaction: discord.Interaction):
    await forage_logic(interaction, callback=None)

async def profile_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("You do not have an account.\nTry running **/create_account** first.",ephemeral=True,delete_after=15)
        return
    _, _, xp_to_next, _ = await check_level_up(
        result['game_level'], result['xp'])
    
    profile_embed = discord.Embed(
        title="👤 Profile Stats",
        description=f"""
**Purse**: ${result['balance']:,}\n**Bank**: Coming Soon!
Current level: **{result['game_level']}** | Next Level: **{result['xp']}/{xp_to_next}**
""",
        color=0x0000CC
    )
    profile_embed.set_footer(text='Made by ocrxn')
    profile_embed.set_author(name=interaction.user)

    view = create_view([
    {"label": "View Log Totals", "style": discord.ButtonStyle.blurple, "emoji": f"{wood['oak']}", "callback": log_totals_callback},
    {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
    {"label": "Shop", "style": discord.ButtonStyle.danger, "emoji": "🛒", "callback": shop_button_callback},
    {"label": "Vote", "style": discord.ButtonStyle.danger, "emoji": "<a:Vote:1383117707519459418>", "callback": vote_button_callback},
    {"label": "GitHub", "emoji": "<a:github:1387274840154701874>", "url": "https://github.com/ocrxn/Foraging-Bot"},
])
    await interaction.response.send_message(embed=profile_embed, view=view, ephemeral=True,delete_after=120)

@bot.tree.command(name='profile', description='Display Profile Stats')
async def profile_command(interaction: discord.Interaction):
    await profile_logic(interaction)

async def log_totals_logic(interaction: discord.Interaction):
    await interaction.response.defer()
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("You do not have an account.\nTry running **/create_account** first.",ephemeral=True,delete_after=15)
        return
    def fmt_block(icon, name, current, total):
        return(f"{icon} **{name} Logs**: {str(current).rjust(5)}\n"
        f"🏆 **Total {name} Collected**: {str(total).rjust(5)}"
)
    lines = [
        f"**Logs in Inventory**: {str(result["logs"]).rjust(5)}\n**🏆All Time Logs Collected**: {str(result["total_logs"]).rjust(5)}",
        fmt_block("<:Acacia_Log:1306063726532624475>", "Acacia", result["acacia"], result["total_acacia"]),
        fmt_block("<:Birch_Log:1306063717582110811>", "Birch", result["birch"], result["total_birch"]),
        fmt_block("<:Dark_Oak_Log:1306063707805061161>", "Dark Oak", result["dark_oak"], result["total_dark_oak"]),
        fmt_block("<:Jungle_Log:1306063697273425950>", "Jungle", result["jungle"], result["total_jungle"]),
        fmt_block("<:Oak_Log:1306063668966064188>", "Oak", result["oak"], result["total_oak"]),
        fmt_block("<:Spruce_Log:1306063686070304869>", "Spruce", result["spruce"], result["total_spruce"]),
]
    totals_embed = discord.Embed(
        title="👤 Logs Collected Stats",
        description="\n\n".join(lines),
        color=0x0000CC
    )
    totals_embed.set_thumbnail(url='https://wallpapers.com/images/hd/aesthetic-pixel-art-hd-tw4g4yk63da4tj6x.jpg')
    totals_embed.set_footer(text='Made by ocrxn')
    totals_embed.set_author(name=interaction.user)

    view = create_view([
    {"label": "Back to Profile", "style": discord.ButtonStyle.secondary, "emoji": "🔙", "callback": profile_button_callback},
])
    await interaction.edit_original_response(embed=totals_embed, view=view)

async def shop_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("You do not have an account.\nTry running **/create_account** first.",ephemeral=True,delete_after=15)
    else:
        shop_embed = discord.Embed(
            title="Shop Menu",
            description=f"""Items to purchase.
1. Axe Upgrades (Current: {axes[result['Axe_Type']]}**{result["Axe_Type"]}**)
2. Armor Upgrades (Current: {armor[result['Armor_Type']]}**{result["Armor_Type"]}**)
3. Pet Upgrades (Current: {'None' if result['Pet_Type'] == 'None' else f'{pets[result['Pet_Type']]} **{result['Pet_Type']}**'})
4. Minion Upgrades (Current: **NONE**)
P.S. Voting gives you a temporary 2x wood multiplier
            """,
        )
        shop_embed.set_footer(text='Made by ocrxn')
        shop_embed.set_author(name=interaction.user)
        row1 = [
            {"label": "Axes", "style": discord.ButtonStyle.blurple, "emoji": f"{axes['diamond_axe']}", "callback": shop_axe_callback},
            {"label": "Armor", "style": discord.ButtonStyle.blurple, "emoji": f"{armor['diamond_armor']}", "callback": shop_armor_callback},
            {"label": "Pets", "style": discord.ButtonStyle.blurple, "emoji": pets.get(result.get("Pet_Type"), "📄"), "callback": shop_pet_callback},
            {"label": "Minions", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": shop_minion_callback}
        ]
        row2=[
            {"label": "Chop Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
            {"label": "Sell Items", "style": discord.ButtonStyle.danger, "emoji": "📄", "callback": sell_inventory_callback},
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
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
    else:
        shop_embed = discord.Embed(
            title="Inventory Menu",
            description=f"""
1. Upgrade Inventory
P.S. Voting gives you a temporary 2x wood multiplier
            """,
        )

        view = create_view([
    {"label": "Upgrade Inventory", "style": discord.ButtonStyle.gray, "emoji": "⬆️", "callback": shop_button_callback},        
    {"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
        await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def sell_inventory_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
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
        )
    view = create_view([
    {"label": "Sell ALL", "style": discord.ButtonStyle.gray, "emoji": f"{wood['logs']}", "sell_type": 'logs', 'disabled': result['logs']<1},
    {"label": "Sell Acacia", "style": discord.ButtonStyle.gray, "emoji": f"{wood['acacia']}", "sell_type": 'acacia', 'disabled': result['acacia']<1},
    {"label": "Sell Birch", "style": discord.ButtonStyle.gray, "emoji": f"{wood['birch']}", "sell_type": 'birch', 'disabled': result['birch']<1},
    {"label": "Sell Dark Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['dark_oak']}", "sell_type": 'dark_oak', 'disabled': result['dark_oak']<1},
    {"label": "Sell Jungle", "style": discord.ButtonStyle.gray, "emoji": f"{wood['jungle']}", "sell_type": 'jungle', 'disabled': result['jungle']<1},
    {"label": "Sell Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['oak']}", "sell_type": 'oak', 'disabled': result['oak']<1},
    {"label": "Sell Spruce", "style": discord.ButtonStyle.gray, "emoji": f"{wood['spruce']}", "sell_type": 'spruce', 'disabled': result['spruce']<1},        
    {"label": "Back to [Shop - Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=sell_embed,view=view,ephemeral=True,delete_after=60)

@bot.tree.command(name='sell', description='Sell Wood')
async def sell_command(interaction: discord.Interaction):
    await sell_inventory_logic(interaction)

async def shop_axe_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return
    item_label = items.ITEMS['Axe_Type']
    # Calculate the maximum width needed for the name column
    max_name_width = max(len(f"{axes[axe]} {axe.replace('_', ' ').title()}") for axe in axes.keys())

    shop_embed = discord.Embed(
        title="Purchase Axes",
        description=f"""Current Axe: **{result["Axe_Type"].replace('_',' ').title()}**
1. {axes['wooden_axe']} **Wooden Axe**{' ' * (max_name_width - len(f'{axes['wooden_axe']} Wooden Axe'))}   • Price: ${item_label['wooden_axe']['cost']:,} {f'⚡Power: {item_label['wooden_axe']['power']/10}':>30}
2. {axes['stone_axe']} **Stone Axe**{' ' * (max_name_width - len(f'{axes['stone_axe']} Stone Axe'))}   • Price: ${item_label['stone_axe']['cost']:,} {f'⚡Power: {item_label['stone_axe']['power']/10}':>30}
3. {axes['iron_axe']} **Iron Axe**{' ' * (max_name_width - len(f'{axes['iron_axe']} Iron Axe'))}   • Price: ${item_label['iron_axe']['cost']:,} {f'⚡Power: {item_label['iron_axe']['power']/10}':>28}
4. {axes['gold_axe']} **Gold Axe**{' ' * (max_name_width - len(f'{axes['gold_axe']} Gold Axe'))}   • Price: ${item_label['gold_axe']['cost']:,} {f'⚡Power: {item_label['gold_axe']['power']/10}':>26}
5. {axes['diamond_axe']} **Diamond Axe**{' ' * (max_name_width - len(f'{axes['diamond_axe']} Diamond Axe'))}   • Price: ${item_label['diamond_axe']['cost']:,} {f'⚡Power: {item_label['diamond_axe']['power']/10}':>18}
6. {axes['netherite_axe']} **Netherite Axe**{' ' * (max_name_width - len(f'{axes['netherite_axe']} Netherite Axe'))}   • Price: ${item_label['netherite_axe']['cost']:,} {f'⚡Power: {item_label['netherite_axe']['power']/10}':>18}
7. {axes['mythic_axe']} **Mythic Axe**{' ' * (max_name_width - len(f'{axes['mythic_axe']} Mythic Axe'))}   • Price: ${item_label['mythic_axe']['cost']:,} {f'⚡Power: {item_label['mythic_axe']['power']/10}':>17}
P.S. Voting gives you a temporary 2x wood multiplier
        """,
    )

    view = create_view([                             
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['wooden_axe']}", "item_type": "Axe_Type", "item_name": "wooden_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['stone_axe']}", "item_type": "Axe_Type", "item_name": "stone_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['iron_axe']}", "item_type": "Axe_Type", "item_name": "iron_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['gold_axe']}", "item_type": "Axe_Type", "item_name": "gold_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['diamond_axe']}", "item_type": "Axe_Type", "item_name": "diamond_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['netherite_axe']}", "item_type": "Axe_Type", "item_name": "netherite_axe"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{axes['mythic_axe']}", "item_type": "Axe_Type", "item_name": "mythic_axe"},
{"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def shop_armor_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return
    price_label = items.ITEMS['Armor_Type']
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
    )

    view = create_view([
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['leather_armor']}", "item_type": "Armor_Type", "item_name": "leather_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['chainmail_armor']}", "item_type": "Armor_Type", "item_name": "chainmail_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['iron_armor']}", "item_type": "Armor_Type", "item_name": "iron_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['gold_armor']}", "item_type": "Armor_Type", "item_name": "gold_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['diamond_armor']}", "item_type": "Armor_Type", "item_name": "diamond_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['netherite_armor']}", "item_type": "Armor_Type", "item_name": "netherite_armor"},
{"label": "", "style": discord.ButtonStyle.green, "emoji": f"{armor['mythic_armor']}", "item_type": "Armor_Type", "item_name": "mythic_armor"},
{"label": "Back to Main Shop", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)


async def shop_pet_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.", ephemeral=True, delete_after=15)
        return
    
    tier_order = ["COMMON", "RARE", "EPIC", "LEGENDARY", "MYTHIC", "DIVINE"]
    items_dict = items.ITEMS["Pet_Type"]
    current_page = 0

    def make_embed(page):
        tier = tier_order[page]
        desc = f"**{tier} Pets**\n"
        pets_on_page = []
        for pet_name, pet_data in items_dict.items():
            if pet_data["tier"] == tier:
                desc += f"- {pet_name} (Cost: ${pet_data['cost']:,})\n"
                pets_on_page.append(pet_name)
        shop_embed = discord.Embed(title="Purchase Pets", description=desc)
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
                "item_type": 'Pet_Type',
                "item_name": pet_name
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


async def pet_menu(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
        
    else:
        result = await retrieve(interaction)
        if isinstance(result.get('pets_inv'), str):
            result['pets_inv'] = json.loads(result['pets_inv'])

    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return

    pet_lines = "\n".join(
        f"{pets.get(pet, '')} {pet}: Level {data['pet_level']} ({data['pet_xp']} XP)"
        for pet, data in result['pets_inv'].items())
    
    
    shop_embed = discord.Embed(
        title="Your Owned Pets",
        description="**No owned pets.** Purchase a pet add it to your collection." if result['Pet_Type'] == 'None' else f"""
    **Current Pet: {pets[result['Pet_Type']]} [Lvl {result['pets_inv'][result['Pet_Type']]['pet_level']}] {result['Pet_Type']}**
    **{pet_lines}**
    P.S. Voting gives you a temporary 2x wood multiplier
        """,
    )


    view = create_view([
{"label": "Back to [Shop: Pets]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_pet_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

async def shop_minion_logic(interaction: discord.Interaction):
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
    
    if not result:
        await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return
    
    shop_embed = discord.Embed(
        title="Minions Menu",
        description=f"""Items to purchase.

P.S. Voting gives you a temporary 2x wood multiplier
        """,
    )

    view = create_view([
{"label": "Purchase Tree", "style": discord.ButtonStyle.green, "emoji": "🌳", "callback": forage_button_callback},
{"label": "Profile Stats", "style": discord.ButtonStyle.blurple, "emoji": "📄", "callback": profile_button_callback},
{"label": "Back to [Shop: Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])
    await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)

#=======================================================
#==================== 🔺 END SLASH COMMANDS 🔺 ====================
#=======================================================
async def is_downgrade(interaction, result, item_type, item_name):
    tier_list = list(items.ITEMS[item_type].keys())    
    player_current_item = result[item_type]

    if player_current_item == "None":
        return
    player_index = tier_list.index(player_current_item)
    item_index = tier_list.index(item_name)
    
    return player_index > item_index

async def purchase_item(interaction: discord.Interaction, item_type:str, item_name: str):
    await interaction.response.defer()
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
        if isinstance(result.get('pets_inv'), str):
            result['pets_inv'] = json.loads(result['pets_inv'])
        await create_temp_user(interaction)
        

    if not result:
        await interaction.followup.send("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return
    
    item_info = items.ITEMS.get(item_type, {}).get(item_name)

    if not item_info:
        await interaction.followup.send("This item doesn't exist.", ephemeral=True)
        return

    cost = item_info["cost"]
    balance = result["balance"]
    if item_type == "Pet_Type":
        if item_name in buffer_db[interaction.user.id]['pets_inv']:
            await interaction.edit_original_response(content=f"You already own this pet.")
            return
    else:
        required_current = item_info["required_current"]
        if item_type == "Axe_Type":
            current_item = result["Axe_Type"]
        elif item_type == "Armor_Type":
            current_item = result["Armor_Type"]
        else:
            await interaction.edit_original_response("Unknown item type.", ephemeral=True,delete_after=15)

        if await is_downgrade(interaction, result, item_type, item_name):
            await interaction.edit_original_response(content="You already own a higher-tier version of this item!")
            return

        if current_item == item_name:
            await interaction.edit_original_response(content=f"You already own **{item_name}**.")
            return
        
        if current_item != required_current:
            await interaction.edit_original_response(content=f"You must own **{required_current}** to purchase **{item_name}**")
            return
    
    if balance < cost:
        await interaction.edit_original_response(content=f"You need {cost} coins to purchase **{item_name}**. You only have {balance}")
        return
    
    await interaction.edit_original_response(content=f"You purchased {item_name} for ${cost:,.2f}.")
    if item_type == "Pet_Type":
        buffer_db[interaction.user.id]['pets_inv'][item_name] = {'pet_level': 0, 'pet_xp': 0}
    buffer_db[interaction.user.id][item_type] = item_name
    buffer_db[interaction.user.id]["balance"] -= cost
    dirty_users.add(interaction.user.id)

async def sell_inventory(interaction: discord.Interaction, sell_type:str):
    await interaction.response.defer()
    if interaction.user.id in buffer_db:
        result = buffer_db[interaction.user.id]
    else:
        result = await retrieve(interaction)
        await create_temp_user(interaction)

    if not result:
        await interaction.followup.send("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
        return
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
    sell_embed = discord.Embed(
            title="Sell Wood Menu",
            description=f"""```💵 You sold {result[sell_type]} {sell_type if sell_type != 'logs' else ''} logs for ${result[sell_type]*2:,}.```
{desc}
P.S. Voting gives you a temporary 2x wood multiplier
            """,
        )
    total = result[sell_type]*2
    if sell_type == "logs":
        buffer_db[interaction.user.id]['logs'] = 0
        for log in wood_id:
            buffer_db[interaction.user.id][log] = 0
    else:
        buffer_db[interaction.user.id]['logs'] = 0
        buffer_db[interaction.user.id][sell_type] = 0
    buffer_db[interaction.user.id]['balance'] += total
    dirty_users.add(interaction.user.id)

    view = create_view([
    {"label": "Sell ALL", "style": discord.ButtonStyle.gray, "emoji": f"{wood['logs']}", "sell_type": 'logs', 'disabled': result['logs']<1},
    {"label": "Sell Acacia", "style": discord.ButtonStyle.gray, "emoji": f"{wood['acacia']}", "sell_type": 'acacia', 'disabled': result['acacia']<1},
    {"label": "Sell Birch", "style": discord.ButtonStyle.gray, "emoji": f"{wood['birch']}", "sell_type": 'birch', 'disabled': result['birch']<1},
    {"label": "Sell Dark Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['dark_oak']}", "sell_type": 'dark_oak', 'disabled': result['dark_oak']<1},
    {"label": "Sell Jungle", "style": discord.ButtonStyle.gray, "emoji": f"{wood['jungle']}", "sell_type": 'jungle', 'disabled': result['jungle']<1},
    {"label": "Sell Oak", "style": discord.ButtonStyle.gray, "emoji": f"{wood['oak']}", "sell_type": 'oak', 'disabled': result['oak']<1},
    {"label": "Sell Spruce", "style": discord.ButtonStyle.gray, "emoji": f"{wood['spruce']}", "sell_type": 'spruce', 'disabled': result['spruce']<1},        
    {"label": "Back to [Shop - Main]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_button_callback}
])

    await interaction.edit_original_response(embed=sell_embed,view=view)
    

def create_view(button_configs):
    view = View(timeout=None)

    if not button_configs:
        return view

    is_multi_row = isinstance(button_configs[0], list)

    if not is_multi_row:
        # Flat list of buttons
        if len(button_configs) <= 5:
            button_rows = [button_configs]  # one row only
        else:
            # Chunk into rows of max 5 buttons
            button_rows = [button_configs[i:i+5] for i in range(0, len(button_configs), 5)]
    else:
        button_rows = button_configs

    # Now iterate through button_rows and add buttons with row indices
    for row_index, row in enumerate(button_rows):
        for config in row:
            # URL buttons
            if config.get('url'):
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.link),
                    emoji=config.get('emoji'),
                    url=config['url'],
                    disabled=config.get('disabled', False),
                    row=row_index
                )
            # Purchase buttons
            elif config.get('item_type') and config.get('item_name'):
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.secondary),
                    emoji=config.get('emoji'),
                    custom_id=config['item_name'],
                    disabled=config.get('disabled', False),
                    row=row_index
                )
                async def callback(interaction, item_type=config['item_type'], item_name=config['item_name']):
                    await purchase_item(interaction, item_type, item_name)
                button.callback = callback
            # Sell buttons
            elif config.get('sell_type'):
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.secondary),
                    emoji=config.get('emoji'),
                    disabled=config.get('disabled', False),
                    row=row_index
                )

                def make_sell_callback(sell_type):
                    async def callback(interaction):
                        await sell_inventory(interaction, sell_type)
                    return callback

                button.callback = make_sell_callback(config.get('sell_type'))
            else:
                # Standard buttons
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.secondary),
                    emoji=config.get('emoji'),
                    disabled=config.get('disabled', False),
                    row=row_index
                )
                button.callback = config['callback']

            view.add_item(button)

    return view



# Button Callbacks
async def vote_button_callback(interaction: discord.Interaction):
    await vote_logic(interaction)

async def forage_button_callback(interaction: discord.Interaction):
    await forage_logic(interaction, callback='callback')

async def profile_button_callback(interaction: discord.Interaction):
    await profile_logic(interaction)
    
async def log_totals_callback(interaction: discord.Interaction):
    await log_totals_logic(interaction)

async def shop_button_callback(interaction: discord.Interaction):
    await shop_logic(interaction)

async def shop_inventory_callback(interaction: discord.Interaction):
    await shop_inventory_logic(interaction)

async def sell_inventory_callback(interaction: discord.Interaction):
    await sell_inventory_logic(interaction)

async def shop_axe_callback(interaction: discord.Interaction):
    await shop_axe_logic(interaction)

async def shop_armor_callback(interaction: discord.Interaction):
    await shop_armor_logic(interaction)

async def shop_pet_callback(interaction: discord.Interaction):
    await shop_pet_logic(interaction)

async def pet_menu_callback(interaction: discord.Interaction):
    await pet_menu(interaction)

async def shop_minion_callback(interaction: discord.Interaction):
    await shop_minion_logic(interaction)


#Run the Bot
@bot.event
async def on_ready():
    try:
        #Initiate update db loop
        global update_task
        print(f'{bot.user} has connected to Discord!')
        update_task = asyncio.create_task(update_db_loop())
    except Exception as e:
        print(f"Bot ran into an unexpected error during sync: {e}")

bot.run(TOKEN)