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

            else:
                button = Button(**button_kwargs)

                if 'callback' in config:
                    args = config.get('args', [])

                    kwargs = config.get('kwargs', {})

                    async def cb(interaction, callback=config['callback'], args=args, kwargs=kwargs):

                        await callback(interaction, *args, **kwargs)

                    button.callback = cb


                elif config.get('kwargs'):

                    # Fallback logic for shop/sell buttons with no custom callback

                    button = Button(**button_kwargs)
                    kwargs = config.get('kwargs', {})

                    async def callback(interaction, kwargs=kwargs):
                        from logic import purchase_item, sell_inventory
                        if 'purchase' in kwargs or kwargs.get('item_type'):
                            await purchase_item(interaction, **kwargs)
                        elif 'sell' in kwargs or 'sell_type' in kwargs:
                            await sell_inventory(interaction, **kwargs)
                        else:
                            await interaction.response.send_message("Action not recognized.", ephemeral=True)

                    button.callback = callback

                else:
                    async def default_cb(interaction):
                        await interaction.response.send_message("No action set for this button.", ephemeral=True)
                        for thing in config:#Debugging
                            print(f"{thing}: {config[thing]}")

                    button.callback = default_cb


            view.add_item(button)

    return view