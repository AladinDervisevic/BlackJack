from model import Blackjack
from colorama import Fore, Style
import model
import colorama

colorama.init(autoreset = True)

DATOTEKA_S_STANJEM = 'stanje.json'

try:
    blackjack = Blackjack.load_games_from_file(DATOTEKA_S_STANJEM)
except FileNotFoundError:
    blackjack = Blackjack()

##################################################################
# Functions for displaying the game.
##################################################################

def bold(text):
    return Style.BRIGHT + f"\033[1m{text}\033[0m"

def good(text):
    return Style.BRIGHT + Fore.GREEN + text

def bad(text):
    return Style.BRIGHT + Fore.RED + text

def neutral(text):
    return Style.BRIGHT + Fore.CYAN + text

def display_cards(cards):
    string = ''
    for card in cards:
        string += (repr(card) + ' ')
    return string.strip()

def display_game(game):
    return f'''Dealer's cards: {display_cards(game.dealer.cards)}
Dealer's balance: {game.dealer.money} $
LOT: {game.lot} $
Your cards: {display_cards(game.player.cards)}
Your balance: {game.player.money} $'''

def win(game):
    return good(f'YOU HAVE WON WITH END BALANCE {game.player.money} $.')

def loss():
    return bad('YOU ARE OUT OF MONEY, BETTER LUCK NEXT TIME.')

def round_win():
    return good('You have won the round.')

def round_loss():
    return bad('You have lost the round.')

def tie():
    return neutral("It's a tie.")

def bust():
    return bad("You're over 21. It's a bust.")

def blackjack_win():
    return good('You have won the round with a blackjack. Bonus: 100 $')

def pause():
    return input('To continue press ENTER.')

##################################################################
# Entry functions
##################################################################

def demand_action():
    print()
    print(neutral(('What would you like to do?')))
    print(model.MOVES)
    action = input().upper()
    while action not in model.ACTIONS:
        print()
        print(bad('FAULTY INPUT'))
        print(neutral(('What would you like to do?')))
        action = input().upper()
    return action

def set_ace_value(game):
    while True:
        print(neutral('Set value of ace to 1 or 11? '))
        value = input()
        if value == '1' or value == '11':
            break
        print(bad('FAULTY INPUT'))
    return game.set_ace_value(int(value))

##################################################################
# Executional functions 
##################################################################

def valid_split(game):
    if len(game.player.cards) != 2:
        print(bad("You cannot split once you have more than 2 cards."))
        return False
    elif game.player.cards[0].kind != game.player.cards[1].kind:
        print(bad("You cannot split since your cards are not of the same kind."))
        return False
    elif game.player.saved_cards:
        print(bad("You cannot double split."))
        return False
    return True

def is_ace(card):
    return card.kind == 'A'

def execute(action, game = None):
    if action == model.BET:
        amount = int(input('How much? '))
        game.bet(amount)
    elif action == model.HIT:
        state, new_card = game.hit()
        if is_ace(new_card):
            print(display_game(game))
            state = set_ace_value(game)
        return state
    elif action == model.DOUBLE_DOWN:
        game.double_down()
        return game.end_round()
    elif action == model.SPLIT and valid_split(game):
        game.split()
    elif action == model.STAND:
        game.stand()
        return game.end_round()
    elif action == model.END:
        return model.END

def new_round(game):
    print(neutral('NEW ROUND'))
    return game.new_round()

def last_game(blackjack):
    if blackjack.games == {}:
        return blackjack.new_game()
    else:
        last_game_id = max(blackjack.games)
        return blackjack.games[last_game_id]

##################################################################
# TEXTUAL INTERFACE
##################################################################

def start_interface():
    greeting()
    game, state = last_game(blackjack)
    while True:
        while True:
            state = new_round(game)
            if not game.player.blackjack():
                while state not in model.RESULTS:
                    print()
                    print(display_game(game))
                    action = demand_action()
                    state = execute(action, game)
                if state == model.END:
                    break
                print()
                print(display_game(game))
                if state == model.ROUND_WIN:
                    print(round_win())
                elif state == model.ROUND_LOSS:
                    print(round_loss())
                elif state == model.TIE:
                    print(tie())
                elif state == model.BUST:
                    print(bust())
                game.end_round()
            else:
                print()
                print(display_game(game))
                game.blackjack()
                print(blackjack_win())
            if game.win():
                print(win(game))
                break
            elif game.loss():
                print(loss())
                break
            print()
            print(pause())
        if state == model.END:
            print()
            goodbye()
            blackjack.save_games_on_file(DATOTEKA_S_STANJEM)
            break
        print()
        print(
            ''''Would you like to play again?'
            1) YES
            2) NO'''
            )
        answer = input('Answer: ')
        while answer not in '12':
            print(bad('FAULTY INPUT'))
            print()
            answer = input('Answer: ')
        if answer == '2':
            blackjack.save_games_on_file(DATOTEKA_S_STANJEM)
            print()
            print(neutral('Saving game...'))
            goodbye()
            break
        elif answer == '2':
            game, state = blackjack.new_game()

def greeting():
    print(neutral(bold('GREETINGS!')))
    input('To start playing, press ENTER')
    print()

def goodbye():
    print(neutral(bold('GOODBYE!')))


start_interface()