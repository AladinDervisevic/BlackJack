import random

START = 'P'
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
SURRENDER = 'SU'
BET = 'B'
ACE = 'A'

ACTIONS = [STAND, SPLIT, DOUBLE_DOWN, SURRENDER, BET, HIT] # player's moves

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
        if self.showing:
            return f'{self.kind} {self.suit}'
        else:
            return '[?]'

    def __repr__(self):
        if self.showing:
            if self.kind in 'AJQK':
                return f'Card({self.kind} = {self.value}, {self.suit})'
            else:
                return f'Card({self.kind}, {self.suit})'
        else:
            return 'Card(?)'

def new_deck():
    deck = []
    for kind in list(range(2, 11)) + ['A', 'J', 'Q', 'K']:
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Pikes']:
            for _ in range(2):
                deck.append(Card(kind, suit))  # so that there are 2 decks in the game
    random.shuffle(deck)
    return deck

def hand_value(cards):
    return sum(card.value for card in cards)

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

    def blackjack(self):
        return all(card.kind in 'AK' for card in self.cards)

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
        self.dealer.cards[1].showing = True
        while hand_value(self.dealer.cards) < 17:
            card = random.choice(self.deck)
            self.dealer.cards.append(card)
            if card.kind == 'A' and hand_value(self.dealer.cards) > 21:
                card.value = 1

    def end_round(self):
        if hand_value(self.dealer.cards) > 21 or (hand_value(self.player.cards) > hand_value(self.player.cards)):
            self.player.money += self.lot
            self.lot = 0
            return ROUND_WIN
        elif hand_value(self.player.cards) == hand_value(self.dealer.cards):
            self.player.money += (self.lot // 2)
            self.dealer.money += (self.lot // 2)
            self.lot = 0
            return TIE
        elif hand_value(self.player.cards) < hand_value(self.dealer.cards):
            self.dealer.money += self.lot
            self.lot = 0
            return ROUND_LOSS

    def bust(self):
        return sum(i.value for i in self.player.cards) > 21

    def hit(self):
        card = random.choice(self.deck)
        self.deck.remove(card)
        self.player.cards.append(card)
        if card.kind == 'A':
            return ACE
        if self.bust():
            return BUST
        else:
            return HIT

    def set_ace_value(self, value):
        for card in self.player.cards[::-1]:
            if card.kind == 'A':
                card.value = value
                return HIT if not self.bust() else BUST

    def double_down(self):
        return DOUBLE_DOWN

    def split(self):
        return SPLIT

    def surrender(self):
        return SURRENDER

    def deal_cards(self):
        if len(self.deck) < 25:
            self.deck += self.graveyard
            random.shuffle(self.deck)
            self.graveyard = []
        if self.player.cards:  #if players currently hold some cards
            self.graveyard += self.dealer.cards
            self.graveyard += self.player.cards
            self.dealer.cards = []
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
        return NEW_ROUND

    def blackjack(self):
        self.player.money += (self.lot + 100)
        self.lot = 0

    def win(self):
        return self.dealer.money <= 0

    def loss(self):
        return self.player.money <= 0

    def action(self, action, amount = 0): #  poteza, treba vrniti stanje igre
        if action == HIT:
            self.hit()
        elif action == STAND:
            self.stand()
        elif action == SPLIT:
            self.split()
        elif action == DOUBLE_DOWN:
            self.double_down()
        elif action == SURRENDER:
            self.surrender()
          
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
        self.games[id] = (Game(id), START)
        return id

    def action(self, game_id, action):
        game, state = self.games[game_id]
        state = game.action(action)
        self.games[game_id] = (game, state)

def new_game():
    return (Game(), START)