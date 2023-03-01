import datetime
import time
import utils
import os

import discord
from discord.ext import commands
from discord.ext.commands import Context
from replit import db

def set_rank(ctx):
  users = utils.get_users(ctx)
  for user in users:
    key = 'v_' + str(user.id)
    db[key] = 0
  #set 28/02/2023
  db['v_'+str(248140709314428940)] = 14 #Y
  db['v_'+str(269883365048582144)] = 13 #J
  db['v_'+str(166867597118275587)] = 11 #K
  db['v_'+str(232076989245161472)] = 10 #R
  db['v_'+str(233667062759686144)] = 8 #A
  db['v_'+str(226765876509147140)] = 4 #Ta
  db['v_'+str(207244267242913792)] = 2 #To
  db['v_'+str(215510052302356480)] = 2 #B
  db['v_'+str(1036260269330010234)] = 2 #M
  db['v_'+str(232081135985754113)] = 1 #Ty


async def set_rank_v(ctx): #non-admin show
  start = time.time()
    
  set_rank(ctx)
  channels = utils.get_channels(ctx)
  good_perm = 1638597655616
  bot_member = utils.get_bot_as_member(ctx)
  v = os.environ['v']
  v_list = v.split()
  search_start = datetime.datetime(2023, 2, 28, 19, 49)
  
  for chan in channels:
    perm = chan.permissions_for(bot_member)
    perm_value = perm.value
    if perm_value == good_perm:
      async for message in chan.history(after=search_start, limit=999):
        if message.author.bot == False:
          for word in str(message.content).split():
            if word in v_list:
              key = 'v_' + str(message.author.id)
              db[key] += 1

  end = time.time() - start
  print('temps d\'exécution rank v : '+str(end))


class Ranking(commands.Cog, name="ranking"):

  def __init__(self, bot):
    self.bot = bot


  @commands.hybrid_command(name='showrank', description='Affiche un classement.')
  async def showrank(self, ctx: Context, arg):
    if arg == 'v':
      keys = db.prefix('v_')
      embed = discord.Embed(description="Classement v")
      dict = {}
      for key in keys:
        id = key[2:]
        name = utils.get_name_from_id(id, ctx)
        value =  db[key]
        dict[name] = value

      sorted_dict = sorted(dict.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
      top1 = utils.get_user_from_name(sorted_dict[0][0], ctx)
      #await ctx.send('Bravo pour ton Top 1 bg ' + top1.mention)
      await ctx.send('Bravo pour ton Top 1 bg ' + top1.nick)
      for i in range(10):
        name = utils.get_number_emoji(i+1, ctx) + ' ' + sorted_dict[i][0] 
        value = str(sorted_dict[i][1])
        embed.add_field(name=name, value=value, inline=False)
      await ctx.send(embed=embed)


  @commands.hybrid_command(name='rank', description='Calcule et affiche un classement (lent).')
  async def rank(self, ctx: Context, arg):
    if arg == 'v':
      await set_rank_v(ctx)
      keys = db.prefix('v_')
      embed = discord.Embed(description="Classement v")
      for key in keys:
        id = key[2:]
        name = utils.get_name_from_id(id, ctx)
        number =  str(db[key])
        embed.add_field(name=name, value=number)

      await ctx.send(embed=embed)


async def setup(bot):
  await bot.add_cog(Ranking(bot))