from model import Blackjack
from colorama import Fore, Back, Style
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
    return f'''\nDealer's cards: {display_cards(game.dealer.cards)}
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

def end_round():
    return input('To continue press ENTER.')

##################################################################
# Functions for input
##################################################################

def demand_action():
    print()
    print(model.MOVES)
    action = input('What will you do: ').upper()
    while action not in model.ACTIONS:
        print('\nFAULTY INPUT')
        action = input('What will you do: ').upper()
    return action

def set_ace_value(game):
    while True:
        value = input('Set value of ace to 1 or 11? ')
        if value == '1' or value == '11':
            break
        print(bad('FAULTY INPUT'))
    return game.set_ace_value(int(value))

##################################################################
# Executional functions 
##################################################################

def valid_split(game):
    if len(game.player.cards) != 2:
        print("You cannot split once you have more than 2 cards.")
        return False
    elif game.player.cards[0].kind != game.player.cards[1].kind:
        print("You cannot split since your cards are not of the same kind.")
        return False
    elif game.player.saved_cards:
        print("You cannot double split.")
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

##################################################################
# TEXTUAL INTERFACE
##################################################################

def start_interface():
    greeting()
    while True:
        game, state = blackjack.new_game()
        while True:
            state = new_round(game)
            if not game.player.blackjack():
                while state not in model.RESULTS:
                    print(display_game(game))
                    action = demand_action()
                    state = execute(action, game)
                if state == model.END:
                    break
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
            print(end_round())
        if state == model.END:
            print()
            goodbye()
            blackjack.save_games_on_file(DATOTEKA_S_STANJEM)
            break
        print()
        answer = input('Would you like to play again? ')
        if answer.lower() == 'no':
            blackjack.save_games_on_file(DATOTEKA_S_STANJEM)
            print()
            goodbye()
            break

def greeting():
    print(neutral(bold('GREETINGS!')))
    input('To start playing, press ENTER')
    print()

def goodbye():
    print(neutral(bold('GOODBYE!')))


start_interface()