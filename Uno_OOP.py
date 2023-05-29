import random
import pickle
import os
import sys
import time

class Card:
    def __init__(self, colour, value):
        self._colour = colour
        self._value = value
        self._is_swap = value == "Swap"


    def __str__(self):
        if self.get_value() in ['Wild', '+4']:
            return f"{self.get_value()}"
        else:
            return f"{self.get_colour()} {self.get_value()}"

    def get_colour(self):
        return self._colour

    def set_colour(self, colour):
        self._colour = colour

    def get_value(self):
        return self._value

    def is_swap(self):
        return self._is_swap


class Deck:
    def __init__(self):
        self._cards = []

    def create_deck(self):
            colours = ['Red', 'Yellow', 'Green', 'Blue']
            values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two']
            special_values = ['Wild', '+4', 'Swap']

            for colour in colours:
                for value in values:
                    for _ in range(2):
                        self._cards.append(Card(colour, value))
                self._cards.append(Card(colour, '0'))  # Only one '0' card per colour

            for value in special_values:
                for _ in range(4):  # Four 'Wild' and '+4' cards each
                    self._cards.append(Card(None, value))  # No colour assigned initially

    def shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self):
        return self._cards.pop()



class Player:
    def __init__(self, name):
        self._name = name
        self._hand = []
        self._said_uno = False

    @property
    def name(self):
        return self._name

    def draw_card(self, deck, num_cards):
        for _ in range(num_cards):
            self._hand.append(deck.draw_card())

    def has_no_cards(self):
        return len(self._hand) == 0
    
    def get_hand(self):
        return self._hand
    
    def add_card(self, card):
        self._hand.append(card)

    def is_valid_move(self, card, top_card):
            if card.get_value() in ["Wild", "+4"]:
                if card.get_value() == "+4":
                    # Check if player has no other cards of the current colour in their hand
                    for c in self._hand:
                        if c.get_colour() == top_card.get_colour():
                            return False
                return True  # 'Wild' and '+4' cards can be played at any time

            return (
                card.get_colour() == top_card.get_colour()
                or card.get_value() == top_card.get_value()
            )

    def play_card(self, card, discard_pile, game):
        if card in self._hand:
            top_card = discard_pile[-1]

            if self.is_valid_move(card, top_card):
                # if the player is about to have one card left, ask them to say 'UNO'
                if len(self._hand) == 2:
                    say_uno = input("You're about to have only one card left! Say 'UNO' (Y/N): ")
                    self._said_uno = say_uno.upper() == 'Y'

                if not self._said_uno and len(self._hand) == 2:
                    print(f"{self._name} failed to say 'UNO'! Draw 2 cards as a penalty.")
                    self.draw_card(game.get_deck(), 2)

                self._hand.remove(card)
                discard_pile.append(card)

                # check if the card is a swap card
                if game._house_rules and card.is_swap():
                    # If it's a swap card, ask the player who they want to swap hands with
                    other_player = self.select_other_player(game._players)
                    self._hand, other_player._hand = other_player._hand, self._hand
                    print(f"{self._name} swaps hands with {other_player._name}!")

                if card.get_value() == "Wild":
                    colour = self.select_colour()
                    card.set_colour(colour)

                elif card.get_value() == "+4":
                    colour = self.select_colour()
                    card.set_colour(colour)
                    next_player = game.get_next_player()
                    next_player.draw_card(game.get_deck(), 4)
                    game.skip_turn()

                if card.get_value() == "Skip":
                    game.skip_turn()
                elif card.get_value() == "Reverse":
                    # if there are only two players treat reverse as a skip
                    if len(game._players) == 2: 
                        game.skip_turn()  
                    else:
                        game.reverse_direction() 
                elif card.get_value() == "Draw Two":
                    next_player = game.get_next_player()
                    next_player.draw_card(game.get_deck(), 2)
                    # skip the next player's turn after they draw the cards
                    game.skip_turn()  
            else:
                print("Invalid move! The selected card cannot be played.\nDraw 2 cards for mistake")

        else:
            print("Invalid choice! Please enter a valid index.")



    def select_colour(self):
            valid_colours = ['Red', 'Yellow', 'Green', 'Blue']
            print("Select a colour:")
            for i, colour in enumerate(valid_colours):
                print(f"{i + 1}. {colour}")

            while True:
                try:
                    choice = int(input("Enter the index of the colour: "))
                    if 1 <= choice <= len(valid_colours):
                        return valid_colours[choice - 1]
                    else:
                        print("Invalid choice! Please enter a valid index.")
                except ValueError:
                    print("Invalid input! Please enter an integer.")
    
    def select_other_player(self, players):
        print("Select a player to swap hands with:")
        other_players = [player for player in players if player is not self]
        for i, player in enumerate(other_players):
            print(f"{i + 1}. {player._name}")
            
        while True:
            try:
                player_index = int(input("Enter the number of the player: "))
                if 1 <= player_index <= len(other_players):
                    return other_players[player_index - 1]
                print("Invalid choice! Please enter a valid number.")
            except ValueError:
                print("Invalid input! Please enter an integer.")


