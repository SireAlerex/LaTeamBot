import discord
from discord.ext import commands, tasks
from discord.ext.commands import Context
from replit import db

import utils
import secrets


async def lancer(context):
  #check roll vide ?
  player1 = True
  dices = db['farkle_player1_dices']
  player = utils.get_user_from_id(int(db['farkle_player1']), context)
  if db['farkle_turn'] == 2:
    dices = db['farkle_player2_dices']
    player1 = False
    player = utils.get_user_from_id(int(db['farkle_player2']), context)

  await context.send('Voici ton lancer de dés ' + player.mention)
  roll = ''
  for i in range(dices):
    roll += str(secrets.randbelow(6) + 1) + '   '
  roll = roll[:-1]
  await context.send(roll)

  check = roll.split()
  if score_from_roll(check) == 0:
    await context.send('Vous ne pouvez pas marquer de points avec ce lancer')
    await show_score(context)
    tour_suivant()
    await lancer(context)
    return

  if player1:
    db['farkle_player1_roll'] = roll
  else:
    db['farkle_player2_roll'] = roll


def tour_suivant():
  if db['farkle_turn'] == 1:
    db['farkle_turn'] = 2
    db['farkle_player1_roll'] = ''
    db['farkle_player1_dices'] = 6
  elif db['farkle_turn'] == 2:
    db['farkle_turn'] = 1
    db['farkle_player2_roll'] = ''
    db['farkle_player2_dices'] = 6
  db['farkle_score_temp'] = 0


async def check_win(context, bot):
  if db['farkle_player1_score'] >= db['farkle_maxscore']:
    player = utils.get_user_from_id(int(db['farkle_player1']), context)
    await context.send('Bravo ' + player.name + ', tu as gagné !')
    utils.reset_farkle()
    bot.game_timer.cancel()
    return
  if db['farkle_player2_score'] >= db['farkle_maxscore']:
    player = utils.get_user_from_id(int(db['farkle_player2']), context)
    await context.send('Bravo ' + player.name + ', tu as gagné !')
    utils.reset_farkle()
    bot.game_timer.cancel()
    return
  tour_suivant()
  await lancer(context)


def full_straight(dices):
  if dices[0] != 1 or len(dices) != 6:
    return False
  counter = 1
  for i in range(1, len(dices)):
    if dices[i] == 1 + dices[i - 1]:
      counter += 1
  if counter == 6:
    return True
  else:
    return False


def partial_straight(dices):
  counter = 1
  for i in range(1, len(dices)):
    if dices[i] == 1 + dices[i - 1]:
      counter += 1
  if counter == 5:
    return True
  else:
    return False

def get_max_score_roll(dices):
  rolls = []
  for raw_roll in dices:
    rolls.append(int(raw_roll))
  rolls.sort()
  score = 0
  if full_straight(rolls):
    return dices

  result = []
  if len(rolls) == 5 and partial_straight(rolls):
    temp = rolls.copy()
    if rolls[0] == 1:  #lower partial straight
      score += 500
    elif rolls[0] == 2:  #higher partial straight
      score += 750
  elif len(rolls) == 6 and rolls[1] <= 3:
    temp = rolls[1:] if rolls[0] == rolls[1] else rolls[:-1]
    if rolls[1] == 1 and partial_straight(temp):  #1-1-2-3-4-5
      score += 500
    elif rolls[1] == 3 and partial_straight(temp):  #2-3-4-5-6-6
      score += 750
    elif rolls[1] == 2 and partial_straight(temp):  #1-2-3-4-5-5
      score += 500 if rolls[0] == 1 else 750  #ou 2-2-3-4-5-6
  if score > 0:  #found partial straight
    for number in temp:
      rolls.remove(number)
      result.append(number)

  count_1 = rolls.count(1)  #process 1s
  if count_1 >= 3:
    score += 1000 * (2**(count_1 - 3))
  if count_1 == 1 or count_1 == 2:
    score += 100 * count_1
  for i in range(count_1):
    rolls.remove(1)
    result.append(1)

  for i in range(2, 7):  #process 2 to 6
    count = rolls.count(i)
    if count >= 3:
      score += 100 * i * (2**(count - 3))
      for k in range(count):
        rolls.remove(i)
        result.append(i)
    if i == 5:  #process 1*5 and 2*5
      if count == 1 or count == 2:
        score += 50 * count
        for k in range(count):
          rolls.remove(i)
          result.append(i)

  return result


