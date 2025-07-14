user_id = interaction.user.id
#     result = buffer_db.get(user_id) or await retrieve(interaction)

#     if isinstance(result.get('minions'), str):
#         result['minions'] = json.loads(result['minions'])

#     minion = result["minions"].get(slot_name, "None")

#     if minion == "None":
#         embed = discord.Embed(
#             title=f"Empty Slot: {slot_name}",
#             description="No minion is placed here.\nWould you like to purchase one?",
#             color=discord.Color.orange()
#         )
#         view = create_view([[
#             {"label": "Purchase Minion", "style": discord.ButtonStyle.green, "emoji": "🛒", "callback": make_purchase_callback(slot_name)},
#             {"label": "Back", "style": discord.ButtonStyle.gray, "emoji": "↩️", "callback": return_to_menu}
#         ]])
#         await interaction.response.edit_message(embed=embed, view=view)
#     else:
#         minion_info = get_minion_info(user_id, slot_name)  # custom function you'll define
#         embed = discord.Embed(
#             title=f"{minion} — Slot: {slot_name}",
#             description=f"""**Level:** {minion_info['level']}
# **Stored Logs:** {minion_info['storage']}
# **XP:** {minion_info['xp']} / {minion_info['xp_needed']}
# """,
#             color=discord.Color.green()
#         )
#         view = create_view([[
#             {"label": "Back", "style": discord.ButtonStyle.gray, "emoji": "↩️", "callback": return_to_menu}
#         ]])
#         await interaction.response.edit_message(embed=embed, view=view)

#     # return view_callback



#     if interaction.user.id in buffer_db:
#         result = buffer_db[interaction.user.id]
        
#     else:
#         result = await retrieve(interaction)
#         if isinstance(result.get('pets_inv'), str):
#             result['pets_inv'] = json.loads(result['pets_inv'])

#     if not result:
#         await interaction.response.send_message("Something went wrong.\nTry running **/create_account**.",ephemeral=True,delete_after=15)
#         return

#     pet_lines = "\n".join(
#         f"{pets.get(pet, '')} {pet}: Level {data['pet_level']} ({data['pet_xp']} XP)"
#         for pet, data in result['pets_inv'].items())
      
#     shop_embed = discord.Embed(
#         title="Your Owned Pets",
#         description="**No owned pets.** Purchase a pet add it to your collection." if result['Pet_Type'] == 'None' else f"""
#     **Current Pet: {pets[result['Pet_Type']]} [Lvl {result['pets_inv'][result['Pet_Type']]['pet_level']}] {result['Pet_Type']}**
#     **{pet_lines}**
#     P.S. Voting gives you a temporary 2x wood multiplier
#         """,
#         timestamp=datetime.now()
#     )


#     view = create_view([
# {"label": "Back to [Shop: Pets]", "style": discord.ButtonStyle.gray, "emoji": "🔙", "callback": shop_pet_callback}
# ])
#     await interaction.response.send_message(embed=shop_embed, view=view, ephemeral=True,delete_after=60)