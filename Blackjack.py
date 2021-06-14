from sys import winver
from threading import Semaphore
from model import User, PLAYER, DEALER, PUSH
import bottle

COOKIE_USERNAME = 'username'
SECRET = 'whatever lad'

#####################################################################
# Pomožne funkcije
#####################################################################

def current_user():
    username = bottle.request.get_cookie(
        COOKIE_USERNAME, secret = SECRET
    )
    if username:
        return User.iz_datoteke(username)
    else:
        bottle.redirect('login')

def save_state(user):
    user.v_datoteko()

#####################################################################
#####################################################################

@bottle.get('/')
def start():
    bottle.redirect('/main_menu/')

#####################################################################
# Signing in & signing up
#####################################################################

@bottle.get('/registration/')
def registration_get():
    return bottle.template('registration.html', mistake = None)

@bottle.post('registration')
def registration_post():
    username = bottle.request.forms.getunicode('username')
    password = bottle.request.forms.getunicode('password')
    if not username:
        return bottle.template(
            'registration.html', mistake = 'Enter username!'
        )
    try:
        User.registration(username, password)
        bottle.response.set_cookie(
            COOKIE_USERNAME, username, path = '/', secret = SECRET
        )
        bottle.redirect('/')
    except ValueError as e:
        return bottle.template(
            'registration.html', mistake = e.args[0]
        )

@bottle.get('/login/')
def login_get():
    return bottle.template('login.html', mistake = None)

@bottle.post('/login/')
def login_post():
    username = bottle.request.forms.getunicode('username')
    password = bottle.request.forms.getunicode('password')
    if not username:
        return bottle.template('login.html', mistake = 'Enter username!')
    try:
        User.login(username, password)
        bottle.response.set_cookie(
            COOKIE_USERNAME, username, path = '/', secret = SECRET
        )
        bottle.redirect('/')
    except ValueError as e:
        return bottle.template(
            'login.html', mistake = e.args[0]
        )

@bottle.post('logout')
def logout():
    bottle.response.delete_cookie(COOKIE_USERNAME, path = '/')
    bottle.redirect('/')

#####################################################################
# Main menu
#####################################################################

@bottle.get('/main_menu/')
def main_menu():
    return bottle.template('main_menu.html')

@bottle.get('/play/')
def play():
    return bottle.template('play.html')

@bottle.post('/new_game/')
def new_game():
    user = current_user()
    user.game.reset()
    bottle.redirect('/game/')

@bottle.get('/resume/')
def resume():
    bottle.redirect('/game/')

@bottle.get('/back_from_play/')
def go_back_from_play():
    bottle.redirect('/')

#####################################################################
# Settings
#####################################################################

@bottle.get('/settings/')
def settings():
    return bottle.template('settings.html')

@bottle.post('/number_of_decks/')
def number_of_decks():
    number = bottle.request.forms['number_of_decks']
    user = current_user()
    user.blackjack.game.deck.change_number_of_decks(number)
    bottle.redirect('/settings/')

@bottle.get('/back_from_settings/')
def go_back_from_settings():
    bottle.redirect('main_menu')

#####################################################################
# Game
#####################################################################

@bottle.get('/game/')
def game():
    game = current_user().game
    return bottle.template('game', game = game)

@bottle.post('/bet/amount:int')
def bet(amount):
    user = current_user()
    user.game.bet(amount)
    bottle.redirect('/game/')

@bottle.post('/hit/')
def hit():
    game = current_user().game
    game.hit()
    if game.bust(game.player):
        bottle.redirect('/bust/')
    else:
        bottle.redirect('/game/')

@bottle.get('/bust/')
def bust():
    game = current_user().game
    return bottle.template('game', game = game, bust = True)

@bottle.post('double_down')
def double_down():
    user = current_user()
    user.game.double_down()
    bottle.redirect('/game/')

@bottle.post('/split/')
def split():
    user = current_user()
    user.game.split()
    bottle.redirect('/game/')

@bottle.post('/stand/')
def stand():
    user = current_user()
    user.game.stand()
    winner = user.game.end_round()
    bottle.redirect('/end_round/<winner>/')

@bottle.get('/end_round/<winner>')
def end_round(winner):
    game = current_user().game
    return bottle.template('game.html', game = game, winner = winner)

#####################################################################
#####################################################################

bottle.run(reloader = True, debug = True)