def score_from_roll(dices):
  rolls = []
  for raw_roll in dices:
    rolls.append(int(raw_roll))
  rolls.sort()
  score = 0
  if full_straight(rolls):
    return 1500

  if len(rolls) == 5 and partial_straight(rolls):
    temp = rolls.copy()
    if rolls[0] == 1:  #lower partial straight
      score += 500
    elif rolls[0] == 2:  #higher partial straight
      score += 750
  elif len(rolls) == 6 and rolls[1] <= 3:
    temp = rolls[1:] if rolls[0] == rolls[1] else rolls[:-1]
    if rolls[1] == 1 and partial_straight(temp):  #1-1-2-3-4-5
      score += 500
    elif rolls[1] == 3 and partial_straight(temp):  #2-3-4-5-6-6
      score += 750
    elif rolls[1] == 2 and partial_straight(temp):  #1-2-3-4-5-5
      score += 500 if rolls[0] == 1 else 750  #ou 2-2-3-4-5-6
  if score > 0:  #found partial straight
    for number in temp:
      rolls.remove(number)

  count_1 = rolls.count(1)  #process 1s
  if count_1 >= 3:
    score += 1000 * (2**(count_1 - 3))
  if count_1 == 1 or count_1 == 2:
    score += 100 * count_1
  for i in range(count_1):
    rolls.remove(1)

  for i in range(2, 7):  #process 2 to 6
    count = rolls.count(i)
    if count >= 3:
      score += 100 * i * (2**(count - 3))
      for k in range(count):
        rolls.remove(i)
    if i == 5:  #process 1*5 and 2*5
      if count == 1 or count == 2:
        score += 50 * count
        for k in range(count):
          rolls.remove(i)

  if len(rolls) == 0 or score == 0:
    return score
  else:
    return -1


async def show_score(context):
  player1 = utils.get_user_from_id(int(db['farkle_player1']), context)
  player2 = utils.get_user_from_id(int(db['farkle_player2']), context)

  embed = discord.Embed(title='Farkle', description='Scores :')
  embed.add_field(name=player1.name, value=db['farkle_player1_score'])
  embed.add_field(name=player2.name, value=db['farkle_player2_score'])
  await context.send(embed=embed)

def get_id_p1():
  return db['farkle_player1']

def get_id_p2():
  return db['farkle_player2']

def can_play(id):
  if db['farkle_turn'] == 1 and id == get_id_p1():
    return True
  if db['farkle_turn'] == 2 and id == get_id_p2():
    return True
  return False


