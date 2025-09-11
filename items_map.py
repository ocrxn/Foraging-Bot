ITEMS = {
    'axe_type': {
        'wooden_axe': {
            'required_current': 'None',
            'next_tier': 'stone_axe',
            'cost': 100,
            'power': 11,
            'cooldown': 5,
        },
        'stone_axe': {
            'required_current': 'wooden_axe',
            'next_tier': 'iron_axe',
            'cost': 1000,
            'power': 12.5,
            'cooldown': 4.5,
        },
        'iron_axe': {
            'required_current': 'stone_axe',
            'next_tier': 'gold_axe',
            'cost': 10000,
            'power': 15,
            'cooldown': 4,
        },
        'gold_axe': {
            'required_current': 'iron_axe',
            'next_tier': 'diamond_axe',
            'cost': 100000,
            'power': 20,
            'cooldown': 3.5,
        },
        'diamond_axe': {
            'required_current': 'gold_axe',
            'next_tier': 'netherite_axe',
            'cost': 1000000,
            'power': 35,
            'cooldown': 3,
        },
        'netherite_axe': {
            'required_current': 'diamond_axe',
            'next_tier': 'mythic_axe',
            'cost': 10000000,
            'power': 50,
            'cooldown': 2.5,
        },
        'mythic_axe': {
            'required_current': 'netherite_axe',
            'next_tier': 'MAX TIER',
            'cost': 100000000,
            'power': 100,
            'cooldown': 2,
        }
    },


    'armor_type': {
        'leather_armor': {
            'required_current': 'None',
            'next_tier': 'chainmail_armor',
            'cost': 100,
            'coin_boost': 1.1,
        },
        'chainmail_armor': {
            'required_current': 'leather_armor',
            'next_tier': 'iron_armor',
            'cost': 1000,
            'coin_boost': 1.25,
        },
        'iron_armor': {
            'required_current': 'chainmail_armor',
            'next_tier': 'gold_armor',
            'cost': 10000,
            'coin_boost': 1.5,
        },
        'gold_armor': {
            'required_current': 'iron_armor',
            'next_tier': 'diamond_armor',
            'cost': 100000,
            'coin_boost': 2,
        },
        'diamond_armor': {
            'required_current': 'gold_armor',
            'next_tier': 'netherite_armor',
            'cost': 1000000,
            'coin_boost': 2.75,
        },
        'netherite_armor': {
            'required_current': 'diamond_armor',
            'next_tier': 'mythic_armor',
            'cost': 10000000,
            'coin_boost': 3.5,
        },
        'mythic_armor': {
            'required_current': 'netherite_armor',
            'next_tier': 'MAX TIER',
            'cost': 100000000,
            'coin_boost': 5,
        }
    },

################-----PETS-----###############
    'pet_type': {
        'Squirrel': {
            'tier': 'COMMON',
            'cost': 100,
            'xp_boost': 1.005
        },
        'Raccoon': {
            'tier': 'COMMON',
            'cost': 100,
            'xp_boost': 1.005
        },
        'Mushroom Spirit': {
            'tier': 'COMMON',
            'cost': 100,
            'xp_boost': 1.005
        },
        'Beaver': {
            'tier': 'RARE',
            'cost': 1000,
            'xp_boost': 1.01
        },
        'Woodpecker': {
            'tier': 'RARE',
            'cost': 1000,
            'xp_boost': 1.01
        },
        'Timber Wolf': {
            'tier': 'RARE',
            'cost': 1000,
            'xp_boost': 1.01
        },
        'Fairy': {
            'tier': 'EPIC',
            'cost': 10000,
            'xp_boost': 1.015
        },
        'Golden Finch': {
            'tier': 'EPIC',
            'cost': 10000,
            'xp_boost': 1.015
        },
        'Leaf Golem': {
            'tier': 'EPIC',
            'cost': 10000,
            'xp_boost': 1.015
        },
        'Dryad Queen': {
            'tier': 'LEGENDARY',
            'cost': 100000,
            'xp_boost': 1.02
        },
        'Ancient Entling': {
            'tier': 'LEGENDARY',
            'cost': 100000,
            'xp_boost': 1.02
        },
        "Lumberjack's Ghost": {
            'tier': 'LEGENDARY',
            'cost': 100000,
            'xp_boost': 1.02
        },
        "Ember": {
            'tier': 'MYTHIC',
            'cost': 1000000,
            'xp_boost': 1.025
        },
        "Woodland Nymph": {
            'tier': 'MYTHIC',
            'cost': 1000000,
            'xp_boost': 1.025
        },
        "Hypixel's Echo": {
            'tier': 'DIVINE',
            'cost': 10000000,
            'xp_boost': 1.05
        },
        "Herobrine's Omen": {
            'tier': 'DIVINE',
            'cost': 10000000,
            'xp_boost': 1.05
        },
    },
    'Minion_Type': {
        'slot_costs': [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300, 2400, 2500],
        'Acacia I': {
            'cost': 1000,
            'speed': 1,
            'storage': 64
        },
        'Birch I': {
            'cost': 2000,
            'speed': 1,
            'storage': 64
        },
        'Dark Oak I': {
            'cost': 2000,
            'speed': 1,
            'storage': 64
        },
        'Jungle I': {
            'cost': 2000,
            'speed': 1,
            'storage': 64
        },
        'Oak I': {
            'cost': 2000,
            'speed': 1,
            'storage': 64
        },
        'Spruce I': {
            'cost': 2000,
            'speed': 1,
            'storage': 64
        }
    }
}

