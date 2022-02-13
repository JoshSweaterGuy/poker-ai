from model import Model
from deck import Deck
from treys import Evaluator
from treys import Card as Card2
import action
from player_functions.josh_func import josh_func
from player_functions.vai_func import vai_func


class Game:
    
    # player_functions amount of players playing and thier respective functions
    # josh_func, vai_func
    def __init__(self, model=Model(), player_functions=[None, None]):
        self.model = model
        self.player_functions = player_functions

    # gives each player two new cards from the deck
    def deal(self):
        deck = self.model.deck
        for player in self.model.players:
            player.cards = (deck.deal(), deck.deal())
            
    def reset_round(self):
        # self.model.cum_cards.append(self.model.deck.deal())
        # self.model.cum_cards = []
        self.model.min_b = self.model.b_blind
        for p in self.model.players:
            p.round_bet = 0

    def reset_game(self):
        self.model.deck = Deck()
        self.model.deck.shuffle()
        self.deal()
        self.model.button = (self.model.button + 1) % len(self.model.players)
        self.model.cum_cards = []
        self.model.pot = 0
        self.model.min_b = self.model.b_blind
        for i in range(len(self.model.players)):
            self.model.players[i].is_folded = False 
        
    def pay_blinds(self):
        sb_index = (self.model.button + 1) % len(self.model.players)
        bb_index = (self.model.button + 2) % len(self.model.players)
        sb = self.model.l_blind 
        bb = self.model.b_blind 
        self.model.players[sb_index].bet(sb)
        self.model.players[bb_index].bet(bb)
    
    # Returns -1 if no winner else winner index
    def play_round(self):
        print("community:", self.model.cum_cards)
        players = self.model.players
        is_round = True

        player_index = (self.model.button + 1) % len(self.model.players)

        def incr_index():
            nonlocal player_index
            player_index = (player_index + 1) % len(self.model.players)            
        
        self.pay_blinds()

        player_to_end_round = players[-1]
        # round loop
        while is_round:
            turn_player = players[player_index]

            while turn_player.is_folded and turn_player.stack == 0:
                incr_index()
                turn_player = players[player_index]

            # returns player action
            if (self.player_functions[player_index] == None):
                player_action_input = input('player {} action: ("enter action: [R]aise, [C]all, [F]old") '.format(turn_player.index))
        
                if player_action_input == 'R':
                    amt = int(input("AMOUNT TO RAISE: "))
                    player_action = (action.RAISE, amt)
                elif player_action_input == 'C':
                    player_action = (action.CALL, 0)
                elif player_action_input == 'F':
                    player_action = (action.FOLD, 0)
                    
            else:
                player_action = self.player_functions[player_index](self.model, self.model.players[player_index])

            if player_action[0] == action.RAISE:
                assert player_action[1] > 0 and player_action[1] <= turn_player.stack, "raise amount must be between 0 and stack"
                self.model.min_b += player_action[1]
                turn_player.bet(player_action[1])
                player_to_end_round = turn_player
                print('player {} raised by {}'.format(turn_player.index, player_action[1]))

            elif player_action[0] == action.CALL or player_action[0] == action.CHECK:
                assert self.model.min_b <= turn_player.stack, "player {} has {} and needs {} to bet".format(turn_player.index, turn_player.stack, self.model.min_b)
                p_bet = self.model.min_b - turn_player.round_bet
                turn_player.bet(p_bet)
                self.model.pot += p_bet
                
                print('player {} called the bet of {}'.format(turn_player.index, self.model.min_b))

                if player_to_end_round is turn_player:
                    is_round = False
                    
            elif player_action[0] == action.FOLD:
                turn_player.is_folded = True
                print('player {} folded'.format(turn_player.index))
            
            incr_index()

        print(players)
    
        print('round over')
    
    # Returns -1 if no winner else winner index
    def play_game(self):
        is_game = True
        cum_cards = self.model.cum_cards
        deck = self.model.deck

        self.reset_round()
        self.play_round()            
        winner = self.get_winner()
        if winner != -1:
            return winner
        
        for _ in range(3): # deals first three community cards
            self.model.cum_cards.append(deck.deal())

        while self.get_winner() == -1:
            self.reset_round()
            self.play_round()
            winner = self.get_winner()
            if winner != -1:
                return winner
            elif len(self.model.cum_cards) == 5:
                return self.showdown()
            
            self.model.cum_cards.append(deck.deal())

        return "LOL BROKE"
            

    def simulate_games_until_winner(self):
        games = 0
        games_before_increase = 30
        
        winner_index = -1
        while winner_index == -1:
            self.reset_game()
            winner_index = self.play_game()

            if games%games_before_increase == 0:
                self.model.b_blind *= 2
                self.model.b_blind *= 2
        
        print('player {} is the winner'.format(winner_index))


    def simulations(self, num_games):

        print('players {}'.format(len(self.model.players)))
        print('number of games {}'.format(num_games))

        winners = {}
        for i in range(num_games):
            winner = self.simulate_games_until_winner()
            if not winner in winners.keys():
                winners[winner] = 0
            winners[winner] += 1
            
            print('winners {}'.format(winners))

    
    # returns the index of the player that won the game if there is one, else returns -1
    # this is only for the case where everone else folds.
    def get_winner(self):
        sum = 0
        index = 0
        for i in range(len(self.model.players)):
            if not self.model.players[i].is_folded:
                sum += 1
                index = i
        if (sum == 1):
            return i 
        return -1

    # return index of winner 
    def showdown(self):
        print('showdown:')
        print('cum cards:')
        for card in self.model.cum_cards:
            print(card)
        ps = []

        for player in self.model.players:
            print('player {}: {}, {}'.format(player.index, player.cards[0], player.cards[1]))
        
            ps.append(player_score(player))
        
        print(ps)

        winner = self.model.players[0]
        
        print('winner is player {}'.format(winner.index))

        return winner.index
    def player_score_absolute(self, player):
        
        board = [Card2.new(), Card2.new('Kd'), Card2.new('Jc')]
        hand = [Card2.new('Qs'), Card2.new('Th')]
        evaluator = Evaluator()
        return  evaluator.evaluate(board, hand)
    def player_score(self, player):
        # each player's score is a 10-element array
        # record highest number for each case in array
        combined_hand = player.cards + self.model.cum_cards;
        combined_hand.sort()
        straight_flush, four_kind, full_house, flush, straight, three_kind, two_pair, pair, high_card = 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
        # 1 Straight Flush (strip 5)
        straight_flush = self.straight_flush_value(combined_hand)
        # combined_hand.

        # 2 Four of a Kind (strip 4)
        if (len(combined_hand) >= 7):
            four_kind = x_of_a_kind(4, combined_hand)

        # 3 Full House (score: highest number of 3-cards) (strip 5)
        if (len(combined_hand) >= 7):
            t3 = x_of_a_kind(3, combined_hand)
            copy_ch = [a.rank for a in combined_hand]
            copy_ch.remove(t3)
            copy_ch.remove(t3)
            t2 = x_of_a_kind(2, copy_ch)
            if t2 != 0 and t3 != 0:
                full_house = t3

        # 4 Flush (strip 5)
        if (len(combined_hand) >= 7):
            flush = self.flush_value(combined_hand)
        # 5 Straight (strip 5)
        if (len(combined_hand) >= 7):
            straight = self.straight_value(combined_hand)
        # 6 Three of a Kind (strip 3)
        if (len(combined_hand) >= 5):
            three_kind = x_of_a_kind(3, combined_hand)

        # 7 Two Pair (strip 4)
        if (len(combined_hand) >= 6):
            p1 = x_of_a_kind(2, combined_hand)
            copy_ch = [a.rank for a in combined_hand]
            copy_ch.remove(p1)
            p2 = x_of_a_kind(2, copy_ch)

            if p2 != 0:
                two_pair = p1 if p1 > p2 else p2


        # 8 One Pair (strip 2)
        if (len(combined_hand) >= 4):
            pair = x_of_a_kind(2, combined_hand)

        # 9 High Card (strip 1)
        if (len(combined_hand) > 2):
            high_card = x_of_a_kind(1, combined_hand)

        return [straight_flush, four_kind, full_house, flush, straight, three_kind, two_pair, pair, high_card] 
    
    # returns tuple of (cards, score) in hand
    def straight_value(self, combined_hand):
        # check for straight
        for i in range(len(combined_hand) - 4):
            if combined_hand[i].rank + 1 == combined_hand[i+1].rank  and combined_hand[i].rank + 2 == combined_hand[i+2].rank  and combined_hand[i].rank + 3 == combined_hand[i+3].rank and combined_hand[i].rank + 4 == combined_hand[i+4].rank :
                return [combined_hand[j] for j in range(i, i+5)], combined_hand[i].rank + 4
            

    def flush_value(self, combined_hand):
        # check for flush
        d = {}

        for card in combined_hand:
            if card not in d:
                d[card] = 1
            else:
                d[card] += 1
        
        mv = 0
        for (card, num) in d.items():
            if num >= 5 and card.rank > mv:
                mv = num
                mv_card = card.rank
        return mv

    # Combined_hand is sorted by rank
    def straight_flush_value(self, combined_hand):
        for i in range(len(combined_hand) - 4):
            start_val = i
            for j in range(i+5):
                # check for straight
                if combined_hand[j].rank == combined_hand[j+1].rank + 1  and combined_hand[j].rank == combined_hand[j+2].rank + 2  and combined_hand[j].rank == combined_hand[j+3].rank + 3 and combined_hand[j].rank == combined_hand[j+4].rank + 4 :
                    if (combined_hand[j].suit == combined_hand[j+1].suit and combined_hand[j].suit == combined_hand[j+2].suit and combined_hand[j].suit == combined_hand[j+3].suit and combined_hand[j].suit == combined_hand[j+4].suit):
                        return combined_hand[j].rank + 4
        return 0
        

    def x_of_a_kind(x, combined_hand):
        # check for x of a kind
        d = {}
        for c in combined_hands:
            if c.rank in d:
                d[c.rank] += 1
            else:
                d[c.rank] = 1
        mv = None
        for (k, v) in d.items():
            if v == x and (mv == None or k > mv):
                mv = k
        return 0