class Farkle(commands.Cog, name='farkle'):

  def __init__(self, bot):
    self.bot = bot

  @tasks.loop(minutes=5.0, count=1)
  async def start_timer(self):
    print('start start loop !')

  @start_timer.after_loop
  async def after_start_timer(self):
    if db['farkle_player2'] == -1:
      utils.reset_farkle()
      print('start loop ended')

  @tasks.loop(minutes=15.0, count=1)
  async def game_timer(self):
    print('start game loop !')

  @game_timer.after_loop
  async def after_game_timer(self):
    utils.reset_farkle()
    print('game timer ended')
  
  @commands.hybrid_command(name='farkle',description='Lance une partie de farkle. Options : "start", "join", "score <x-y-z>", "max", "relance", "passe", "help", "reset", "test"')
  async def farkle(self, context: Context, arg='', arg2=''):
    if arg == '':
      await context.send('Pas d\'argument')
      return
    id = context.author.id
    if arg == 'start':
      if db['farkle'] != 0:
        await context.send('Erreur : ne peut pas démarrer la partie')
        return
      db['farkle'] = 1
      db['farkle_player1'] = id
      await context.send('Partie setup, en attente d\'un autre joueur ($farkle join)')
      self.start_timer.start()
      return

    if arg == 'join':
      if db['farkle'] != 1:
        await context.send('Erreur : pas de partie en cours ($farkle start)')
        return
      if db['farkle_player2'] != -1:
        await context.send('Erreur : déjà un joueur 2')
        return
      self.start_timer.cancel()
      self.game_timer.start()
      db['farkle_player2'] = id
      db['farkle_turn'] = 1
      await lancer(context)
      return

    if arg == 'score' or arg == 's':
      if not can_play(id):
        return
      if arg2.count('-') > 0: #a-b-c format
        choices = arg2.split('-')
      else: #"a b c" format
        choices = arg2.split()
      if db['farkle_turn'] == 1:
        roll = db['farkle_player1_roll'].split()
      elif db['farkle_turn'] == 2:
        roll = db['farkle_player2_roll'].split()
      test_roll = roll.copy()
      if not all(roll in test_roll for roll in choices):
        await context.send('Pas de triche !')
        return
      score = score_from_roll(choices)
      if score == -1:
        await context.send('Mauvaise saisie des dés : certains ne marquent pas de points')
        return
      db['farkle_score_temp'] += score
      #update dés restants
      if db['farkle_turn'] == 1:
        db['farkle_player1_dices'] -= len(choices)
        if db['farkle_player1_dices'] == 0:
          db['farkle_player1_dices'] = 6
        msg = 'Vous pouvez relancer vos ' + str(
          db['farkle_player1_dices']) + ' dés restants'
      elif db['farkle_turn'] == 2:
        db['farkle_player2_dices'] -= len(choices)
        if db['farkle_player2_dices'] == 0:
          db['farkle_player2_dices'] = 6
        msg = 'Vous pouvez relancer vos ' + str(
          db['farkle_player2_dices']) + ' dés restants'

      msg += ' ou augmenter vos points de ' + str(db['farkle_score_temp'])
      await context.send(msg)
      await context.send('Utilisez "$farkle relance" ou "$farkle passe"')
      return

    if arg == 'relancer' or arg == 'relance' or arg == 'r':
      if not can_play(id):
        return
      await lancer(context)
      return
      
    if arg == 'passer' or arg == 'passe' or arg == 'p':
      if not can_play(id):
        return
      if db['farkle_turn'] == 1:
        db['farkle_player1_score'] += db['farkle_score_temp']
      elif db['farkle_turn'] == 2:
        db['farkle_player2_score'] += db['farkle_score_temp']
      await show_score(context)
      await check_win(context, self)
      return

    if arg == 'test' or arg == 't':
      if arg2.count('-') > 0: #a-b-c format
        rolls = arg2.split('-')
      else: #"a b c" format
        rolls = arg2.split()
      score = score_from_roll(rolls)
      await context.send('Score du test : ' + str(score))
      return

    if arg == 'reset':
      if get_id_p1() == -1 or get_id_p2() == -1:
        await context.send('Pas de partie à reset')
        return
      if id == db['farkle_player1'] and db[
          'farkle_reset_player1'] == 0:
        db['farkle_reset_player1'] = 1
        await context.send('Joueur 1 veut reset le jeu')
      elif id == db['farkle_player2'] and db[
          'farkle_reset_player2'] == 0:
        db['farkle_reset_player2'] = 1
        await context.send('Joueur 2 veut reset le jeu')
      if db['farkle_reset_player1'] == 1 and db['farkle_reset_player2'] == 1:
        utils.reset_farkle()
        await context.send('Le jeu a été reset')
        self.game_timer.cancel()
      return

    if arg == 'help' or arg == 'h':
      embed = discord.Embed(title='Farkle',
                            description='Comment jouer au Farkle ?')
      rules = 'Le but est de faire le plus de score possible à partir d\'un ou plusieurs lancers de 6d6.\n'
      rules += 'Le jeu se joue en duel au tour par tour. A son tour, un joueur doit sélectionner les dés qu\'il souhaite prendre pour marquer des points puit doit choisir s\'il veut relancer les dés restants pour marquer plus de points ou s\'il marque les points cumulés lors de son tour. S\'il ne lui reste plus de dés il peut relancer les 6.\n'
      rules += 'Attention : si un joueur ne peut pas faire de points avec son lancer, il passe son tour et ne marque aucun point !\n'
      rules += 'Le premier joueur à 4000 points gagne la partie.'
      embed.add_field(name='Règles', value=rules, inline=False)
      points = 'Suite complète de 1 à 6 : 1500 pts \nSuite partielle de 2 à 6 : 750 pts\n'
      points += 'Suite partielle de 1 à 5 : 500 pts\nTriple un : 1000 pts\n'
      points += 'Triplé d\'un chiffre (sauf un) : chiffre x 100 pts\nQuadruple : le double d\'un triple\n'
      points += 'Quintuple : le double d\'un quadruple\nSextuple : double d\'un quintuple\n'
      points += 'Un : 100 pts\nCinq : 50 pts'
      embed.add_field(name='Points', value=points, inline=False)
      commandes = 'start : créé un lobby de Farkle (reset après 5 min)\n'
      commandes += 'join : rejoins un lobby de Farkle et lance la partie (durée max : 15 min)\n'
      commandes += '[score | s] a-b-...-f | "a b c f" : choisi les dés du lancer à ajouter au score\n'
      commandes += 'max | m : choisit le maximum de dés possible à ajouter au score\n'
      commandes += 'relance | r : relance les dés restants\n'
      commandes += 'passe | p : termine le tour en ajoutant les points cumulés du tour\n'
      commandes += 'reset : reset la partie si les deux joueurs tapent la commande\n'
      commandes += 'test <a-b-..-f> : donne le score que valent les dés en paramètres'
      embed.add_field(name='Options de la commande $farkle', value=commandes, inline=False)
      await context.send(embed=embed)
      return

    if arg == 'showscore':
      await show_score(context)
      return

    if arg == 'max' or arg == 'm':
      if not can_play(id):
        return
      if db['farkle_turn'] == 1:
        roll = db['farkle_player1_roll'].split()
      elif db['farkle_turn'] == 2:
        roll = db['farkle_player2_roll'].split()
      max_dices = get_max_score_roll(roll)
      score = score_from_roll(max_dices)
      db['farkle_score_temp'] += score
      #update dés restants
      if db['farkle_turn'] == 1:
        db['farkle_player1_dices'] -= len(max_dices)
        if db['farkle_player1_dices'] == 0:
          db['farkle_player1_dices'] = 6
        msg = 'Vous pouvez relancer vos ' + str(
          db['farkle_player1_dices']) + ' dés restants'
      elif db['farkle_turn'] == 2:
        db['farkle_player2_dices'] -= len(max_dices)
        if db['farkle_player2_dices'] == 0:
          db['farkle_player2_dices'] = 6
        msg = 'Vous pouvez relancer vos ' + str(
          db['farkle_player2_dices']) + ' dés restants'
  
      msg += ' ou augmenter vos points de ' + str(db['farkle_score_temp'])
      await context.send(msg)
      await context.send('Utilisez "$farkle relance" ou "$farkle passe"')
      return
      return
    

    if not can_play(id):
        return
    if arg.count('-') > 0: #a-b-c format
      choices = arg.split('-')
    else: #"a b c" format
      choices = arg.split()
    if db['farkle_turn'] == 1:
      roll = db['farkle_player1_roll'].split()
    elif db['farkle_turn'] == 2:
      roll = db['farkle_player2_roll'].split()
    test_roll = roll.copy()
    if not all(roll in test_roll for roll in choices):
      await context.send('Pas de triche !')
      return
    score = score_from_roll(choices)
    if score == -1:
      await context.send('Mauvaise saisie des dés : certains ne marquent pas de points')
      return
    db['farkle_score_temp'] += score
    #update dés restants
    if db['farkle_turn'] == 1:
      db['farkle_player1_dices'] -= len(choices)
      if db['farkle_player1_dices'] == 0:
        db['farkle_player1_dices'] = 6
      msg = 'Vous pouvez relancer vos ' + str(
        db['farkle_player1_dices']) + ' dés restants'
    elif db['farkle_turn'] == 2:
      db['farkle_player2_dices'] -= len(choices)
      if db['farkle_player2_dices'] == 0:
        db['farkle_player2_dices'] = 6
      msg = 'Vous pouvez relancer vos ' + str(
        db['farkle_player2_dices']) + ' dés restants'

    msg += ' ou augmenter vos points de ' + str(db['farkle_score_temp'])
    await context.send(msg)
    await context.send('Utilisez "$farkle relance" ou "$farkle passe"')
    return

  @commands.hybrid_command(name='reset_timer', description='commande de debug, ne pas utiliser !')
  async def reset_timer(self, context):
    self.game_timer.cancel()
    self.start_timer.cancel()


async def setup(bot):
  await bot.add_cog(Farkle(bot))
