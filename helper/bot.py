# -*- coding: utf-8 -*-

from elasticsearch import Elasticsearch
from bot_token import TOKEN

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
# KEYWORD can be 'fact', 'item', 'craft', 'trade', 'spawn', 'map'
@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!command'):
        logger.info("From: '" + str(message.author) + "' - '" + message.content + "'")

        words = message.content.split(' ')
        if len(words) > 1 and words[1] == 'item':

            items = search_item(words[2])
            if len(items) > 0:
                msg = ""
                for item in items:
                    msg += 'Name: ' + item['name'] + '\n' + 'Description: ' + item['description'] + '\n'
            else:
                msg = "Sorry chief, nothing found for that research."

            channel = message.channel
            logger.info("Sending to: " + str(channel) + " - '" + msg + "'")
            await channel.send(msg)

        elif words[1] == 'test':

            embed = discord.Embed(
                title='TEST',
                description='this is a test',
                colour=discord.Colour.blue()
            )

            embed.set_footer(text='footer test')
            embed.set_image(url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/4/4e/TransilluminatorIcon.png?version=b944a5fa8ba1e7ee655cbebf7e83fb11')
            embed.set_thumbnail(url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/4/4e/TransilluminatorIcon.png?version=b944a5fa8ba1e7ee655cbebf7e83fb11')
            embed.set_author(name='USEC Command', icon_url='https://gamepedia.cursecdn.com/escapefromtarkov_gamepedia/7/7d/Skill_mental_charisma.png?version=9d52bcf9bcd3a30e562b3327513a8709')
            embed.add_field(name='field1', value='field1 test', inline=False)
            embed.add_field(name='field2', value='field2 test', inline=True)
            embed.add_field(name='field3', value='field3 test', inline=True)

            channel = message.channel
            await channel.send(embed=embed)

        elif words[1] == 'fact':

            jb = discord.utils.get(message.guild.members, name = 'Juanito')
            msg = jb.mention + ' will not uninstall the game after the next patch.'

            channel = message.channel
            await channel.send(msg)


@client.event
async def on_ready():
    logger.info("Bot started")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')


client.run(TOKEN)