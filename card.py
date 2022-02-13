class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __repr__(self):
        return str(self.rank) + " of " + str(self.suit)

    def __str__(self):
        return str(self.rank) + " of " + str(self.suit)
    