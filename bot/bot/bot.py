# -*- coding: utf-8 -*-

from bot_token import TOKEN
from settings import *

import builder
import search


# format should be "!command KEYWORD ITEM"
@client.event
async def on_message(message):

    # we do not want the bot to reply to itself
    if message.author == client.user:
        return

    if message.content.startswith('!command') or message.content.startswith('!co'):
        logger.info("From: '" + str(message.author) + "' - '" + message.content + "'")
        cleaned_message = ' '.join(message.content.split())
        words = cleaned_message.split(' ')
        embeds = []

        # ITEM command
        if len(words) > 1 and words[1] == 'item':
            search_query = ' '.join(words[2:]) # rejoin the user query with space
            result = search.search_item(search_query)
            if result['total'] == -1:
                embeds.append(builder.build_error_embed(result['items'][0]))
            elif len(result['items']) > 0:
                if result['total'] > len(result['items']):
                    embeds.append(builder.build_too_many_embed(result['total'], search_query))
                for item in result['items']:
                    embeds.append(builder.build_item_embed(item))
            else:
                embeds.append(builder.build_item_embed(None))

        # SEARCH command
        elif len(words) > 1 and words[1] == 'search':
            search_query = ' '.join(words[2:]) # rejoin the user query with space
            result = search.search_item(search_query, advanced=True)
            if result['total'] == -1:
                embeds.append(builder.build_error_embed(result['items'][0]))
            elif len(result['items']) > 0:
                if result['total'] > len(result['items']):
                    embeds.append(builder.build_too_many_embed(result['total'], search_query))
                for item in result['items']:
                    embeds.append(builder.build_item_embed(item))
            else:
                embeds.append(builder.build_item_embed(None))

        # LIST command
        elif len(words) > 1 and words[1] == 'list':
            search_query = ' '.join(words[2:]) # rejoin the user query with space
            result = search.search_item(search_query, res_size=50, advanced=True, scroll_time='10s')
            if result['total'] == -1:
                embeds.append(builder.build_error_embed(result['items'][0]))
            elif len(result['items']) == 0:
                embeds.append(builder.build_item_embed(None))
            else:
                while len(result['items']) > 0:
                    embeds.append(builder.build_list_embeds(result['items'], search_query))
                    result = search.scroll_item(result['scroll_id'], scroll_time='10s')

        # MEDICAL command
        elif len(words) > 1 and words[1] == 'medical':
            embeds.append(builder.build_image_embed("Medical helper", CONST_MEDICAL_IMAGE))     ### TODO: Replace CONST by ES search for the file

        # INJECTOR command
        elif len(words) > 1 and (words[1] == 'injector' or words[1] == 'injectors'):
            embeds.append(builder.build_image_embed("Injector helper", CONST_INJECTOR_IMAGE))   ### TODO: Replace CONST by ES search for the file

        # TIP command
        elif len(words) > 1 and (words[1] == 'tips' or words[1] == 'tip'):
            embeds.append(builder.build_tips_embed())

        # UNKNOWN command
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
