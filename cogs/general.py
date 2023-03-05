import platform
import random
import secrets
import os
import time
import utils
from replit import db

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context


async def roll(ctx, arg):
  try:
    roll = arg
    first_split = roll.split('d', 1)  #sépare le nombre de dés du reste
    if first_split[0] == '':
      roll_count = 1  #par défaut, nombre de dé = 1
    else:
      roll_count = int(roll.split('d', 1)[0])
      if roll_count < 1:
        raise Exception('Nombre de dés inférieur à 1')

    positive_mod = True
    if first_split[1].find('+') != -1:  #sépare taille du dé et mod
      second_split = first_split[1].split('+', 1)
    else:
      second_split = first_split[1].split('-', 1)
      positive_mod = False

    dice = second_split[0]  #taille du dé
    if int(dice) < 1:
      raise Exception('Taille du dé inférieur à 1')
    if len(second_split) == 1:
      modifier = '0'  #par défaut mod = 0
    else:
      modifier = second_split[1]  #modifier du lancer

    if roll_count > 100:  #pour éviter les trop longues boucles
      raise Exception('Nombre maximum de dés : 100')

    value = 0  #valeur du lancer de dé(s)
    res = ''  #affichage des calculs
    for i in range(roll_count):
      #rolled = random.randint(1, int(dice))
      rolled = secrets.randbelow(int(dice)) + 1  #0-5 +1
      value += rolled
      if roll_count > 1:  #ajoute les lancers à l'affichage
        res += str(rolled) + ' + '
      else:  #ajoute le lancer à l'affichage
        res += str(rolled) + ' '

    if roll_count > 1:
      res = res[:-2]  #enlève '+ ' final en trop

    if positive_mod:  #rajoute le modifier aux dés
      value += int(modifier)
    else:
      value -= int(modifier)

    if int(modifier) != 0 or roll_count > 1:  #afficher modificateur et =
      if int(modifier) != 0:
        if positive_mod:
          res += '(+' + modifier + ')'
        else:
          res += '(-' + modifier + ')'
      res += ' = '
      res += str(value)

    await ctx.send(res)
  except Exception as e:
    error = 'Erreur : ' + str(
      e) + '\n format du $roll incorrect, utiliser : (k)d<n>+(m)'
    await ctx.send(error)


async def bonjour(ctx):
  salutations = ['Bonjour !', 'Salut !', 'Coucou !', 'Yo !']
  await ctx.send(random.choice(salutations))


class General(commands.Cog, name="general"):

  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(name="help",
                           description="Liste les commandes du bot.")
  async def help(self, context: Context) -> None:
    prefix = '$'
    embed = discord.Embed(title="Help",
                          description="Liste des commandes disponibles :",
                          color=0x9C84EF)
    for i in self.bot.cogs:
      cog = self.bot.get_cog(i.lower())
      commands = cog.get_commands()
      data = []
      for command in commands:
        description = command.description.partition("\n")[0]
        data.append(f"{prefix}{command.name} - {description}")
      help_text = "\n".join(data)
      embed.add_field(name=i.capitalize(),
                      value=f"```{help_text}```",
                      inline=False)
    await context.send(embed=embed)

  @commands.hybrid_command(name='bonjour', description='Dit \'bonjour\'.')
  async def dit(self, context: Context) -> None:
    await bonjour(context)

  @commands.hybrid_command(name='slide', description='Slide dans tes dm')
  async def slide(self, ctx: Context):
    await ctx.message.author.send('Salut!')

  @commands.hybrid_command(
    name='roll', description='Lancer de dé(s) sous la forme (k)d<n>+(m)')
  async def roll(self, ctx: Context, arg) -> None:
    await roll(ctx, arg)

  @commands.hybrid_command(name='basé',
                           description='Détermine si c\'est basé ou cringe')
  async def basé(self, context: Context):
    rolled = secrets.randbelow(2)
    if rolled == 0:
      result = 'Basé'
    else:
      result = 'Cringe'
    await context.send(result)

  @commands.hybrid_command(
    name='anniv',
    description='Mettre son anniversaire dans la base de données')
  async def anniv(self, context: Context, arg):
    try:
      date = arg
      user = context.author
      key = 'anniv_' + str(user.id)
      db[key] = date
      check_key = 'check_anniv_' + str(user.id)
      check_value = 0
      db[check_key] = check_value
      await context.send('Date d\'anniversaire mise à ' + date)
    except Exception as e:
      error = 'Format incorrect, utiliser : $anniv <jour>-<mois>'
      await context.send(error)

  @commands.hybrid_command(name='showanniv',
                           description='Montre son anniversaire')
  async def showanniv(self, context: Context):
    try:
      key = 'anniv_' + str(context.author.id)
      value = db[key]
      await context.send('Votre anniversaire : ' + str(value))
    except Exception as e:
      error = 'Pas d\'anniversaire dans la base de données, utilisez $anniv <votre-anniv>'
      await context.send(error)


async def setup(bot):
  await bot.add_cog(General(bot))
