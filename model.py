import random

WIN = 'W'
LOSS = 'L'
PLAYING = 'P'
HIT = 'H'
STAND = 'ST'
SPLIT = 'SP'
DOUBLE_DOWN = 'DD'
SURENDER = 'SU'
BET = 'B'

class Card:
    def __init__(self, kind, suit):
        self.showing = True
        self.kind = kind
        self.suit = suit
        if kind in range(2, 11):
            self.value = kind
        elif kind in 'JQK':
            self.value = 10
        else:
            self.value = 11  # Ace can be worth 1 or 11

    def __str__(self):
        return f'{self.kind} {self.suit}'

    def __repr__(self):
        return f'Card({self.kind},{self.suit})'

def new_deck():
    deck = []
    for kind in list(range(2, 11)) + ['A', 'J', 'Q', 'K']:
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Pikes']:
            deck.append(Card(kind, suit))
    return deck

class Dealer:
    def __init__(self):
        self.cards = []
        self.money = 1000

class Player:
    def __init__(self, name = '1'):
        self.money = 1000
        self.cards = []
        self.name = name
        self.saved_cards = []

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Player({self.name})'

class Game:
    def __init__(self):
        self.deck = new_deck()
        self.player = Player()
        self.dealer = Dealer()
        self.lot = 0
        self.graveyard = []

    def __repr__(self):
        return 'Game()'

    def bet(self, amount):
        if amount >= self.player.money:
            self.player.money -= amount
            self.lot += amount
            if amount > self.dealer.money:
                self.lot += self.dealer.money
                self.dealer.money = 0
            else:
                self.lot += amount
                self.dealer.money -= amount
        else:
            return 'Nimaš dovolj denarja za tolikšno stavo.'

    def stand(self):
        pass

    def hit(self):
        card = random.choice(self.deck)
        self.deck.remove(card)
        self.player.cards.append(card)

    def double_down(self):
        pass

    def split(self):
        pass

    def surrender(self):
        pass

    def deal_cards(self):
        if bool(self.graveyard):  #if players currently hold some cards
            self.graveyard.append(i for i in self.dealer.cards)
            self.dealer.cards = []
            self.graveyard.append(i for i in self.player.cards)
            self.player.cards = self.player.saved_cards
        for char in [self.player, self.dealer]:
            for i in range(2):
                card = random.choice(self.deck)
                if i == 1 and char == self.dealer:
                    card.showing = False
                self.deck.remove(card)
                char.cards.append(card)

    def new_round(self):
        self.lot += 20
        self.dealer.money -= 10
        self.player.money -= 10
        self.deal_cards()

    def win(self):
        return self.dealer.money <= 0

    def loss(self):
        return self.player.money <= 0

    def bust(self):
        return sum(i.value for i in self.player.cards) > 21

    def end_round():
        pass

    def action(self, action, amount = 0): #  poteza, treba vrniti stanje igre
        if action == HIT:
            self.hit()
        elif action == STAND:
            self.stand()
        elif action == SPLIT:
            self.split()
        elif action == DOUBLE_DOWN:
            self.double_down()
        elif action == SURENDER:
            self.surrender()
        elif action == BET:
            self.bet(amount)
          
class Blackjack:
    def __init__(self):
        self.games = {}

    def __repr__(self):
        return 'Blackjack()'

    def new_id(self):
        if not self.games:
            return 0
        else:
            return max(self.igre) + 1

    def new_game(self):
        id = self.new_id()
        self.games[id] = (Game(id), PLAYING)
        return id

    def action(self, game_id, action):
        game, state = self.games[game_id]
        state = game.action(action)
        self.games[game_id] = (game, state)

def new_game():
    return Game()