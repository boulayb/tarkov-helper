# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from bot_token import TOKEN
from datetime import datetime

import random
import discord
import logging

client = discord.Client()
es = Elasticsearch(hosts=[{"host":'elasticsearch'}])

# logs init
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s :: %(levelname)s :: %(message)s')
hdlr = logging.FileHandler("./logs_bot.txt")
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)


# 'YYYYMMDDHHmmss' to timestamp
# fuck this format and fuck you for using it 
def convert_date(date):

    year = int(date[0:4])
    date_without_year = date[4:]
    split = [int(date_without_year[i:i+2]) for i in range(0, len(date_without_year), 2)] # split line every two characters
    proper_date = datetime(year, split[0], split[1], split[2], split[3], split[4])

    return proper_date


def build_tips_embed():

    tips_list = [
        'Always plan your route before the start of the raid.',
        'Never go in raid without an objective.',
        'Never pick a fight you are not sure to win.',
        'Pick the right gear for the right raid.',
        'Never go out without heal, bandage and painkillers on you.',
        'You can\'t hear if you are loud.',
        'Always be suspicious of bushes.',
        'Take your time.',
        'Killa can freeze himself for a second when he is shot. Take advantage.',
        'Always protect your head first from grenades.',
        'Never camp the exit.',
        'Patience is rewarding.',
        'If it is too good to be true, it is probably a trap.',
        'If you don\'t have the biggest gun, have the biggest brain.',
        'Never feel too confident, but never be scared.',
        'Be a ninja.',
        'Never turn your back to a BEAR.',
        'Style is as important as protection.',
        'Always dominate with violence of action.',
        'Sometimes, it is ok to fall back.',
        'The priciest ammo might not be the best ammo.',
        'Grenades can solve complicated situations really fast.',
        'It is all about seeing before being seen.',
        'Don\'t be greedy.',
        'The hideout is a must have investment.',
        'Allways insure your belongings.',
        'Don\'t forget to log in to retrieve your insurances returns.',
        'The price that matters is the price per slot.',
        'As a group, always have a leading leader.',
        'Stay frosty.',
        'Keep an eye on the clock.']

    embed = discord.Embed(
        title=random.choice(tips_list),
        description='',
        colour=discord.Colour.blue()
    )

    return embed


def build_help_embed():
    embed = discord.Embed(
        title='USEC Command',
        description='Here to assist you in your raids, even you BEAR scums',
        colour=discord.Colour.blue()
    )

    #embed.set_author(name='USEC command', icon_url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/7/7d/Skill_mental_charisma.png?version=9d52bcf9bcd3a30e562b3327513a8709')
    embed.set_thumbnail(url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/7/7d/Skill_mental_charisma.png?version=9d52bcf9bcd3a30e562b3327513a8709')
    embed.set_footer(text='By Redleouf - contact: redleouf@gmail.com')
    embed.add_field(name='!command item [YOUR ITEM]', value='Display informations about the searched item', inline=False)
    embed.add_field(name='!command tips', value='Display a usefull tip to help you git gud', inline=False)
    embed.add_field(name='Data fetched from:', value='[EFT Wiki](https://escapefromtarkov.gamepedia.com) and [Loot Goblin](https://eft-loot.com/)', inline=False)

    return embed


# format an embed to display item infos
def build_item_embed(item):

    if item is None:
        embed = discord.Embed(
            title='',
            description='Sorry chief, nothing found for that research.',
            colour=discord.Colour.blue()
        )

    else:
        embed = discord.Embed(
            title=item['name'],
            description=item['description'] + "\n",
            timestamp=convert_date(item['price_date']),
            url=item['url'],
            colour=discord.Colour.blue()
        )

        # embed.set_image(url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/4/4e/TransilluminatorIcon.png?version=b944a5fa8ba1e7ee655cbebf7e83fb11')
        embed.set_thumbnail(url=item['icon'])
        embed.set_footer(text='Last updated: ')
        embed.add_field(name='Size', value=item['size'], inline=True)
        embed.add_field(name='Weight', value=item['weight'], inline=True)
        embed.add_field(name='Exp on loot', value=item['exp'] + "\n", inline=True) # "\u200b" to add a blank line
        embed.add_field(name='Avg. price', value=str(item['price']) + ' ₽', inline=True)
        embed.add_field(name='Avg. price/slot', value=str(item['price_slot']) + ' ₽', inline=True)

    return embed


### TODO: ajust research to be less precise (matche should return "matches")
# search item in ES by name and return a list of found items
def search_item(item):
    logger.info("Searching for item: " + item)
    items = []
    results = es.search(body={"query": {"match": {"name": item}}}, index='tarkov')
    if results["hits"]['total'] > 0:
        for result in results["hits"]["hits"]:
            items.append(result['_source'])
    logger.info("Found: " + str(len(items)))
    return items


# format should be "!command KEYWORD ITEM"
# KEYWORD can be 'tips', 'item', 'craft', 'trade', 'spawn', 'map'...
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!command') or message.content.startswith('!co'):
        logger.info("From: '" + str(message.author) + "' - '" + message.content + "'")
        words = message.content.split(' ')
        embeds = []

        if len(words) > 1 and words[1] == 'item':
            items = search_item(words[2])
            if len(items) > 0:
                for item in items:
                    embeds.append(build_item_embed(item))
            else:
                embeds.append(build_item_embed(None))
        
        elif len(words) > 1 and words[1] == 'tips':
            embeds.append(build_tips_embed())

        else:
            embeds.append(build_help_embed())

        channel = message.channel
        for embed in embeds:
            logger.info("Sending to: " + str(channel) + " - '" + str(embed) + "'")
            await channel.send(embed=embed)


@client.event
async def on_ready():
    logger.info("Bot started")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game('!command / !co'))


client.run(TOKEN)