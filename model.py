import random
import json
import hashlib

DATOTEKA_S_STANJEM = 'stanje.json'

START = 'start'
NEW_ROUND = 'new round'
PLAYER = 'player'
DEALER = 'dealer'
PUSH = 'push'
BLACKJACK = 'blackjack'

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
        showing = slovar['showing']
        value = int(slovar['value'])
        card = Card(kind, suit)
        card.value = value
        return card

class Deck:
    def __init__(self, number_of_decks = 2, empty = False):
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
    def iz_slovarja(slovar):
        deck = Deck(empty = True)
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
    def __init__(self):
        self.deck = Deck()
        self.player = Player()
        self.dealer = Dealer()
        self.lot = 0
        self.graveyard = Deck(empty = True)

    def __repr__(self):
        return f'Game({self.id})'

    def hand_value(self, person):
        if person == self.dealer and not person.cards[1].showing:
            return person.cards[0].value
        else:
            return sum(card.value for card in person.cards)

    def change_number_of_decks(self, number):
        self.deck = Deck(number_of_decks = number)
        for cards in [self.dealer.cards, self.player.cards]:
            for card in cards:
                self.deck.cards.remove(card)
        for card in self.graveyard:
            self.deck.cards.remove(card)

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
        return self.player.money == 0

    def v_slovar(self):
        return {
            'deck': self.deck.v_slovar(),
            'player': self.player.v_slovar(),
            'dealer': self.dealer.v_slovar(),
            'lot': self.lot,
            'graveyard': self.graveyard.v_slovar(),
        }
    
    @staticmethod
    def iz_slovarja(slovar):
        game = Game()
        game.deck = Deck.iz_slovarja(slovar['deck'])
        game.player = Player.iz_slovarja(slovar['player'])
        game.dealer = Dealer.iz_slovarja(slovar['dealer'])
        game.lot = int(slovar['lot'])
        game.graveyard = Deck.iz_slovarja(slovar['graveyard'])
        return game

class Blackjack:
    def __init__(self):
        self.games = {}

    def new_id(self):
        if not self.games:
            return 0
        else:
            return max(self.games) + 1

    def new_game(self):
        id = self.new_id()
        self.games[id] = (Game(), START)
        return id

    def save_games(self):
        games = {}
        for id in self.games:
            game, state = self.games[id]
            games[id] = {'game': game.v_slovar(), 'state': state}
        with open(DATOTEKA_S_STANJEM, 'w', encoding='utf-8') as dat:
            json.dump(games, dat, indent=4)

    def load_games_from_file(self):
        with open(DATOTEKA_S_STANJEM, encoding='utf-8') as dat:
            igre_slovar = json.load(dat)
        for id in igre_slovar:
            game = Game.iz_slovarja(igre_slovar[id]['game'])
            state = igre_slovar[id]['state']
            self.games[int(id)] = (game, state)

# class User:
#     def __init__(self, username, encrypted_password, game):
#         self.username = username
#         self.encrypted_password = encrypted_password
#         self.game = game
# 
#     @staticmethod
#     def login(username, visible_password):
#         user = User.iz_datoteke(username)
#         if user is None:
#             raise ValueError("Username doesn't exist.")
#         elif user.check_password(visible_password):
#             return user
#         else:
#             raise ValueError('Password is incorrent.')
# 
#     @staticmethod
#     def registration(username, visible_password):
#         if User.iz_datoteke(username) is not None:
#             raise ValueError('Username already exists.')
#         else:
#             encrypted_password = User.encryt(visible_password)
#             user = User(username, encrypted_password, Game())
#             user.v_datoteko()
#             return user
# 
#     def encryt(visible_password, add = None):
#         if add is None:
#             add = str(random.getrandbits(16))
#         encrypted_password = add + visible_password + add
#         hash = hashlib.blake2b()
#         hash.update(encrypted_password.encode(encoding = 'utf-8'))
#         return f'{add}%{hash.hexdigest()}'
# 
#     def check_password(self, visible_password):
#         add, _ = self.encrypted_password.split('%')
#         return self.encrypted_password == User.encryt(visible_password, add)
# 
#     def v_slovar(self):
#         return {
#             self.username: {
#                 'username': self.username,
#                 'encrypted_password': self.encrypted_password,
#                 'game': self.game.v_slovar(),
#             }
#         }
# 
#     @staticmethod
#     def iz_slovarja(slovar):
#         username = slovar['username']
#         encrypted_password = slovar['encrypted_password']
#         game = Game.iz_slovarja(slovar['game'])
#         return User(username, encrypted_password, game)
# 
#     def v_datoteko(self):
#         with open(
#             DATOTEKA_S_STANJEM, 'w', encoding = 'utf-8'
#             ) as dat:
#             json.dump(self.v_slovar(), dat, ensure_ascii = False, indent = 4)
# 
#     @staticmethod
#     def iz_datoteke(username):
#         try:
#             with open(DATOTEKA_S_STANJEM, encoding = 'utf-8') as dat:
#                 slovar = json.load(dat)
#             return User.iz_slovarja(slovar[username])
#         except KeyError:
#             return None