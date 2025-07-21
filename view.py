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
            button_kwargs = {
                'label': config.get('label'),
                'style': config.get('style', discord.ButtonStyle.secondary),
                'emoji': config.get('emoji'),
                'disabled': config.get('disabled', False),
                'row': row_index,
            }
            if config.get('url'):
                button_kwargs["style"] = discord.ButtonStyle.link
                button_kwargs["url"] = config.get('url')
                button = Button(**button_kwargs)
                
            elif config.get('kwargs'):
                button = Button(**button_kwargs)
                kwargs = config.get('kwargs', {})

                async def callback(interaction, kwargs=kwargs):
                    from logic import purchase_item, sell_inventory

                    if 'purchase' in kwargs or kwargs.get('item_type'):
                        from logic import purchase_item
                        await purchase_item(interaction, **kwargs)
                    elif 'sell' in kwargs or 'sell_type' in kwargs:
                        from logic import sell_inventory
                        await sell_inventory(interaction, **kwargs)
                    else:
                        await interaction.response.send_message("Action not recognized.", ephemeral=True)

                button.callback = callback

            else:
                button = Button(**button_kwargs)

                def create_button_callback(callback, args=None,kwargs=None):
                    args = args or []
                    kwargs = kwargs or {}

                    async def cb(interaction):
                        await callback(interaction, *args, **kwargs)

                    return cb
                
                button.callback = create_button_callback(config['callback'], config.get('args', []), config.get('kwargs', {}))           

            view.add_item(button)

    return view