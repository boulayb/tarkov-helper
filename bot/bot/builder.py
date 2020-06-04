# -*- coding: utf-8 -*-

from tips import TIPS_LIST
from settings import *

import tools

import random
import discord


# format an embed to alert the user that there is too many results for his search
def build_too_many_embed(total, name):

    embed = discord.Embed(
        title="I found " + str(total) + " results for '" + name + "'. Here is only 3, be more precise.",
        description='',
        colour=discord.Colour.blue()
    )

    return embed


# format an embed to display a random tip from the tips list
def build_tips_embed():

    embed = discord.Embed(
        title=random.choice(TIPS_LIST),
        description='',
        colour=discord.Colour.blue()
    )

    return embed


# format an embed to display the default embed with the list of command available
def build_help_embed():

    embed = discord.Embed(
        title='USEC Command',
        description='Here to assist you in your raids, even you BEAR scums',
        colour=discord.Colour.blue()
    )

    embed.set_thumbnail(url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/7/7d/Skill_mental_charisma.png?version=9d52bcf9bcd3a30e562b3327513a8709')
    embed.set_footer(text='By Redleouf - contact: redleouf@gmail.com')

    embed.add_field(name='!command item [YOUR ITEM]', value='Display informations about the searched item.\nOpen original trade/craft image in webbrowser for full list.', inline=False)
    embed.add_field(name='!command tips', value='Display a usefull tip to help you git gud.', inline=False)

    embed.add_field(name='Data fetched from:', value='[EFT Wiki](https://escapefromtarkov.gamepedia.com) and [Loot Goblin](https://eft-loot.com/)', inline=False)

    embed.add_field(name='Donation:', value='If you like this project, feel free to donate by clicking [here](https://paypal.me/boulayb).\nIt helps me pay for the server!', inline=False)
    
    return embed


# format an embed to display item infos
def build_item_embed(item):

    if item is None:
        embed = discord.Embed(
            title='Sorry chief, nothing found for that research.',
            description='',
            colour=discord.Colour.blue()
        )

    else:
        # append type to title if it exist
        if item['type']:
            title = '**' + item['name'] + '** - ```' + item['type'] + '```'
        else:
            title = '**' + item['name'] + '**'

        embed = discord.Embed(
            title=title,
            description=' '.join(item['description']),
            url=item['url'],
            colour=discord.Colour.blue()
        )

        embed.set_thumbnail(url=item['icon'])
        if 'price_date' in item:
            embed.set_footer(text='Click title for more infos - Last price update: ' + tools.days_since(tools.convert_date(item['price_date'])))
        else:
            embed.set_footer(text='Click title for more infos')

        if len(item['notes']) > 0:
            notes_str = tools.build_string(item['notes'], item['url'] + "#Notes")
            embed.add_field(name='Notes', value=notes_str, inline=False)

        embed.add_field(name='Size', value=item['size'], inline=True)
        embed.add_field(name='Weight', value=item['weight'], inline=True)
        embed.add_field(name='Exp on loot', value=item['exp'] + '\n', inline=True) # "\u200b" to add a blank line

        if 'price' in item and 'price_slot' in item:
            embed.add_field(name='Avg. price', value=str(item['price']) + ' ₽', inline=True)
            embed.add_field(name='Avg. price/slot', value=str(item['price_slot']) + ' ₽', inline=True)

        if len(item['quests']) > 0:
            quests_str = tools.build_string(item['quests'], item['url'] + "#Quests")
            embed.add_field(name='Quests', value=quests_str, inline=False)

        if len(item['hideouts']) > 0:
            hideouts_str = tools.build_string(item['hideouts'], item['url'] + "#Hideout")
            embed.add_field(name='Hideouts', value=hideouts_str, inline=False)

        if len(item['locations']) > 0:
            locations_str = tools.build_string(item['locations'], item['url'] + "#Location")
            embed.add_field(name='Locations', value=locations_str, inline=False)

        if item['trades']:
            embed.set_image(url=item['trades'])

    return embed
