# from model import User
import model
from model import BUST, PLAYER, DEALER, PUSH, START, NEW_ROUND
import bottle

COOKIE_USERNAME = 'username'
SECRET = 'whatever lad'

blackjack = model.Blackjack()
blackjack.load_games_from_file()

#####################################################################
# Pomožne funkcije
#####################################################################

def current_game():
    id = bottle.request.get_cookie('game_id', secret=SECRET)
    game, state = blackjack.games[id]
    return (game, state)

#####################################################################
# Signing in & signing up
#####################################################################

# @bottle.get('/registration/')
# def registration_get():
#     return bottle.template('registration.html', mistake = None)
# 
# @bottle.post('/registration/')
# def registration_post():
#     username = bottle.request.forms.getunicode('username')
#     password = bottle.request.forms.getunicode('password')
#     if not username:
#         return bottle.template(
#             'registration.html', mistake = 'You have to enter your username!'
#         )
#     try:
#         User.registration(username, password)
#         bottle.response.set_cookie(
#             COOKIE_USERNAME, username, path = '/', secret = SECRET
#         )
#         return bottle.redirect('/main_menu/')
#     except ValueError as e:
#         return bottle.template(
#             'registration.html', mistake = e.args[0]
#         )
# 
# @bottle.get('/login/')
# def login_get():
#     return bottle.template('login.html', mistake = None)
# 
# @bottle.post('/login/')
# def login_post():
#     username = bottle.request.forms.getunicode('username')
#     password = bottle.request.forms.getunicode('password')
#     if not username:
#         return bottle.template(
#             'login.html', mistake = 'You have to enter your username!'
#         )
#     try:
#         User.login(username, password)
#         bottle.response.set_cookie(
#             COOKIE_USERNAME, username, path = '/', secret = SECRET
#         )
#         return bottle.redirect('/main_menu/')
#     except ValueError as e:
#         return bottle.template(
#             'login.html', mistake = e.args[0]
#         )
# 
# @bottle.post('logout')
# def logout():
#     bottle.response.delete_cookie(COOKIE_USERNAME, path = '/')
#     return bottle.redirect('/')

#####################################################################
# Main
#####################################################################

@bottle.get('/')
def start():
    return bottle.template('start.html')

@bottle.post('/play/')
def play():
    id = blackjack.new_game()
    blackjack.save_games()
    bottle.response.set_cookie('game_id', id, path='/', secret=SECRET)
    return bottle.redirect('/game/')

@bottle.get('/game/')
def game():
    game, state = current_game()
    if state == START:
        state = game.new_round()
        blackjack.save_games()
    return bottle.template('game', game = game, winner = None)

#####################################################################
# Settings
#####################################################################

@bottle.get('/settings/')
def settings():
    game, _ = current_game()
    num = game.deck.number_of_decks
    return bottle.template('settings.html', number_of_decks = num)

@bottle.post('/number_of_decks/')
def number_of_decks():
    number = bottle.request.forms['number_of_decks']
    game, _ = current_game()
    game.deck.change_number_of_decks(number)
    blackjack.save_games()
    return bottle.redirect('/settings/')

@bottle.get('/back_from_settings/')
def go_back_from_settings():
    return bottle.redirect('/')

#####################################################################
# Game moves
#####################################################################

@bottle.post('/bet/')
def bet():
    game, state = current_game()
    amount = bottle.request.forms['amount']
    game.bet(int(amount))
    state = game.deal_cards()
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/hit/')
def hit():
    game, _ = current_game()
    game.hit()
    if game.bust(game.player):
        state, winner = BUST, DEALER
        blackjack.save_games()
        return bottle.redirect('/end_round/<winner>')
    else:
        blackjack.save_games()
        return bottle.redirect('/game/')

@bottle.post('double_down')
def double_down():
    game, _ = current_game()
    game.double_down()
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/split/')
def split():
    game, _ = current_game()
    game.split()
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/stand/')
def stand():
    game, _ = current_game()
    game.stand()
    winner = game.end_round()
    blackjack.save_games()
    return bottle.redirect('/end_round/<winner>')

@bottle.get('/end_round/<winner>')
def end_round(winner):
    game, _ = current_game()
    return bottle.template('game.html', game = game, winner = winner)

#####################################################################
# Media
#####################################################################

@bottle.get('/img/<picture>')
def show_picture(picture):
    return bottle.static_file(picture, root='img/')

#####################################################################
#####################################################################

bottle.run(reloader = True, debug = True)