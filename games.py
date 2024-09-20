import random

class Game:
    @staticmethod
    async def play(game_type, user_choice=None):
        if game_type == "rps":
            return await RockPaperScissors.play(user_choice)
        elif game_type == "coin_flip":
            return await CoinFlip.play(user_choice)
        elif game_type == "dice_roll":
            return await DiceRoll.play()

class RockPaperScissors:
    @staticmethod
    async def play(user_choice):
        choices = ['rock', 'paper', 'scissors']
        bot_choice = random.choice(choices)
        
        if user_choice == bot_choice:
            return 'draw', bot_choice, 0
        elif (user_choice == 'rock' and bot_choice == 'scissors') or \
             (user_choice == 'scissors' and bot_choice == 'paper') or \
             (user_choice == 'paper' and bot_choice == 'rock'):
            return 'win', bot_choice, 5
        else:
            return 'lose', bot_choice, 0

class CoinFlip:
    @staticmethod
    async def play(user_choice):
        result = random.choice(['heads', 'tails'])
        if user_choice == result:
            return 'win', result, 3
        else:
            return 'lose', result, 0

class DiceRoll:
    @staticmethod
    async def play():
        roll = random.randint(1, 6)
        if roll > 3:
            return 'win', roll, roll
        else:
            return 'lose', roll, 0
