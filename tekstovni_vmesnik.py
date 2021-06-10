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

def blackjack_win():
    return 'You have won the round with a blackjack. Bonus: 100 $'

def demand_action():
    legend = f'''Hit : H
STAND = ST
SPLIT = SP
DOUBLE DOWN = DD
BET = B'''
    print(legend)
    return input('What will you do: ')

def start_interface():
    print('WELCOME TO BLACKJACK')
    while True:
        game, state = model.new_game()
        player = game.player
        print('NEW GAME\n')

        while True:
            state = game.new_round()
            print('NEW ROUND')

            if not player.blackjack():
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
                        new_card = game.player.cards[-1]
                        if new_card.kind == 'A':
                            value = input('Set value of ace to 1 or 11? ')
                            state = game.set_ace_value(value)
                    elif action == model.DOUBLE_DOWN:
                        game.double_down()
                    elif action == model.SPLIT:
                        game.split()
                    elif action == model.STAND:
                        game.stand()
                        state = game.end_round()

                print(display_game(game))
                if state == model.ROUND_WIN:
                    print(round_win())
                elif state == model.ROUND_LOSS:
                    print(round_loss())
                elif state == model.TIE:
                    print(tie())
            else:
                print(display_game(game))
                game.blackjack()
                print(blackjack_win())

            if game.win():
                state = model.WIN
                print(win(game))
                break
            elif game.loss():
                state = model.LOSS
                print(loss())
                break
            
        answer = input('Would you like to play again? ')
        if answer.lower() == 'no':
            print('GOODBYE')
            break

start_interface()