class Game:
    def __init__(self, players, house_rules=False):
        self._players = players
        self._deck = Deck()
        self._discard_pile = []
        self._direction = 1
        self._current_player_index = 0
        #house rules flag
        self._house_rules = house_rules

    def start_game(self):
        self._deck.create_deck()
        self._deck.shuffle()
        self.deal_initial_cards()

        top_card = self._deck.draw_card()
        special_values = ['Skip', 'Reverse', 'Draw Two', 'Wild', '+4']
        
        while top_card.get_value() in special_values:
            # if the top card is a special card, put it back and get another card
            self._deck._cards.insert(0, top_card)  
            top_card = self._deck.draw_card()  

        self._discard_pile.append(top_card)
        self.print_game_status()

        while True:
            if self.is_game_over():
                print("Game Over!")
                break

            self.play_turn()

    def deal_initial_cards(self):
        for player in self._players:
            player.draw_card(self._deck, 7)

    def print_game_status(self):
        print(f"Top card: {self._discard_pile[-1]}")

    def is_game_over(self):
        for player in self._players:
            if player.has_no_cards():
                return True
        return False

    def current_player(self):
        return self._players[self._current_player_index]

    def get_next_player_index(self):
        return (self._current_player_index + self._direction + len(self._players)) % len(self._players)

    def skip_turn(self):
        self._current_player_index = self.get_next_player_index()

    def reverse_direction(self):
        self._direction *= -1

    def get_deck(self):
        return self._deck

    def play_turn(self):
        current_player = self.current_player()
        print(f"\nCurrent player: {current_player.name}")
        print(f"Your hand: {', '.join(f'{i + 1}. {card}' for i, card in enumerate(current_player.get_hand()))}")

        valid_cards = self.get_valid_moves()
        print("Valid cards:")
        if valid_cards:  
            for i, card in enumerate(valid_cards):
                print(f"{i + 1}. {card}")
        else:  
            # tell the player to draw a card if there are no valid moves
            print("No valid cards in your hand. You will have to draw a card.")

        card_choice = self.get_card_choice(valid_cards)

        if isinstance(card_choice, Card) and self._house_rules and card_choice.get_value() in ["Draw Two", "+4"]:
            # ff stacking is toggled and a draw card is played, check if the next player can stack
            next_player = self.get_next_player()
            for card in next_player._hand:
                if card.get_value() == card_choice.get_value():
                    print("Stacking enabled!")
                    card_to_stack = card
                    break
            else:
                card_to_stack = None

            if card_to_stack is not None:
                # if the next player can stack, play their card and skip the current player's turn
                print(f"{next_player.name} stacks a {card_choice}!")
                next_player.play_card(card_to_stack, self._discard_pile, self)
                self._current_player_index = (self._current_player_index + self._direction) % len(self._players)
            else:
                # if the next player can't stack, apply the penalty and move on to the next player
                next_player.draw_card(self._deck, 2 if card_choice.get_value() == "Draw Two" else 4)
                self._current_player_index = (self._current_player_index + self._direction) % len(self._players)
        else:
            if card_choice != "Draw a card":
                current_player.play_card(card_choice, self._discard_pile, self)
                self._current_player_index = (self._current_player_index + self._direction) % len(self._players)
            else:
                drawn_card = self._deck.draw_card()
                current_player.add_card(drawn_card)
                print(f"You drew a {drawn_card}.")
                
                # check if the drawn card is valid
                top_card = self._discard_pile[-1]
                if current_player.is_valid_move(drawn_card, top_card):
                    print(f"The card you drew is valid. You may choose to play it.")
                    decision = input("Do you want to play the card you drew? (Y/N): ")
                    if decision.lower() == 'y':
                        current_player.play_card(drawn_card, self._discard_pile, self)

        self._current_player_index = (self._current_player_index + self._direction) % len(self._players)
        self.print_game_status()

    def get_valid_moves(self):
        top_card = self._discard_pile[-1]
        valid_moves = []

        current_player = self.current_player()  
        for card in current_player._hand:  
            if card.get_colour() == top_card.get_colour() or card.get_value() == top_card.get_value() or card.get_value() in ["Wild", "+4"]:
                valid_moves.append(card)
        return valid_moves


    def get_card_choice(self, valid_cards):
        while True:
            choice = input("Enter the index of the card you want to play, 'D' to draw a card, or 'S' to save and exit: ").strip()
            if choice.lower() == "d":
                return "Draw a card"
            elif choice.lower() == "s":
                self.save_game()
                print("Game saved and exited.")
                # uses sys.exit to quit game
                sys.exit(0)  
            else:
                try:
                    choice = int(choice)
                    if 1 <= choice <= len(valid_cards):
                        return valid_cards[choice - 1]
                    else:
                        print("Invalid choice! Please enter a valid index.")
                except ValueError:
                    print("Invalid input! Please enter an integer.")


    def get_next_player(self):
        # return index of next player
        return self._players[self.get_next_player_index()]
    
    def get_next_player(self):
        # return player object of next player
        return self._players[self.get_next_player_index()]
    
    def save_game(self):
        with open('saved_game.pkl', 'wb') as file:
            pickle.dump(self, file)
        print("Game has been saved.")

    def resume_game(self):
        self.print_game_status()
        while True:
            if self.is_game_over():
                print("Game Over!")
                break
            self.play_turn()

    @staticmethod
    def load_game():
        if os.path.exists('saved_game.pkl'):
            with open('saved_game.pkl', 'rb') as file:
                return pickle.load(file)
        else:
            print("No saved game found.")
            return None

