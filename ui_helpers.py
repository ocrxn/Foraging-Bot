from config import *
import discord

async def vote_button_callback(interaction: discord.Interaction):
    from logic import vote_logic
    await vote_logic(interaction)

async def lb_button_callback(interaction: discord.Interaction, page=1):
    from logic import leaderboard_logic
    await leaderboard_logic(interaction, callback='callback', page=page)

async def forage_button_callback(interaction: discord.Interaction):
    from logic import forage_logic
    await forage_logic(interaction, callback='callback')

async def profile_button_callback(interaction: discord.Interaction):
    from logic import profile_logic
    await profile_logic(interaction, callback='callback')

async def log_totals_callback(interaction: discord.Interaction):
    from logic import log_totals_logic
    await log_totals_logic(interaction)

async def shop_button_callback(interaction: discord.Interaction):
    from logic import shop_logic
    await shop_logic(interaction)

async def shop_inventory_callback(interaction: discord.Interaction):
    from logic import shop_inventory_logic
    await shop_inventory_logic(interaction)

async def sell_inventory_callback(interaction: discord.Interaction):
    from logic import sell_inventory_logic
    await sell_inventory_logic(interaction)

async def shop_axe_callback(interaction: discord.Interaction):
    from logic import shop_axe_logic
    await shop_axe_logic(interaction)

async def shop_armor_callback(interaction: discord.Interaction):
    from logic import shop_armor_logic
    await shop_armor_logic(interaction)

async def shop_pet_callback(interaction: discord.Interaction):
    from logic import shop_pet_logic
    await shop_pet_logic(interaction)

async def pet_menu_callback(interaction: discord.Interaction):
    from logic import pet_menu_logic
    await pet_menu_logic(interaction)

async def shop_minion_callback(interaction: discord.Interaction, current_page):
    from logic import shop_minion_logic
    await shop_minion_logic(interaction, start_page=current_page['index'])

async def minion_slot_view_callback(interaction: discord.Interaction, slot_name, current_page):
    from logic import minion_slot_view_logic
    await minion_slot_view_logic(interaction, slot_name=slot_name, current_page=current_page)
