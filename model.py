from deck import Deck
from player import Player

# Keeps track of the state of the game
class Model:

    def __init__(self, num_players=2, start_cash=1000, b_blind=50, l_blind=25):
        # the deck
        self.deck = Deck()
        self.deck.shuffle()

        # array of players
        self.players = [Player(index=i, stack=start_cash, cards=(), round_bet=0) for i in range(num_players)]   

        # the index of player that deals the card, indexs bb and lb
        self.button = 0

        # array of cards
        self.cum_cards = []

        # cash to win in the pot   
        self.pot = 0

        # amount needed to match or raise in round
        self.min_b = b_blind

        self.b_blind = b_blind
        self.l_blind = l_blind



    


