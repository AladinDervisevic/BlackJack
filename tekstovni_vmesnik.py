import model

def display_game(game):
    return f'''
Dealer's cards: {game.dealer.cards}
Dealer's balance: {game.dealer.money} $
LOT: {game.lot} $
Your cards: {game.player.cards}
Your balance: {game.player.money} $'''

def win(game):
    return f'You won and earned {game.player.money} $.'

def loss():
    return 'You are out of money. Better luck next time.'

def round_win():
    return 'You have won the round.'

def round_loss():
    return 'You have lost the round.'

def tie():
    return "It's a tie."

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
        print(game.new_round())

        while state not in [model.ROUND_WIN, model.ROUND_LOSS, model.TIE, model.BUST]:
            print(display_game(game))

            action = demand_action()
            while action not in model.ACTIONS:
                print('Faulty input.')
                action = demand_action()

            if action == model.BET:
                amount = int(input('How much? '))
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

        if state == model.ROUND_WIN:
            print(round_win())
        elif state == model.ROUND_LOSS:
            print(round_loss())
        elif state == model.TIE:
            print(tie())

        if game.win():
            state = model.WIN
            print(win(game))
            break
        elif game.loss():
            state = model.LOSS
            print(loss())
            break

start_interface()