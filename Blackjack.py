# from model import User
import model
from model import PLAYER, DEALER, PUSH
import bottle

COOKIE_USERNAME = 'username'
SECRET = 'whatever lad'

blackjack = model.Blackjack()
blackjack.load_games_from_file()

#####################################################################
# Pomožne funkcije
#####################################################################

def current_game_id():
    id = bottle.request.get_cookie('game_id', secret=SECRET)
    return id

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

@bottle.post('/new_game/')
def play():
    id = blackjack.new_game()
    game, _ = blackjack.games[id]
    state = game.new_round()
    blackjack.games[id] = (game, state)
    blackjack.save_games()
    bottle.response.set_cookie('game_id', id, path='/', secret=SECRET)
    bottle.redirect('/game/')

@bottle.post('/resume/')
def resume():
    return bottle.redirect('/game/')

@bottle.get('/game/')
def game():
    id = current_game_id()
    game, state = blackjack.games[id]
    if not game.player.money and not game.lot:
        return bottle.template('end.html')
    else:
        return bottle.template(
            'game.html', game = game, mistake = None, state = state
        )

@bottle.post('/new_round/')
def new_round():
    id = current_game_id()
    game, _ = blackjack.games[id]
    state = game.new_round()
    blackjack.games[id] = (game, state)
    blackjack.save_games()
    bottle.redirect('/game/')

#####################################################################
# Settings
#####################################################################

@bottle.get('/settings/')
def settings():
    id = current_game_id()
    game, _ = blackjack.games[id]
    number = game.deck.number_of_decks
    return bottle.template('settings.html', number_of_decks = number)

@bottle.post('/number_of_decks/')
def number_of_decks():
    number = bottle.request.forms['number_of_decks']
    id = current_game_id()
    game, _ = blackjack.games[id]
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
    id = current_game_id()
    game, _ = blackjack.games[id]
    amount = bottle.request.forms['amount']
    try:
        game.bet(int(amount))
        game.deal_cards()
        blackjack.save_games()
        return bottle.redirect('/game/')
    except ValueError as e:
        return bottle.template(
            'game.html', game = game, mistake = e.args[0], state = None
        )

@bottle.post('/hit/')
def hit():
    id = current_game_id()
    game, state = blackjack.games[id]
    game.hit()
    if game.bust(game.player):
        state = DEALER
    blackjack.games[id] = (game, state)
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/double_down/')
def double_down():
    id = current_game_id()
    game, state = blackjack.games[id]
    game.double_down()
    if game.bust(game.player):
        state = DEALER
    elif game.bust(game.dealer):
        state = PLAYER
    else:
        state = PUSH
    blackjack.games[id] = (game, state)
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/split/')
def split():
    id = current_game_id()
    game, _ = blackjack.games[id]
    game.split()
    blackjack.save_games()
    return bottle.redirect('/game/')

@bottle.post('/stand/')
def stand():
    id = current_game_id()
    game, state = blackjack.games[id]
    game.stand()
    state = game.end_round()
    blackjack.games[id] = (game, state)
    blackjack.save_games()
    return bottle.redirect('/game/')

#####################################################################
# Media
#####################################################################

@bottle.get('/img/<picture>')
def show_picture(picture):
    return bottle.static_file(picture, root='img/')

#####################################################################
#####################################################################

bottle.run(reloader = True, debug = True)