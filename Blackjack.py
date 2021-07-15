from model import User
from model import DEALER, END
import bottle

COOKIE_USERNAME = 'username'
SECRET = 'wobz'

#####################################################################
# Pomožne funkcije
#####################################################################

def current_user():
    username = bottle.request.get_cookie(
        COOKIE_USERNAME, secret = SECRET
    )
    return User.import_from_file(username)

def current_game_id():
    games = current_user().blackjack.games
    if games:
        id = max(current_user().blackjack.games)
        return id
    else:
        return None

#####################################################################
# Signing in & signing up
#####################################################################

@bottle.get('/')
def initial():
    return bottle.redirect('/login/')

@bottle.get('/login/')
def login_get():
    return bottle.template('login.html', mistake = None)

@bottle.post('/login/')
def login_post():
    username = bottle.request.forms.getunicode('username')
    password = bottle.request.forms.getunicode('password')
    if not username:
        return bottle.template(
            'login.html', mistake = 'You have to enter your username!'
        )
    try:
        User.login(username, password)
        bottle.response.set_cookie(
            COOKIE_USERNAME, username, path = '/', secret = SECRET
        )
        return bottle.redirect('/main_menu/')
    except ValueError as e:
        return bottle.template(
            'login.html', mistake = e.args[0]
        )

@bottle.get('/registration/')
def registration_get():
    return bottle.template('registration.html', mistake = None)

@bottle.post('/registration/')
def registration_post():
    username = bottle.request.forms.getunicode('username')
    password = bottle.request.forms.getunicode('password')
    if not username:
        return bottle.template(
            'registration.html', mistake = 'You have to enter your username!'
        )
    try:
        User.registration(username, password)
        bottle.response.set_cookie(
            COOKIE_USERNAME, username, path = '/', secret = SECRET
        )
        return bottle.redirect('/main_menu/')
    except ValueError as e:
        return bottle.template(
            'registration.html', mistake = e.args[0]
        )

@bottle.post('/logout/')
def logout():
    bottle.response.delete_cookie(COOKIE_USERNAME, path = '/')
    return bottle.redirect('/')

#####################################################################
# Main
#####################################################################

@bottle.get('/main_menu/')
def main_menu():
    blackjack = current_user().blackjack
    return bottle.template('main_menu.html', blackjack = blackjack)

@bottle.post('/new_game/')
def play():
    user = current_user()
    blackjack = user.blackjack
    id = blackjack.new_game()
    game, _ = blackjack.games[id]
    state = game.new_round()
    blackjack.games[id] = (game, state)
    user.save_file()
    return bottle.redirect('/game/')

@bottle.post('/resume/')
def resume():
    return bottle.redirect('/game/')

@bottle.get('/game/')
def game():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, state = blackjack.games[id]
    return bottle.template(
        'game.html', game = game, mistake = None, state = state
    )

@bottle.post('/new_round/')
def new_round():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, _ = blackjack.games[id]
    state = game.new_round()
    blackjack.check_high_score(game)
    blackjack.games[id] = (game, state)
    user.save_file()
    return bottle.redirect('/game/')

#####################################################################
# Settings
#####################################################################

@bottle.get('/settings/')
def settings():
    blackjack = current_user().blackjack
    number = blackjack.number_of_decks
    return bottle.template('settings.html', number_of_decks = number)

@bottle.post('/number_of_decks/')
def number_of_decks():
    user = current_user()
    number = bottle.request.forms['number_of_decks']
    user.blackjack.number_of_decks = number
    id = current_game_id()
    if id is not None:
        game = user.blackjack.games[id][0]
        game.change_number_of_decks(number)
    user.save_file()
    return bottle.redirect('/settings/')

@bottle.get('/back_from_settings/')
def go_back_from_settings():
    return bottle.redirect('/main_menu/')

#####################################################################
# About
#####################################################################

@bottle.get('/about/')
def about():
    return bottle.template('about.html')

@bottle.get('/back_from_about/')
def go_back_from_about():
    return bottle.redirect('/main_menu/')

#####################################################################
# Game moves
#####################################################################

@bottle.post('/bet/')
def bet():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, _ = blackjack.games[id]
    amount = bottle.request.forms['amount']
    try:
        game.bet(int(amount))
        game.deal_cards()
        user.save_file()
        return bottle.redirect('/game/')
    except ValueError as e:
        return bottle.template(
            'game.html', game = game, mistake = e.args[0], state = None
        )

@bottle.post('/hit/')
def hit():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, state = blackjack.games[id]
    game.hit()
    if game.bust(game.player):
        state = game.end_round()
    if game.loss():
        state = END
    blackjack.games[id] = (game, state)
    user.save_file()
    return bottle.redirect('/game/')

@bottle.post('/double_down/')
def double_down():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, _ = blackjack.games[id]
    state = game.double_down()
    if game.loss():
        state = END
    blackjack.games[id] = (game, state)
    user.save_file()
    return bottle.redirect('/game/')

@bottle.post('/split/')
def split():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, _ = blackjack.games[id]
    game.split()
    user.save_file()
    return bottle.redirect('/game/')

@bottle.post('/stand/')
def stand():
    user = current_user()
    blackjack = user.blackjack
    id = current_game_id()
    game, _ = blackjack.games[id]
    game.stand()
    state = game.end_round()
    if game.loss():
        state = END
    blackjack.games[id] = (game, state)
    user.save_file()
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