from config import *
import discord
from discord.ui import Button, View


def create_view(button_configs):
    view = View(timeout=None)

    if not button_configs:
        return view

    is_multi_row = isinstance(button_configs[0], list)

    if not is_multi_row:
        if len(button_configs) <= 5:
            button_rows = [button_configs]
        else:
            button_rows = [button_configs[i:i+5] for i in range(0, len(button_configs), 5)]
    else:
        button_rows = button_configs

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
            elif config.get('item_type'):
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.secondary),
                    emoji=config.get('emoji'),
                    custom_id = config.get('item_name') or None,
                    disabled=config.get('disabled', False),
                    row=row_index
                )
                async def callback(interaction, item_type=config['item_type'], item_name=config.get('item_name') or None):
                    from logic import purchase_item,is_downgrade
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
                        from logic import sell_inventory
                        await sell_inventory(interaction, sell_type)
                    return callback

                button.callback = make_sell_callback(config.get('sell_type'))
            else:
                def create_button_callback(callback, args):
                    async def cb(interaction):
                        await callback(interaction, *args)
                    return cb
                
                button = Button(
                    label=config['label'],
                    style=config.get('style', discord.ButtonStyle.secondary),
                    emoji=config.get('emoji'),
                    disabled=config.get('disabled', False),
                    row=row_index
                )
                args = config.get('args', [])

                button.callback = create_button_callback(config['callback'], config.get('args', []))

                

            view.add_item(button)

    return view