import sys

import utils

sys.path.insert(0, 'cogs')
import general


async def handle_macros(user_message, bot, message):
  context = await bot.get_context(message)
  msg = user_message.split()
  if len(msg) < 1:
    await context.send('Erreur : pas de nom de macro')
    return
  else:
    name = msg[0]
    id = message.author.id
    macro = utils.get_macro(context, id, name)
    if macro == 'not found':
      await context.send('Erreur : macro inconnue')
      return
    macro = macro.split('*')
    command = macro[0]
    param = macro[1]

    if command == 'roll':
      await general.roll(context, param)
  return
