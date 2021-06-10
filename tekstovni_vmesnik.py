import model

def display_game(game):
    return f'''
Dealer's cards: {game.dealer.cards}
LOT: {game.lot}
Your cards: {game.player.cards}'''

def print_win(game):
    return f'You won and earned {game.player.money} $.'

def print_loss():
    return 'You are out of money. Better luck next time.'

def demand_action():
    legend = f'''Hit : H
STAND = ST
SPLIT = SP
SURRENDER = SU
DOUBLE DOWN = DD
BET = B'''
    print(legend)
    return input('What will you do: ')

def start_interface():
    game, state = model.new_game()

    while True:
        game.new_round()

        while state not in [model.ROUND_WIN, model.ROUND_LOSS, model.TIE, model.BUST]:
            print(display_game(game))

            action = demand_action()
            while action not in model.ACTIONS:
                print('Faulty input.')
                action = demand_action()

            if action == model.BET:
                amount = input('How much? ')
                state = game.bet(amount)
            elif action == model.HIT:
                state = game.hit()
                if state == model.ACE:
                    value = input('Set value of ace to 1 or 11? ')
                    state = game.set_ace_value(value)
            elif action == model.STAND:
                state = game.stand()
            else:
                state = game.action(action)


start_interface()