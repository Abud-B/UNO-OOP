import random

class Card:
    def __init__(self, color, value):
        self._color = color
        self._value = value

    def __str__(self):
        if self.get_value() in ['Wild', '+4']:
            return f"{self.get_value()}"
        else:
            return f"{self.get_color()} {self.get_value()}"

    def get_color(self):
        return self._color

    def set_color(self, color):
        self._color = color

    def get_value(self):
        return self._value


class Deck:
    def __init__(self):
        self._cards = []

    def create_deck(self):
            colors = ['Red', 'Yellow', 'Green', 'Blue']
            values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two']
            special_values = ['Wild', '+4']

            for color in colors:
                for value in values:
                    for _ in range(2):
                        self._cards.append(Card(color, value))
                self._cards.append(Card(color, '0'))  # Only one '0' card per color

            for value in special_values:
                for _ in range(4):  # Four 'Wild' and '+4' cards each
                    self._cards.append(Card(None, value))  # No color assigned initially

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

    def is_valid_move(self, card, top_card, game):
            if card.get_value() in ["Wild", "+4"]:
                if card.get_value() == "+4":
                    # Check if player has no other cards of the current color in their hand
                    for c in self._hand:
                        if c.get_color() == top_card.get_color():
                            return False
                return True  # 'Wild' and '+4' cards can be played at any time

            return (
                card.get_color() == top_card.get_color()
                or card.get_value() == top_card.get_value()
            )

    def play_card(self, card, discard_pile, game):
        if card in self._hand:
            top_card = discard_pile[-1]

            if self.is_valid_move(card, top_card, game):
                # if the player is about to have one card left, ask them to say 'UNO'
                if len(self._hand) == 2:
                    say_uno = input("You're about to have only one card left! Say 'UNO' (Y/N): ")
                    self._said_uno = say_uno.upper() == 'Y'

                if not self._said_uno and len(self._hand) == 2:
                    print(f"{self._name} failed to say 'UNO'! Draw 2 cards as a penalty.")
                    self.draw_card(game.get_deck(), 2)

                self._hand.remove(card)
                discard_pile.append(card)

                if card.get_value() == "Wild":
                    color = self.select_color()
                    card.set_color(color)

                elif card.get_value() == "+4":
                    color = self.select_color()
                    card.set_color(color)
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


    def select_color(self):
        valid_colors = ['Red', 'Yellow', 'Green', 'Blue']
        print("Select a color:")
        for i, color in enumerate(valid_colors):
            print(f"{i + 1}. {color}")

        while True:
            try:
                choice = int(input("Enter the index of the color: "))
                if 1 <= choice <= len(valid_colors):
                    return valid_colors[choice - 1]
                else:
                    print("Invalid choice! Please enter a valid index.")
            except ValueError:
                print("Invalid input! Please enter an integer.")


class Game:
    def __init__(self, players):
        self._players = players
        self._deck = Deck()
        self._discard_pile = []
        self._direction = 1
        self._current_player_index = 1

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

        if card_choice != "Draw a card":
            current_player.play_card(card_choice, self._discard_pile, self)
        else:
            drawn_card = self._deck.draw_card()
            current_player.add_card(drawn_card)
            print(f"You drew a {drawn_card}.")
                    
            # check if the drawn card is valid
            top_card = self._discard_pile[-1]
            if current_player.is_valid_move(drawn_card, top_card, self):
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
            if card.get_color() == top_card.get_color() or card.get_value() == top_card.get_value() or card.get_value() in ["Wild", "+4"]:
                valid_moves.append(card)
        return valid_moves


    def get_card_choice(self, valid_cards):
        while True:
            choice = input("Enter the index of the card you want to play or 'D' to draw a card: ").strip()
            if choice.lower() == "d":
                return "Draw a card"
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
        return self._players[self.get_next_player_index()]



def main():
    num_players = int(input("Enter the number of players: "))
    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append(Player(name))

    game = Game(players)
    game.start_game()


if __name__ == "__main__":
    main()