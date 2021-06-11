import model

def display_game(game):
    return f'''\nDealer's cards: {game.dealer.cards}
Dealer's balance: {game.dealer.money} $
LOT: {game.lot} $
Your cards: {game.player.cards}
Your balance: {game.player.money} $'''

def win(game):
    return f'\nYOU HAVE WON AND EARNED {game.player.money} $.'

def loss():
    return '\nYOU ARE OUT OF MONEY, BETTER LUCK NEXT TIME.'

def round_win():
    return 'You have won the round.'

def round_loss():
    return 'You have lost the round.'

def tie():
    return "It's a tie."

def bust():
    return "You're over 21. It's a bust."

def blackjack_win():
    return 'You have won the round with a blackjack. Bonus: 100 $'

def end_round():
    return input('To continue press ENTER.')

def demand_action():
    print(model.legend)
    action = input('What will you do: ').upper()
    while action not in model.ACTIONS:
        print('\nFAULTY INPUT')
        action = input('What will you do: ').upper()
    return action

def set_ace_value(game):
    value = int(input('Set value of ace to 1 or 11? '))
    return game.set_ace_value(value)

def is_ace(card):
    return card.kind == 'A'

def valid_split():
    if len(player.cards) != 2:
        print("You cannot split once you have more than 2 cards.")
        return False
    elif player.cards[0].kind != player.cards[1].kind:
        print("You cannot split since your cards are not of the same kind.")
        return False
    elif player.saved_cards:
        print("You cannot double split.")
        return False
    return True

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
    elif action == model.SPLIT and valid_split():
        game.split()
    elif action == model.STAND:
        game.stand()
        return game.end_round()

def start_interface():
    while True:
        game, state = model.new_game()
        player = game.player
        print('NEW GAME')

        while True:
            state = game.new_round()
            print('\nNEW ROUND')
            if not player.blackjack():
                while state not in [model.ROUND_WIN, model.ROUND_LOSS, model.TIE, model.BUST]:
                    print(display_game(game))
                    action = demand_action()
                    state = execute(action, game)
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
            end_round()

            if game.win():
                print(win(game))
                break
            elif game.loss():
                print(loss())
                break
            
        answer = input('Would you like to play again? ')
        if answer.lower() == 'no':
            print('GOODBYE')
            break

start_interface()