def main():
    game = None
    while True:
        command = input("Enter a command (new, save, load, quit): ")
        if command.lower() == 'new':
            game = start_new_game()
        elif command.lower() == 'save':
            if game is None:
                print("No active game to save. Start a new game first.")
            else:
                game.save_game()
        elif command.lower() == 'load':
            if not os.path.exists('saved_game.pkl'):
                print("No saved game to load. Start and save a new game first.")
            else:
                game = Game.load_game()
                if game is not None:
                    print("Game loaded successfully.")
                    #load and start game
                    game.resume_game()  
                else:
                    print("Failed to load the game.")
        elif command.lower() == 'quit':
            print("Game quitting\nGoodbye!")
            time.sleep(5)
            break
        else:
            print("Invalid command.")


def start_new_game():
    while True:
        try:
            num_players = int(input("Enter the number of players: "))
            break
        except ValueError:
            print("Invalid input! Please enter an integer.")

    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append(Player(name))

    while True:
        house_rules_input = input("Do you want to enable house rules? (yes/no): ").lower().strip()
        if house_rules_input in ["yes", "no"]:
            break
        print("Invalid input! Please enter 'yes' or 'no'.")

    house_rules = house_rules_input == "yes"

    game = Game(players, house_rules)
    game.start_game()

    return game

if __name__ == "__main__":
    main()