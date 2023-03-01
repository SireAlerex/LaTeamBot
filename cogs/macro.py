import discord
from discord.ext import commands
from discord.ext.commands import Context
from replit import db

import general
import utils

good_macros = ['roll', 'bonjour']


class Macro(commands.Cog, name="macro"):

  def __init__(self, bot):
    self.bot = bot

  @commands.hybrid_command(name='addmacro', description='Ajoute une macro')
  async def addmacro(self, context: Context, arg):
    input = arg.split()
    if len(input) != 3:
      await context.send(
        'Erreur : format de macro incorrect, utiliser $addmacro "<nom> <commande> <paramètre>"'
      )
      return
    name = input[0]
    command = input[1]
    if not command in good_macros:
      await context.send('Mauvaise macro')
      return
    params = input[2]
    id = context.author.id

    if utils.get_user_macro_count(context, id) < int(
        utils.get_macro_lim(context)):
      key = 'macro_' + str(id) + '_' + name
      macro = command + '*' + params
      db[key] = macro
      await context.send('La macro '+name+' a bien été enregistrée')
    else:
      await context.send('macro count above limit')
      return
    return


  @commands.hybrid_command('editmacro', description='Modifie une macro')
  async def editmacro(self, context, name, arg):
    try:
      key = 'macro_' + str(context.author.id) + '_' + name
      macro = arg.split()
      command = macro[0]
      param = macro[1]
      new = command + '*' + param
      db[key] = new
      await context.send('Macro ' + name + ' modifiée')
      return
    except Exception as e:
      await context.send('Erreur editmacro : utiliser la syntaxe "$editmacro <nom> "<commande> <paramètre>""')
      return


  @commands.hybrid_command(name='showmacro', description='Montre les macros')
  async def showmacro(self, context):
    prefix = 'macro_' + str(context.author.id)
    length = len(prefix) + 1
    user_macros = db.prefix(prefix)
    if len(user_macros) == 0:
      await context.send('Pas de macros')
    else:
      desc = 'Liste des macros de ' + str(context.author)
      embed = discord.Embed(title='Macros', description=desc)
      for user_macro in user_macros:
        name = user_macro[length:]
        macro = db[user_macro].split('*')
        command = macro[0]
        param = macro[1]
        value = command + ' ' + param
        embed.add_field(name=name, value=value, inline=False)
      await context.send(embed=embed)


  @commands.hybrid_command(name='delmacro', description='Supprime une macro')
  async def delmacro(self, context, name):
    try:
      key = 'macro_' + str(context.author.id) + '_' + name
      del db[key]
      await context.send('Macro ' + name + ' supprimée')
      return
    except Exception as e:
      await context.send('Erreur delmacro : ' + e)
      return
      

  @commands.hybrid_command(name='clearmacro', description='Supprime toutes les macros')
  async def clearmacro(self, context):
    prefix = 'macro_' + str(context.author.id)
    length = len(prefix) + 1
    user_macros = db.prefix(prefix)
    if len(user_macros) == 0:
      await context.send('Pas de macros')
    else:
      for user_macro in user_macros:
        del db[user_macro]
      await context.send('Vos macros ont bien été supprimées')


async def setup(bot):
  await bot.add_cog(Macro(bot))
