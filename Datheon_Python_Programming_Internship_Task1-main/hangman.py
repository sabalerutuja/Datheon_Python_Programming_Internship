import random
import os

# ASCII Hangman stages
HANGMAN_ART = [
    """
     +---+
         |
         |
         |
        ===
    """,
    """
     +---+
     O   |
         |
         |
        ===
    """,
    """
     +---+
     O   |
     |   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|   |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
         |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    /    |
        ===
    """,
    """
     +---+
     O   |
    /|\\  |
    / \\  |
        ===
    """
]


def load_words():
    """Load English words from the provided text file."""
    filename = "English Words List.txt"

    try:
        with open(filename, "r", encoding="utf-8") as file:
            words = [
                word.strip().lower()
                for word in file
                if word.strip().isalpha()
            ]

        if not words:
            print("Error: The word list is empty.")
            return []

        return words

    except FileNotFoundError:
        print(f"Error: '{filename}' was not found.")
        print("Place the word list in the same folder as hangman.py.")
        return []


def display_word(secret_word, guessed_letters):
    """Display correctly guessed letters and hide the others."""
    return " ".join(
        letter if letter in guessed_letters else "_"
        for letter in secret_word
    )


def play_hangman():
    """Run the Hangman game."""
    words = load_words()

    if not words:
        return

    secret_word = random.choice(words)
    guessed_letters = set()
    wrong_guesses = 0
    max_attempts = 6

    print("\n================================")
    print("       HANGMAN WORD GAME")
    print("================================")
    print("Guess the hidden English word!")
    print("You have 6 incorrect attempts.")

    while wrong_guesses < max_attempts:

        print("\nHangman:")
        print(HANGMAN_ART[wrong_guesses])

        print("Word:", display_word(secret_word, guessed_letters))
        print("Incorrect attempts:", wrong_guesses)
        print("Attempts remaining:", max_attempts - wrong_guesses)

        if guessed_letters:
            print("Previously guessed letters:",
                  ", ".join(sorted(guessed_letters)))
        else:
            print("Previously guessed letters: None")

        # Check whether the player has guessed the word
        if all(letter in guessed_letters for letter in secret_word):
            print("\nCongratulations! You won!")
            print("The word was:", secret_word)
            return

        guess = input("\nEnter a letter: ").strip().lower()

        # Validate the input
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Enter one alphabet letter.")
            continue

        # Prevent duplicate guesses
        if guess in guessed_letters:
            print("You already guessed that letter. Try another.")
            continue

        guessed_letters.add(guess)

        # Check the guessed letter
        if guess in secret_word:
            print("Correct guess!")
        else:
            wrong_guesses += 1
            print("Incorrect guess!")

    # Display the final hangman stage
    print("\n" + HANGMAN_ART[max_attempts])
    print("================================")
    print("           GAME OVER")
    print("================================")
    print("You have used all 6 incorrect attempts.")
    print("The correct word was:", secret_word)


if __name__ == "__main__":
    play_hangman()