import os
from dotenv import load_dotenv
import psycopg2
from config import *

load_dotenv()
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()


# cursor.execute(
#     """INSERT INTO stats (
#   dc_id, dc_username, game_level, xp, balance, Axe_Type, Armor_Type, Pet_Type, pets_inv, minions,
#   logs, acacia, birch, dark_oak, jungle, oak, spruce, total_logs, total_acacia, total_birch,
#   total_dark_oak, total_jungle, total_oak, total_spruce
# ) VALUES (
#   942468987114123286, 'keypressed', 14, 1811, 99999888863073, 'mythic_axe', 'None', 'None', '{}', '{}',
#   935, 170, 270, 80, 85, 160, 170, 1407, 223, 347, 137, 211, 260, 229
# );"""
# )
# conn.commit()

cursor.execute("SELECT * FROM stats;")
rows = cursor.fetchall()
for row in rows:
    print(row)

cursor.close()
conn.close()

