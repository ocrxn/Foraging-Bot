
import ast
import asyncio
import json
import math
import os
import random
import signal
import sys
import threading
import time
from collections import defaultdict
from datetime import datetime
from functools import partial

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

from config import *
from bot_instance import bot


def connect_db():
        return mysql.connector.connect(host=HOST,user=USER,password=PASSWORD,database=DATABASE, port=PORT)

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
                "minions": json.loads(result['minions']) if isinstance(result['minions'], str) else (result['minions'] or {}),
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
                "minions": {},
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
                minions = %(minions)s,
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
                        if isinstance(user_copy.get('minions'), dict):
                            user_copy['minions'] = json.dumps(user_copy['minions'])
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
                    if isinstance(user_copy.get('minions'), dict):
                            user_copy['minions'] = json.dumps(user_copy['minions'])
                    dirty_values.append(user_copy)
                exe.executemany(buffer_query, dirty_values)
                conn.commit()
                dirty_users.clear()
                buffer_db.clear()
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