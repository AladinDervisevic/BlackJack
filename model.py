class Card:
    def __init__(self, value, suit):
        self.showing = True
        self.value = value
        self.suit = suit

def new_deck():
    deck = []
    for value in range(1, 15):
        for suit in ['Hearts', 'Diamonds', 'Clubs', 'Pikes']:
            deck.append(Card(value, suit))
    return deck

class Dealer:
    def __init__(self):
        self.cards = []

class Player:
    def __init__(self):
        self.money = 0
        self.cards = []

    def bet(self, amount):
        pass

    def stand(self):
        pass

    def hit(self):
        pass

    def double_down(self):
        pass

    def split(self):
        pass

    def surrender(self):
        pass

class Game:
    def __init__(self, id):
        self.id = id
        self.deck = new_deck()
        self.players = []
        self.current_player = 0
        self.dealer = Dealer()
        self.lot = 0

    def bet(self, player, amount):
        pass

    def stand(self, player):
        pass

    def hit(self, player):
        pass

    def double_down(self, player):
        pass

    def split(self, player):
        pass

    def surrender(self, player):
        pass

    def new_round(self):
        pass

class Blackjack:
    def __init__(self):
        self.games = {}

    def new_id(self):
        if not self.games:
            return 0
        else:
            return max(self.igre) + 1

    def new_game(self):
        id = self.new_id()
        return Game(id)