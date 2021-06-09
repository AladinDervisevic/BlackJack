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
    game = model.new_game()

    while True:
        game.new_round()
        print(display_game(game))

        action = demand_action()
        if action == 'H':
            game.hit()
        elif action == 'ST':
            game.stand()
        elif action == 'SP':
            game.split()
        elif action == 'SU':
            game.surrender()
        elif action == 'DD':
            game.double_down()
        elif action == 'B':
            amount = input('How much? ')
            game.bet(amount)
        else:
            print('Faulty input.')
        
        game.end_round()