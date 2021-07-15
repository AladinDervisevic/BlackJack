import random
import json
import hashlib

DATOTEKA_S_STANJEM = 'users.json'

START = 'start'
NEW_ROUND = 'new round'
PLAYER = 'player'
DEALER = 'dealer'
PUSH = 'push'
BLACKJACK = 'blackjack'
END = 'end'

number_kinds = [str(i) for i in range(2, 11)]
special_kinds = ['A', 'K', 'Q', 'J']

class Card:
    def __init__(self, kind, suit):
        self.showing = True
        self.kind = kind
        self.suit = suit
        self.name = f'{self.kind}' + self.suit[0]
        if kind in number_kinds:
            self.value = int(kind)
        elif kind in 'JQK':
            self.value = 10
        else:
            self.value = 11  # Ace can be worth 1 or 11

    def __repr__(self):
        if self.showing:
            return f'Card({self.kind}, {self.suit})'
        else:
            return 'Card(?)'

    def v_slovar(self):
        return {
            'showing': self.showing,
            'kind': self.kind,
            'suit': self.suit,
            'value': self.value,
        }

    @staticmethod
    def iz_slovarja(slovar):
        kind = slovar['kind']
        suit = slovar['suit']
        value = int(slovar['value'])
        showing = slovar['showing']
        card = Card(kind, suit)
        card.value = value
        card.showing = showing
        return card

class Deck:
    def __init__(self, number_of_decks, empty = False):
        self.number_of_decks = number_of_decks
        cards = []
        if not empty:
            for kind in number_kinds + special_kinds:
                for suit in ['Hearts', 'Diamonds', 'Clubs', 'Pikes']:
                    for _ in range(number_of_decks):
                        cards.append(Card(kind, suit))
            random.shuffle(cards)
        self.cards = cards

    def v_slovar(self):
        return {
            'cards': [card.v_slovar() for card in self.cards]
        }

    @staticmethod
    def iz_slovarja(slovar, number_of_decks):
        deck = Deck(number_of_decks, empty = True)
        for card_slovar in slovar['cards']:
            card = Card.iz_slovarja(card_slovar)
            deck.cards.append(card)
        return deck

class Dealer:
    def __init__(self):
        self.cards = []

    def v_slovar(self):
        return {
            'cards': [card.v_slovar() for card in self.cards], 
        }

    @staticmethod
    def iz_slovarja(slovar):
        dealer = Dealer()
        for card_slovar in slovar['cards']:
            card = Card.iz_slovarja(card_slovar)
            dealer.cards.append(card)
        return dealer

class Player:
    def __init__(self, money = 1000):
        self.cards = []
        self.saved_cards = []
        self.money = money

    def blackjack(self):
        if len(self.cards) == 2:
            return self.cards[0].value + self.cards[1].value == 21
        else:
            return False

    def valid_split(self):
        if len(self.cards) != 2:
            return False
        else:
            return self.cards[0].kind == self.cards[1].kind

    def v_slovar(self):
        return {   
            'cards': [card.v_slovar() for card in self.cards],
            'saved_cards': [card.v_slovar() for card in self.saved_cards],
            'money': self.money,
        }

    @staticmethod
    def iz_slovarja(slovar):
        player = Player()
        player.money = slovar['money']
        for card_slovar in slovar['cards']:
            card = Card.iz_slovarja(card_slovar)
            player.cards.append(card)
        for card_slovar in slovar['saved_cards']:
            card = Card.iz_slovarja(card_slovar)
            player.saved_cards.append(card)
        return player

