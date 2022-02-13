from deck import Deck
from card import Card
class Player:
    def __init__(self, index=0, stack=0, cards=(Card(0, 1), Card(1, 1)), round_bet=0):
        self.index = index
        self.stack = stack
        self.cards = cards
        self.round_bet = round_bet
        self.is_folded = False
        self.total_bet = 0

    def bet(self, amount):
        self.round_bet += amount
        self.stack -= amount
        self.total_bet += amount

    def fold(self):
        self.is_folded = True

    def __repr__(self):
        return "Player {}: {} \n round_bet {}, total_bet {}".format(self.index, self.cards, self.round_bet, self.total_bet)
    def __str__(self):
        return "Player {}: {}".format(self.index, self.cards)
    