# -*- coding: utf-8 -*-

from bot_token import TOKEN
from settings import *

import builder


# search item in ES by name and return a list of found items
def search_item(item):
    logger.info("Searching for item: " + item)

    items = []

    search = es.search(body={"query": {"query_string": {"default_field": "name", "query": "*" + item + "*"}}}, index='tarkov', size=3)
    total = search['hits']['total']
    if total > 0:
        for hit in search['hits']['hits']:
            items.append(hit['_source'])

    result = {'total': total, 'items': items}

    logger.info("Found " + str(total) + " items, returning " + str(len(items)))
    return result


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
            result = search_item(words[2])
            if len(result['items']) > 0:
                if result['total'] > len(result['items']):
                    embeds.append(builder.build_too_many_embed(result['total'], words[2]))
                for item in result['items']:
                    embeds.append(builder.build_item_embed(item))
            else:
                embeds.append(builder.build_item_embed(None))
        
        elif len(words) > 1 and words[1] == 'tips':
            embeds.append(builder.build_tips_embed())

        else:
            embeds.append(builder.build_help_embed())

        channel = message.channel
        for embed in embeds:
            logger.info("Sending to: " + str(channel) + " - '" + str(embed.to_dict()) + "'")
            await channel.send(embed=embed)


@client.event
async def on_ready():

    logger.info("Bot started")
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    await client.change_presence(activity=discord.Game('!command / !co'))


def main():

    client.run(TOKEN)

    # close log handle
    log_hdlr.close()
    logger.removeHandler(log_hdlr)


if __name__ == "__main__":
    main()
