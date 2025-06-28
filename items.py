ITEMS = {
    'Axe_Type': {
        'wooden_axe': {
            'required_current': 'None',
            'next_tier': 'stone_axe',
            'cost': 100,
            'power': 11
        },
        'stone_axe': {
            'required_current': 'wooden_axe',
            'next_tier': 'iron_axe',
            'cost': 1000,
            'power': 12.5
        },
        'iron_axe': {
            'required_current': 'stone_axe',
            'next_tier': 'gold_axe',
            'cost': 10000,
            'power': 15
        },
        'gold_axe': {
            'required_current': 'iron_axe',
            'next_tier': 'diamond_axe',
            'cost': 100000,
            'power': 20
        },
        'diamond_axe': {
            'required_current': 'gold_axe',
            'next_tier': 'netherite_axe',
            'cost': 1000000,
            'power': 35
        },
        'netherite_axe': {
            'required_current': 'diamond_axe',
            'next_tier': 'mythic_axe',
            'cost': 10000000,
            'power': 50
        },
        'mythic_axe': {
            'required_current': 'netherite_axe',
            'next_tier': 'MAX TIER',
            'cost': 100000000,
            'power': 100
        }
    },


    'Armor_Type': {
        'leather_armor': {
            'required_current': 'None',
            'next_tier': 'chainmail_armor',
            'cost': 100
        },
        'chainmail_armor': {
            'required_current': 'leather_armor',
            'next_tier': 'iron_armor',
            'cost': 1000
        },
        'iron_armor': {
            'required_current': 'chainmail_armor',
            'next_tier': 'gold_armor',
            'cost': 10000
        },
        'gold_armor': {
            'required_current': 'iron_armor',
            'next_tier': 'diamond_armor',
            'cost': 100000
        },
        'diamond_armor': {
            'required_current': 'gold_armor',
            'next_tier': 'netherite_armor',
            'cost': 1000000
        },
        'netherite_armor': {
            'required_current': 'diamond_armor',
            'next_tier': 'mythic_armor',
            'cost': 10000000
        },
        'mythic_armor': {
            'required_current': 'netherite_armor',
            'next_tier': 'MAX TIER',
            'cost': 100000000
        }
    },

################-----PETS-----###############
    'Pet_Type': {
        'Squirrel': {
            'tier': 'COMMON',
            'cost': 100
        },
        'Raccoon': {
            'tier': 'COMMON',
            'cost': 100
        },
        'Mushroom Spirit': {
            'tier': 'COMMON',
            'cost': 100
        },
        'Beaver': {
            'tier': 'RARE',
            'cost': 1000
        },
        'Woodpecker': {
            'tier': 'RARE',
            'cost': 1000
        },
        'Timber Wolf': {
            'tier': 'RARE',
            'cost': 1000
        },
        'Fairy': {
            'tier': 'EPIC',
            'cost': 10000
        },
        'Golden Finch': {
            'tier': 'EPIC',
            'cost': 10000
        },
        'Leaf Golem': {
            'tier': 'EPIC',
            'cost': 10000
        },
        'Dryad Queen': {
            'tier': 'LEGENDARY',
            'cost': 100000
        },
        'Ancient Entling': {
            'tier': 'LEGENDARY',
            'cost': 100000
        },
        "Lumberjack's Ghost": {
            'tier': 'LEGENDARY',
            'cost': 100000
        },
        "Ember": {
            'tier': 'MYTHIC',
            'cost': 1000000
        },
        "Woodland Nymph": {
            'tier': 'MYTHIC',
            'cost': 1000000
        },
        "Hypixel's Echo": {
            'tier': 'DIVINE',
            'cost': 10000000
        },
        "Herobrine's Omen": {
            'tier': 'DIVINE',
            'cost': 10000000
        },
    }
}


