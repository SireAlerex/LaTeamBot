import os
import discord
from discord.ext import commands
from discord.ext.commands import Context
from replit import db


def get_channels(ctx: Context):
  chan = []
  for channel in ctx.guild.channels:
    if channel.category != None and channel.type == discord.ChannelType.text:
      chan.append(channel)
  return chan


def get_user_from_name(name, ctx):
  users = get_users(ctx)
  for user in users:
    if user.nick == name:  
      return user


def get_users(ctx: Context):
  members = []
  for member in ctx.guild.members:
    if member.bot == False:
      members.append(member)
  return members


def get_name_from_id(id, ctx: Context):
  users = get_users(ctx)
  b = os.environ['b']
  for user in users:
    if user.id == int(id):
      return user.nick
  if int(id) == int(b):
    return 'Billy'
  return 'user not found'


def get_bot_as_member(ctx):
  bot_id = int(os.environ['bot_id'])
  for member in ctx.guild.members:
    if member.id == bot_id:
      return member
  print('didnt found')
  return ''


def get_anniv(id):
  key = 'anniv_' + str(id)
  try:
    value = db[key]
    return db[key]
  except Exception as e:
    return 'not found'


def get_number_emoji(number, ctx):
  numbers = {}
  numbers[0] = ':zero:'
  numbers[1] = ':one:'
  numbers[2] = ':two:'
  numbers[3] = ':three:'
  numbers[4] = ':four:'
  numbers[5] = ':five:'
  numbers[6] = ':six:'
  numbers[7] = ':seven:'
  numbers[8] = ':eight:'
  numbers[9] = ':nine:'
  numbers[10] = ':keycap_ten:'
  if number >= 0 and number <= 10:
    return numbers[number]
  else:
    return 'Erreur : number emoji'

def get_user_macro_count(context, id):
  key = 'macro_' + str(id)
  user_macros = db.prefix(key)
  return len(user_macros)

def get_macro_lim(context):
  return db['macro_lim']

def get_macro(context, id, name):
  key = 'macro_' + str(id)
  length = len(key)+1
  user_macros = db.prefix(key)
  for user_macro in user_macros:
    test = user_macro[length:]
    if test == name:
      return db[user_macro]
  return 'not found'