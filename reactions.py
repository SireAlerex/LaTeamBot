import discord
import random

import utils
import datetime
from replit import db

societe = ['sociét', 'societ']
sus = ['sus']
cum = ['cum']
fromage = ['fromage']
cfr = ['pas mal non']
conversano = ['arab']
source = ['source ?', 'sources ?']
bot_list = ['bot', 'robot']
salutations = ['bonjour', 'salut', 'coucou', 'yo']
good_bot = ['good', 'bon', 'gentil']
bad_bot = ['bad', 'méchant', 'mauvais']
hot_bot = ['gay bot']
thomas = ['thomas', 'attend', 'civ']
pirate_epee = ['belle', 'bite']

def nerdify(string):
  res = ""
  for i in range(len(string)):
    if i%2 != 0:
      res += string[i].upper()
    else:
      res += string[i]
  return res

def find_any_word(word_list, source_list):
  if any(word in word_list for word in source_list):
    return True
  else:
    return False

def find_any_substring(word_list, message):
  for word in word_list:
    if message.count(word) > 0:
      return True
  return False    


def handle_response(user_message, bot, message) -> str:
  p_message = user_message.lower()
  p_list = p_message.split()

  #message d'anniversaire
  raw_anniv = utils.get_anniv(message.author.id)
  if raw_anniv != 'not found':
    day = int(raw_anniv.split('-')[0])
    month = int(raw_anniv.split('-')[1])
    anniv = datetime.datetime(1, month, day)
    today = datetime.date.today()
    if anniv.month == today.month and anniv.day == today.day:
      check_key = 'check_anniv_' + str(message.author.id)
      if db[check_key] == 0:
        return ('Joyeux anniversaire ' + format(message.author.mention))
        db[check_key] = 1

  if find_any_word("saucisse", p_list) or find_any_substring(societe, p_message): #saucisse
    emoji = discord.utils.get(bot.emojis, name='saucisse')
    return 'saucisse ' + str(emoji) + ' !'

  if find_any_substring(sus, p_message):  #réaction sus
    emoji = discord.utils.get(bot.emojis, name='afungus')
    return 'sus ' + str(emoji)

  if find_any_word(['fromage'], p_list):  #réaction fromage
    emoji = discord.utils.get(bot.emojis, name='fromage')
    return str(emoji)

  if p_message == 'oof':  #réaction oof
    emoji = discord.utils.get(bot.emojis, name='OOF')
    return str(emoji)

  if find_any_word(cum, p_list): #cum
    emoji = discord.utils.get(bot.emojis, name='milk')
    return 'cum :milk:'

  if find_any_substring(source, p_message): #source
      return 'Ça m\'est apparu dans un rêve'

  if find_any_substring(cfr, p_message): #pas mal non ?
    return 'C\'est français :flag_fr:'

  if find_any_word(bot_list, p_list) and find_any_word(salutations, p_list): #bonjour !
    return (random.choice(salutations)).capitalize() + " !"

  if find_any_word(bot_list, p_list) and find_any_word(good_bot, p_list): #good bot
    good_bot_reactions = [':smiley:', ':smile:', ':grin:', ':blush:',      
     ':smiling_face_with_3_hearts:']
    return random.choice(good_bot_reactions)

  if find_any_word(bot_list, p_list) and find_any_word(bad_bot, p_list): #bad bot
    bad_bot_reactions = [':nerd:', ':pensive:', ':worried:', ':slight_frown:', ':frowning2:',           ':cry:']
    reaction = random.choice(bad_bot_reactions)
    if reaction == ":nerd:":
      return "\"" + nerdify(p_message) + "\" " + reaction
    return reaction

  if find_any_substring(hot_bot, p_message):
    hot_bot_reaction = [':hot_face:', ':shushing_face:']
    return random.choice(hot_bot_reaction)

  count_thomas = 0
  for word in thomas:
    if p_message.count(word) > 0:
      count_thomas += 1
  if count_thomas >= 3:
    emoji = discord.utils.get(bot.emojis, name='Bedge')
    return ' ' + str(emoji)

  count_drapeau = 0
  for word in pirate_epee:
    if p_list.count(word) > 0:
      count_drapeau += 1
    if count_drapeau >= 2:
      swords = '\U00002694️'
      pirate = '\U0001F3F4'+'\U0000200D'+'\U00002620'+'\U0000FE0F'
      res_list = [swords, pirate]
      return res_list

  if find_any_substring(conversano, p_message):
    link = 'https://media.tenor.com/UUXIxp7UiI4AAAAC/bagarre-soral.gif'
    embed = discord.Embed(description='Conversano')
    embed.set_image(url=link)
    return embed

  return ''
