# -*- coding: utf-8 -*-

from tips import TIPS_LIST
from settings import *

import tools

import random
import discord


# format an embed to alert the user that there is too many results for his search
def build_too_many_embed(total, name):

    embed = discord.Embed(
        title="I found " + str(total) + " results for '" + name + "'. Here is only 3, be more precise or use the 'list' command.",
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


# format an embed to display an image from an url
def build_image_embed(title, image_url):

    embed = discord.Embed(
        title=title,
        description='',
        colour=discord.Colour.blue()
    )

    embed.set_image(url=image_url)

    return embed


# format an embed to display an error message
def build_error_embed(error):

    embed = discord.Embed(
        title='Oops, something went wrong with that research.',
        description='If that keeps happening, please contact the developper.',
        colour=discord.Colour.blue()
    )

    embed.add_field(name='reason:', value=str(error), inline=False)

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
    embed.add_field(name='!command search [YOUR ITEM]', value='Same as the item command but with advanced search features.\nClick [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html) to learn more.', inline=False)
    embed.add_field(name='!command list [YOUR ITEM]', value='Advanced search returning the full list of results names.\nClick [here](https://www.elastic.co/guide/en/elasticsearch/reference/current/query-dsl-query-string-query.html) to learn more.', inline=False)
    embed.add_field(name='!command medical', value='Display a medical chart to help you.', inline=False)
    embed.add_field(name='!command injector', value='Display an injector chart to help you.', inline=False)
    embed.add_field(name='!command tips', value='Display a usefull tip to help you git gud.', inline=False)

    embed.add_field(name='Data fetched from:', value='[EFT Wiki](https://escapefromtarkov.gamepedia.com) and [Tarkov-Market](https://tarkov-market.com/)', inline=False)

    embed.add_field(name='Donation:', value='If you like this project, feel free to donate by clicking [here](https://paypal.me/boulayb).\nIt helps me pay for the server!', inline=False)
    
    return embed


# format an embeds list to list items names
def build_list_embeds(items, query):

    if len(items) == 0:
        embed = discord.Embed(
            title='Sorry chief, nothing found for that research.',
            description='',
            colour=discord.Colour.blue()
        )

    else:
        list_of_names = []

        for item in items:
            line = '[**' + item['name'] + '**](' + item['url'] + ')'
            list_of_names.append(line)

        embed = discord.Embed(
            colour=discord.Colour.blue()
        )

        # embed char limit is 1024 so we must build many until no text is left
        build_res = tools.build_string(list_of_names, "", see_more=False)
        while build_res["rest_str"] is not None:
            embed.add_field(name='Result list:', value=build_res["embed_str"], inline=False)
            build_res = tools.build_string(build_res["rest_str"].split('\n'), "", see_more=False)  # .split('\n- ')[1:] to remove the first empty '-' because of how shitty tools.build_string() is made
        embed.add_field(name='Result list:', value=build_res["embed_str"], inline=False)

        embed.set_footer(text='Click name for more infos')

    return embed


# format an embed to display no result
def build_not_found_embed():
    embed = discord.Embed(
        title='Sorry chief, nothing found for that research.',
        description='',
        colour=discord.Colour.blue()
    )

    return embed


# format an embed to display item infos, "\u200b" to add a blank line
def build_item_embed(item):

    try:
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

        if item['icon']:
            embed.set_thumbnail(url=item['icon'])

        if item['price_date']:
            embed.set_footer(text='Click title for more infos - Last price update: ' + tools.days_since(tools.convert_date_tarkov_market(item['price_date'])))
        else:
            embed.set_footer(text='Click title for more infos')

        if len(item['notes']) > 0:
            notes_str = tools.build_string(item['notes'], item['url'] + "#Notes", prefix='- ')['embed_str']
            embed.add_field(name='Notes', value=notes_str, inline=False)

        if item['size']:
            embed.add_field(name='Size', value=item['size'] + ' (' + str(item['total_size']) + ')', inline=True)
        if item['weight']:
            embed.add_field(name='Weight', value=str(item['weight']) + ' kg', inline=True)
        if item['exp']:
            embed.add_field(name='Exp on loot', value=item['exp'] + '\n', inline=True)

        if item['price_day'] and item['price_change_day']:
            if item['price_change_day'] >= 0:   # add a '+' if it is positive
                embed.add_field(name='Avg. price 24H', value=str(item['price_day']) + ' ₽' + " (+" + str(int(item['price_change_day'])) + "%)", inline=True)
            else:
                embed.add_field(name='Avg. price 24H', value=str(item['price_day']) + ' ₽' + " (" + str(int(item['price_change_day'])) + "%)", inline=True)
        if item['price_week'] and item['price_change_week']:
            if item['price_change_week'] >= 0:  # add a '+' if it is positive
                embed.add_field(name='Avg. price 7d', value=str(item['price_week']) + ' ₽' + " (+" + str(int(item['price_change_week'])) + "%)", inline=True)
            else:
                embed.add_field(name='Avg. price 7d', value=str(item['price_week']) + ' ₽' + " (" + str(int(item['price_change_week'])) + "%)", inline=True)
        if item['price_slot_day']:
            embed.add_field(name='Avg. price/slot', value=str(item['price_slot_day']) + ' ₽', inline=True)
        if item['trader_name'] and item['trader_price']:
            embed.add_field(name='Best merchant rebuy', value=str(item['trader_price']) + ' ₽ (' + str(int(item['trader_price'] / item['total_size'])) + ' ₽/slot) at ' + item['trader_name'], inline=True)

        if len(item['quests']) > 0:
            quests_str = tools.build_string(item['quests'], item['url'] + "#Quests", prefix='- ')['embed_str']
            embed.add_field(name='Quests', value=quests_str, inline=False)

        if len(item['hideouts']) > 0:
            hideouts_str = tools.build_string(item['hideouts'], item['url'] + "#Hideout", prefix='- ')['embed_str']
            embed.add_field(name='Hideouts', value=hideouts_str, inline=False)

        if len(item['locations']) > 0:
            locations_str = tools.build_string(item['locations'], item['url'] + "#Location", prefix='- ')['embed_str']
            embed.add_field(name='Locations', value=locations_str, inline=False)

        if item['trade']:
            embed.set_image(url=item['trade'].replace('%22', '%2522'))

    except Exception as e:
        logger.info("Warning: Embed build failed for item: " + item['name'] + " - Reason: " + e)
        embed = build_error_embed(e)

    return embed
