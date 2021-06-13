import random
import json
import hashlib

START = 'P'
END = 'E'
WIN = 'W'
LOSS = 'L'
ROUND_WIN = 'RW'
ROUND_LOSS = 'RL'
TIE = 'T'
BUST = 'BU'
NEW_ROUND = 'NR'
HIT = 'H'
STAND = 'ST'
SPLIT = 'SP'
DOUBLE_DOWN = 'DD'
BET = 'B'
MOVES = f'''H) Hit
ST) Stand
SP) Split
D) Double down
B) Bet
E) End game'''

ACTIONS = [BET, HIT, STAND, SPLIT, DOUBLE_DOWN, END]
RESULTS = [ROUND_WIN, ROUND_LOSS, TIE, BUST, END]

class Card:
    def __init__(self, kind, suit):
        self.showing = True
        self.kind = kind
        self.suit = suit
        if kind in list(str(i) for i in range(2, 11)):
            self.value = int(kind)
        elif kind in 'JQK':
            self.value = 10
        else:
            self.value = 11  # Ace can be worth 1 or 11

    def __repr__(self):
        if self.showing:
            if self.kind in 'A':
                return f'Card({self.kind} = {self.value}, {self.suit})'
            else:
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
    def __init__(self, empty = ''):
        cards = []
        if not empty:
            for kind in [str(i) for i in range(2, 11)] + ['A', 'J', 'Q', 'K']:
                for suit in ['Hearts', 'Diamonds', 'Clubs', 'Pikes']:
                    for _ in range(2):
                        cards.append(Card(kind, suit))
            random.shuffle(cards)
        self.cards = cards

    def v_slovar(self):
        return {'cards': [card.v_slovar() for card in self.cards]}

    @staticmethod
    def iz_slovarja(slovar):
        deck = Deck('empty')
        for card_slovar in slovar['cards']:
            card = Card.iz_slovarja(card_slovar)
            deck.cards.append(card)
        return deck

def hand_value(cards):
    return sum(card.value for card in cards)

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
        assert len(self.cards) == 2
        return self.cards[0].value + self.cards[1].value == 21

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
        self.graveyard = Deck('empty')

    def __repr__(self):
        return f'Game({self.id})'

    def bet(self, amount):
        if amount <= self.player.money:
            self.player.money -= amount
            self.lot += amount
            return BET
        else:
            return 'Nimaš dovolj denarja za tolikšno stavo.'

    def stand(self):
        self.dealer.cards[1].showing = True
        while hand_value(self.dealer.cards) < 17:
            card = random.choice(self.deck.cards)
            self.dealer.cards.append(card)
            if card.kind == 'A' and hand_value(self.dealer.cards) > 21:
                card.value = 1

    def bust(self):
        return sum(i.value for i in self.player.cards) > 21

    def end_round(self):
        if hand_value(self.dealer.cards) > 21:
            self.player.money += (self.lot * 2)
            self.lot = 0
            return ROUND_WIN
        elif hand_value(self.player.cards) > 21:
            self.lot = 0
            return ROUND_LOSS
        if hand_value(self.player.cards) < hand_value(self.dealer.cards):
            self.lot = 0
            return ROUND_LOSS
        elif hand_value(self.player.cards) > hand_value(self.dealer.cards):
            self.player.money += (self.lot * 2)
            self.lot = 0
            return ROUND_WIN
        elif hand_value(self.player.cards) == hand_value(self.dealer.cards):
            self.player.money += self.lot
            self.lot = 0
            return TIE

    def hit(self, double_down = False):
        card = random.choice(self.deck.cards)
        self.deck.cards.remove(card)
        self.player.cards.append(card)
        if card.kind == 'A':
            self.set_ace_value(card)
        if self.bust():
            return BUST
        elif double_down:
            return DOUBLE_DOWN
        else:
            return HIT

    def set_ace_value(self, ace):
        if hand_value(self.player.cards) > 21:
            ace.value = 1

    def double_down(self):
        self.player.money -= self.lot
        self.lot *= 2
        self.hit(True)
        self.stand()

    def split(self):
        card = self.player.cards[1]
        self.player.cards.remove(card)
        self.player.saved_cards.append(card)
        card = random.choice(self.deck.cards)
        self.player.cards.append(card)
        self.deck.cards.remove(card)

    def deal_cards(self):
        if len(self.deck.cards) < 25:
            self.deck.cards += self.graveyard.cards
            random.shuffle(self.deck.cards)
            self.graveyard.cards = []
        if self.player.cards:  #if players currently hold some cards
            self.graveyard.cards += self.dealer.cards
            self.graveyard.cards += self.player.cards
            self.dealer.cards = []
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
        self.deal_cards()
        return NEW_ROUND

    def blackjack(self):
        self.player.money += (self.lot + 100)
        self.lot = 0

    def loss(self):
        return self.player.money <= 0

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
        self.game = None
        self.state = None

    def __repr__(self):
        return 'Blackjack()'

    def new_game(self):
        return Game(), START

    def v_dvojico(self):
        return (self.game.v_slovar(), self.state)

    @staticmethod
    def iz_dvojice(dvojica):
        blackjack = Blackjack()
        blackjack.game, blackjack.state = dvojica
        return blackjack

#    def save_games_on_file(self, file_name):
#        with open(file_name, 'w', encoding = 'utf-8') as dat:
#            json.dump(self.v_dvojico(), dat, ensure_ascii = False, indent = 4)
#
#    @staticmethod
#    def load_games_from_file(file_name):
#        with open(file_name, 'r', encoding = 'utf-8') as dat:
#            dvojica = json.load(dat)
#        return Blackjack.iz_dvojice(dvojica)