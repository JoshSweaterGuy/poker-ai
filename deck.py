from card import Card

class Deck:
    def __init__(self):
        self.deck = []
        for suit in range(4):
            for rank in range(1, 14):
                self.deck.append(Card(suit, rank))

    def shuffle(self):
        import random
        random.shuffle(self.deck)

    def deal(self):
        if len(self.deck) == 0:
            return None
        else:
            return self.deck.pop()