class Game:
    def __init__(self, number_of_decks):
        self.number_of_decks = number_of_decks
        self.deck = Deck(self.number_of_decks)
        self.player = Player()
        self.dealer = Dealer()
        self.lot = 0
        self.graveyard = Deck(self.number_of_decks, empty = True)

    def __repr__(self):
        return f'Game({self.id})'

    def hand_value(self, person):
        if person == self.dealer and not person.cards[1].showing:
            return person.cards[0].value
        else:
            return sum(card.value for card in person.cards)

    def change_number_of_decks(self, number):
        self.number_of_decks = number
        self.deck = Deck(number)
        self.dealer.cards = []
        self.player.cards = []
        self.player.saved_cards = []

    def bet(self, amount:int):
        if amount <= 0:
            raise ValueError('You cannot bet non-positive amounts!')
        elif amount > self.player.money:
            raise ValueError("You don't have enough money for such a bet.")
        else:
            self.player.money -= amount
            self.lot += amount

    def bust(self, person):
        return sum(i.value for i in person.cards) > 21

    def end_round(self):
        if self.player.blackjack():
            if self.hand_value(self.dealer) == 21:
                self.player.money += self.lot
                self.lot = 0
                return PUSH
            else:
                self.player.money += (self.lot * 3)
                self.lot = 0
                return BLACKJACK
        if self.bust(self.dealer):
            self.player.money += (self.lot * 2)
            self.lot = 0
            return PLAYER
        elif self.bust(self.player):
            self.lot = 0
            return DEALER
        if self.hand_value(self.player) < self.hand_value(self.dealer):
            self.lot = 0
            return DEALER
        elif self.hand_value(self.player) > self.hand_value(self.dealer):
            self.player.money += (self.lot * 2)
            self.lot = 0
            return PLAYER
        elif self.hand_value(self.player) == self.hand_value(self.dealer):
            self.player.money += self.lot
            self.lot = 0
            return PUSH

    def hit(self):
        card = random.choice(self.deck.cards)
        self.deck.cards.remove(card)
        self.player.cards.append(card)
        if card.kind == 'A':
            self.set_ace_value(self.player, card)

    def set_ace_value(self, person, ace):
        if self.hand_value(person) > 21:
            ace.value = 1

    def stand(self):
        self.dealer.cards[1].showing = True
        while self.hand_value(self.dealer) < 17:
            card = random.choice(self.deck.cards)
            self.dealer.cards.append(card)
            if card.kind == 'A':
                self.set_ace_value(self.dealer, card)

    def double_down(self):
        self.player.money -= self.lot
        self.lot *= 2
        self.hit()
        self.stand()
        return self.end_round()

    def valid_double_down(self):
        return self.player.money >= self.lot

    def split(self):
        card = self.player.cards[1]
        self.player.cards.remove(card)
        self.player.saved_cards.append(card)
        card = random.choice(self.deck.cards)
        self.player.cards.append(card)
        self.deck.cards.remove(card)

    def deal_cards(self):
        leftover_cards = len(self.deck.cards)
        total = self.deck.number_of_decks * 52
        if leftover_cards < (total // 2):
            self.deck.cards += self.graveyard.cards
            random.shuffle(self.deck.cards)
            self.graveyard.cards = []
        self.player.cards = [] + self.player.saved_cards
        self.player.saved_cards = []
        for char in [self.player, self.dealer]:
            for i in range(2):
                card = random.choice(self.deck.cards)
                if i == 1 and char == self.dealer:
                    card.showing = False
                if char == self.player and len(char.cards) == 2:
                    continue
                self.deck.cards.remove(card)
                char.cards.append(card)

    def new_round(self):
        self.lot = 0
        for char in [self.player, self.dealer]:
            self.graveyard.cards += char.cards
            char.cards = []
        return NEW_ROUND

    def loss(self):
        return self.player.money == 0 and self.lot == 0

    def v_slovar(self):
        return {
            'deck': self.deck.v_slovar(),
            'player': self.player.v_slovar(),
            'dealer': self.dealer.v_slovar(),
            'lot': self.lot,
            'graveyard': self.graveyard.v_slovar(),
            'number_of_decks': self.number_of_decks
        }
    
    @staticmethod
    def iz_slovarja(slovar):
        number_of_decks = int(slovar['number_of_decks'])
        game = Game(number_of_decks)
        game.number_of_decks = number_of_decks
        game.deck = Deck.iz_slovarja(slovar['deck'], number_of_decks)
        game.player = Player.iz_slovarja(slovar['player'])
        game.dealer = Dealer.iz_slovarja(slovar['dealer'])
        game.lot = int(slovar['lot'])
        game.graveyard = Deck.iz_slovarja(slovar['graveyard'], number_of_decks)
        return game

class Blackjack:
    def __init__(self):
        self.games = {}
        self.high_score = 0
        self.number_of_decks = 2

    def new_id(self):
        if not self.games:
            return 0
        else:
            return max(self.games) + 1

    def new_game(self):
        id = self.new_id()
        self.games[id] = (Game(self.number_of_decks), START)
        return id

    def check_high_score(self, game):
        if game.player.money > self.high_score:
            self.high_score = game.player.money

    def v_slovar(self):
        games = {}
        for game_id in self.games:
            game, state = self.games[game_id]
            games[game_id] = {'game': game.v_slovar(), 'state': state}
        return {
            'games': games, 
            'high_score': self.high_score,
            'number_of_decks': self.number_of_decks
        }

    @staticmethod
    def iz_slovarja(slovar):
        blackjack = Blackjack()
        blackjack.high_score = slovar['high_score']
        blackjack.number_of_decks = slovar['number_of_decks']
        games_slovar = slovar['games']
        for game_id in games_slovar:
            game = Game.iz_slovarja(games_slovar[game_id]['game'])
            state = games_slovar[game_id]['state']
            blackjack.games[int(game_id)] = (game, state)
        return blackjack

class User:
    def __init__(self, username, encrypted_password, blackjack):
        self.username = username
        self.encrypted_password = encrypted_password
        self.blackjack = blackjack

    def encryt(visible_password, add = None):
        if add is None:
            add = str(random.getrandbits(16))
        encrypted_password = add + visible_password + add
        hash = hashlib.blake2b()
        hash.update(encrypted_password.encode(encoding = 'utf-8'))
        return f'{add}%{hash.hexdigest()}'

    def check_password(self, visible_password):
        add, _ = self.encrypted_password.split('%')
        return self.encrypted_password == User.encryt(visible_password, add)

    def v_slovar(self):
        return {
            self.username: {
                'username': self.username,
                'encrypted_password': self.encrypted_password,
                'blackjack': self.blackjack.v_slovar(),
            }
        }

    def save_file(self):
        with open(
            DATOTEKA_S_STANJEM, 'w', encoding = 'utf-8'
        ) as dat:
            json.dump(
                self.v_slovar(), dat, ensure_ascii = False, indent = 4
            )

    @staticmethod
    def iz_slovarja(slovar):
        username = slovar['username']
        encrypted_password = slovar['encrypted_password']
        blackjack = Blackjack.iz_slovarja(slovar['blackjack'])
        return User(username, encrypted_password, blackjack)

    @staticmethod
    def import_from_file(username):
        try:
            with open(DATOTEKA_S_STANJEM, encoding = 'utf-8') as dat:
                users = json.load(dat)
                return User.iz_slovarja(users[username])
        except KeyError:
            return None

    @staticmethod
    def login(username, visible_password):
        user = User.import_from_file(username)
        if user is None:
            raise ValueError("Username doesn't exist.")
        elif user.check_password(visible_password):
            return user
        else:
            raise ValueError('Password is incorrent.')

    @staticmethod
    def registration(username, visible_password):
        if User.import_from_file(username) is not None:
            raise ValueError('Username already exists.')
        elif len(str(visible_password)) < 3:
            raise ValueError('Password has contain at least 3 characters.')
        else:
            encrypted_password = User.encryt(str(visible_password))
            user = User(username, encrypted_password, Blackjack())
            user.save_file()
            return user