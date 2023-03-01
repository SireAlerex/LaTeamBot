import discord
import sys
sys.path.insert(0, 'cogs')
import general
import utils
import datetime
from replit import db

societe = ['société', 'societe', 'societer', 'saucisse']
sus = ['sus', 'sussy']
cum = ['cum']
conversano = ['arabe', 'arabes']
source = ['source ?', 'sources ?']
bonjour = ['bonjour bot', 'bonjour le bot', 'salut bot', 'salut le bot', 'yo bot', 'yo le bot', 'coucou bot', 'coucou le bot']


async def handle_response(user_message, bot, message) -> str:
  p_message = user_message.lower()
  context = await bot.get_context(message)
  
  raw_anniv = utils.get_anniv(message.author.id)
  if raw_anniv != 'not found':
    day = int(raw_anniv.split('-')[0])
    month = int(raw_anniv.split('-')[1])
    anniv = datetime.datetime(1, month, day)
    today =datetime.date.today()
    if anniv.month == today.month and anniv.day == today.day:
      check_key = 'check_anniv_' + str(message.author.id)
      if db[check_key] == 0:
        await context.send('Joyeux anniversaire ' + format(message.author.mention))
        db[check_key] = 1

  if any(word in p_message for word in societe):  #réaction saucisse
    emoji = discord.utils.get(bot.emojis, name='saucisse')
    return 'saucisse ' + str(emoji) + ' !'

  if any(word in p_message for word in sus):  #réaction sus
    emoji = discord.utils.get(bot.emojis, name='afungus')
    return 'sus ' + str(emoji)
  
  if p_message == 'fromage':  #réaction fromage
    emoji = discord.utils.get(bot.emojis, name='fromage')
    return str(emoji)

  if p_message == 'oof':  #réaction oof
    emoji = discord.utils.get(bot.emojis, name='OOF')
    return str(emoji)

  if any(word in p_message for word in cum):
    emoji = discord.utils.get(bot.emojis, name='milk')
    return 'cum :milk:'

  for word in source:
    if p_message.count(word) > 0:
      return 'Ça m\'est apparu dans un rêve'

  cfr = 'pas mal non'
  if p_message.count(cfr) >= 1:
    return 'C\'est français :flag_fr:'

  for word in bonjour:
    if p_message.count(word) > 0:
      await general.bonjour(context)

  

  if any(word in p_message for word in conversano):
    link = 'https://media.tenor.com/UUXIxp7UiI4AAAAC/bagarre-soral.gif'
    embed = discord.Embed(description='Conversano')
    embed.set_image(url=link)
    return embed

  return ''