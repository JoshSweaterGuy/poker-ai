from model import Model
from deck import Deck
import action
from player_functions.josh_func import josh_func
from player_functions.vai_func import vai_func
class Game:
    
    # player_functions [player1_func, player2_func] amount of players playing and thier respective functions
    def __init__(self, model=Model(), player_functions=[josh_func, vai_func]):
        self.model = model
        self.player_functions = player_functions

    # gives each player two new cards from the deck
    def deal(self):
        deck = self.model.deck
        for player in self.model.players:
            player.cards = (deck.deal(), deck.deal())
            
    def reset_round(self):
        self.model.cum_cards.append(self.model.deck.deal())
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
            player_action = self.player_functions[player_index](self.model, self.model.players[player_index])

            if player_action == action.NONE:
                # IF NONE THEN GET INPUT
                # player_action[0] = input("enter action: [R]aise + [AMT], [C]all, [F]old")
                pass

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

        print('round over')
    
    # Returns -1 if no winner else winner index
    def play_game(self):
        is_game = True
        cum_cards = self.model.cum_cards
        deck = self.model.deck

        while is_game:
            self.reset_round()
            self.play_round()            
            winner = self.get_winner()
            if winner != -1:
                return winner
            
            for i in range(3): # deals first three community cards
                cum_cards.append(deck.deal)
            self.reset_round()
            self.play_round()
            winner = self.get_winner()
            if winner != -1:
                return winner

            cum_cards.append(deck.deal)
            self.reset_round()
            self.play_round()
            winner = self.get_winner()
            if winner != -1:
                return winner

            cum_cards.append(deck.deal)
            self.reset_round()
            self.play_round()
            winner = self.get_winner()
            if winner != -1:
                return winner
            return self.showdown()
            

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

        for player in self.model.players:
            print('player {}: {}, {}'.format(player.index, player.cards[0], player.cards[1]))
        
        winner = self.model.players[0]
        
        print('winner is player {}'.format(winner.index))

        return winner.index