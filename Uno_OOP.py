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
        self._valid_colors = ['Red', 'Yellow', 'Green', 'Blue']

    def create_deck(self):
        colors = ['Red', 'Yellow', 'Green', 'Blue']
        values = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'Skip', 'Reverse', 'Draw Two', 'Wild', '+4']

        for color in colors:
            for value in values:
                self._cards.append(Card(color, value))

    def shuffle(self):
        random.shuffle(self._cards)

    def draw_card(self):
        return self._cards.pop()

    def get_valid_colors(self):
        return self._valid_colors

    def set_valid_colors(self, valid_colors):
        self._valid_colors = valid_colors


class Player:
    def __init__(self, name):
        self._name = name
        self._hand = []

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

    def is_valid_move(self, card, top_card, game):
        return (
            card.get_color() == top_card.get_color()
            or card.get_value() == top_card.get_value()
            or card.get_value() in ["Wild", "+4"]
        )

    def play_card(self, card, discard_pile, game):
        if card in self._hand:
            top_card = discard_pile[-1]

            if self.is_valid_move(card, top_card, game):
                self._hand.remove(card)
                discard_pile.append(card)
                
                if len(self._hand) == 1:
                    say_uno = input("Say 'UNO' if you have only one card left (Y/N): ")
                    while say_uno.upper() not in ["Y", "N", "UNO"]:
                        print("Invalid input! Please enter 'Y' or 'N'.")
                        say_uno = input("Say 'UNO' if you have only one card left (Y/N): ")

                    if say_uno.upper() != "Y":
                        print("You failed to say 'UNO'! Draw 2 cards as a penalty.")
                        self.draw_card(game.get_deck(), 2)

                if card.get_value() == "Wild":
                    valid_colors = game.get_deck().get_valid_colors()
                    color = self.select_color(valid_colors)
                    card.set_color(color)
                    valid_colors.append(color)

                elif card.get_value() == "+4":
                    valid_colors = game.get_deck().get_valid_colors()
                    color = self.select_color(valid_colors)
                    card.set_color(color)
                    valid_colors.append(color)
                    next_player = game.get_next_player()
                    next_player.draw_card(game.get_deck(), 4)
                    game.skip_turn()

                if card.get_color() != "Wild" and card.get_color() in game.get_deck().get_valid_colors():
                    game.get_deck().get_valid_colors().remove(card.get_color())

                if card.get_value() == "Skip":
                    game.skip_turn()
                elif card.get_value() == "Reverse":
                    game.reverse_direction()
                elif card.get_value() == "Draw Two":
                    next_player = game.get_next_player()
                    next_player.draw_card(game.get_deck(), 2)
                    game.skip_turn()  # Skip the next player's turn when a "Draw Two" card is played
            else:
                print("Invalid move! The selected card cannot be played.")
        else:
            print("Invalid choice! Please enter a valid index.")


    def select_color(self, valid_colors):
        print("Select a valid color:")
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
        self._current_player_index = 0

    def start_game(self):
        self._deck.create_deck()
        self._deck.shuffle()
        self.deal_initial_cards()

        top_card = self._deck.draw_card()
        special_values = ['Skip', 'Reverse', 'Draw Two', 'Wild', '+4']
        
        while top_card.get_value() in special_values:
            self._deck._cards.insert(0, top_card)  # Put the special card back into the deck
            top_card = self._deck.draw_card()  # Draw another card

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
        return (self._current_player_index + self._direction) % len(self._players)

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
        for i, card in enumerate(valid_cards):
            print(f"{i + 1}. {card}")

        card_choice = self.get_card_choice(valid_cards)

        if card_choice != "Draw a card":
            current_player.play_card(card_choice, self._discard_pile, self)
        else:
            drawn_card = self._deck.draw_card()
            current_player.hand.append(drawn_card)
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
