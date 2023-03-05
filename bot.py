import discord
from discord.ext import commands, tasks
from discord.ext.commands import Bot, Context
from replit import db
import os
import random
import asyncio
import reactions
import macros
import time
import datetime
import utils
import sys

sys.path.insert(0, 'cogs')
import ranking


def admin_check(ctx, owner):
  if int(ctx.message.author.id) != int(owner):
    print('unauthorized access to admin command')
    return False
  else:
    return True


def run_bot():
  intents = discord.Intents.default()
  intents.message_content = True
  intents.members = True
  owner = os.environ['owner']

  bot = Bot(
    command_prefix=commands.when_mentioned_or('$'),
    intents=intents,
    help_command=None,
  )

  @bot.event
  async def on_ready() -> None:
    status_task.start()
    reset_anniv_task.start()
    print('bot ready')
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------')

  @bot.command()
  async def test(ctx, arg):
    if not admin_check(ctx, owner):
      return
    await ctx.send(arg)
    string = utils.remove_all(arg, '?')
    await ctx.send(str(arg) + ' ' + str(string))

  @bot.command()
  async def status(ctx, arg):
    if not admin_check(ctx, owner):
      return
    await bot.change_presence(activity=discord.Game(arg))

  @bot.command()
  async def status_toggle(ctx):
    if not admin_check(ctx, owner):
      return
    if status_task.is_running():
      status_task.cancel()
      await ctx.send('Boucle de status désactivée')
    else:
      status_task.start()
      await ctx.send('Boucle de status activée')

  @tasks.loop(minutes=1.0)
  async def status_task() -> None:
    statuses = [
      "LoL avec les boys", "Deep Rock Galactic avec les boys",
      "Pathfinder avec les boys", "Minecraft avec les boys",
      'Civ6 avec les boys', 'être raciste', 'manger son caca',
      '[STRENG GEHEIM]'
    ]
    await bot.change_presence(activity=discord.Game(random.choice(statuses)))

  @tasks.loop(hours=24.0)
  async def reset_anniv_task():
    await reset_anniv_def()

  async def reset_anniv_def():
    check_keys = db.prefix('check_anniv_')
    for check_key in check_keys:
      db[check_key] = 0
    print('reseted anniv message')     

  @bot.command()
  async def reset_anniv(ctx):
    if not admin_check(ctx, owner):
      return
    await reset_anniv_def()
    await ctx.send('Check anniversaire message reset')

  @bot.command()
  async def set_macro_lim(ctx, arg):
    if not admin_check(ctx, owner):
      return
    key = 'macro_lim'
    db[key] = arg
    await ctx.send('set macro_lim to '+arg)

  @bot.event
  async def on_message(message: discord.Message) -> None:
    if message.author == bot.user or message.author.bot:
      return
    await bot.process_commands(message)
    user_message = str(message.content)
    if len(user_message) == 0:
      return
    if user_message[0] == '$':
      return
    if user_message[0] == '!':
      user_message = user_message[1:]
      await macros.handle_macros(user_message, bot, message)
      return
    response = await reactions.handle_response(user_message, bot, message)
    if response == '':
      return
    if str(response)[0] == '<':
      await message.channel.send(embed=response)
    else:
      await message.channel.send(response)

  @bot.command()
  async def users(ctx):
    if not admin_check(ctx, owner):
      return
    members = []
    for member in ctx.guild.members:
      members.append(member.name)
    await ctx.send(str(members))

  @bot.command()
  async def channels(ctx):
    if not admin_check(ctx, owner):
      return
    guild = ctx.guild
    chan = []
    for channel in guild.channels:
      if channel.category != None:
        #print(str(channel.permissions_for(utils.get_bot_as_member(ctx))))
        chan.append(str(channel))
    await ctx.send(chan)

  @bot.command()
  async def set_rank_v(ctx):
    if not admin_check(ctx, owner):
      return

    start = time.time()
    ranking.set_rank(ctx)
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
        async for message in chan.history(after=search_start):
          if message.author.bot == False:
            for word in str(message.content).split():
              if word in v_list:
                key = 'v_' + str(message.author.id)
                db[key] += 1

    end = time.time() - start
    print('temps d\'exécution rank v : ' + str(end))
    await ctx.send('set rank v, temps = ' + str(end))

  @bot.command()
  async def farkle_show(context):
    if not admin_check(context, owner):
      return
    farkle_keys = db.prefix('farkle')
    embed = discord.Embed(description='farkle db :')
    for farkle_key in farkle_keys:
      print(farkle_key + ' ' + str(db[farkle_key]))
      embed.add_field(name=farkle_key, value=str(db[farkle_key]), inline=True)
    await context.send(embed=embed)

  @bot.command()
  async def farkle_setup(context):
    if not admin_check(context, owner):
      return
    utils.reset_farkle()
    await context.send('reset farkle')

  @tasks.loop(minutes=15.0)
  async def farkle_auto_reset():
    utils.reset_farkle()

  @bot.command()
  async def set_db(context, key, value, type='str'):
    if not admin_check(context, owner):
      return
    if value == '¤':
      db[key] = ''
      return
    if type == 'int':
      db[key] = int(value)
    else:
      db[key] = value
    await context.send('set value with no error')

  @bot.command()
  async def is_int(context, key):
    if not admin_check(context, owner):
      return
    if isinstance(db[key], int):
      await context.send('yes')
    else:
      await context.send('no')

  @bot.command()
  async def get_db(context, key):
    if not admin_check(context, owner):
      return
    await context.send(db[key])

  async def load_cogs() -> None:
    for file in os.listdir('cogs'):
      if file.endswith('.py'):
        print('charging ' + file)
        extension = file[:-3]
        try:
          await bot.load_extension(f"cogs.{extension}")
        except Exception as e:
          exception = f"{type(e).__name__}: {e}"
          print('error ' + exception)

  asyncio.run(load_cogs())
  token = os.environ['token']
  bot.run(token)
