from known_vocab.vocab_recognizer import VocabRecognizer
from argparse import ArgumentParser
import colorama
from os.path import basename, splitext
import pandas as pd
import csv

LAST_INDEX_PATH = "./last_index_{}.txt"
DIFFICULTY_PATH = "./difficulty_日本語.csv"


def grade_sentences(args):
    # Load vocab
    vocab_recognizer = VocabRecognizer()
    print("Finished loading known vocab.")

    # Load the CSV file
    df = pd.read_csv(args.input_path)

    # Set the starting index to the last ID from the previous run
    start_index = 0
    try:
        with open(LAST_INDEX_PATH.format(splitext(basename(args.input_path))[0]), "r") as f:
            start_index = int(f.read().strip()) + 1
    except FileNotFoundError:
        pass

    # Loop through each row in the dataframe, starting from the last ID
    for i in range(start_index, len(df)):
        # Get the Japanese sentence, ID, and English translation
        japanese_sentence = df.loc[i, args.japanese_sentence_key]
        english_translation = df.loc[i, args.english_sentence_key] if args.english_sentence_key is not None else None

        # Ask the user to input a difficulty score
        difficulty_score = input(
            f"Please enter a difficulty score (0-2) for this sentence: "
            f"{vocab_recognizer.mark_known_vocab(japanese_sentence, add_readings=True)}\n")
        while difficulty_score not in ["0", "1", "2"]:
            difficulty_score = input("Invalid input. Please enter a difficulty score (0-2): ")

        # Print the English translation and the user's difficulty score
        if english_translation is not None and english_translation != "":
            print(f"English translation: {repr(english_translation)}")

            # Give the user the option to change the difficulty score or continue
            change_score = input("Would you like to change the difficulty score? (y/n): ")
            while change_score.lower() not in ["y", "n"]:
                change_score = input("Invalid input. Would you like to change the difficulty score? (y/n): ")

            # If the user wants to change the score, ask for a new one
            if change_score.lower() == "y":
                new_score = input(f"Please enter a new difficulty score (0-2) for this sentence: "
                                  f"{vocab_recognizer.mark_known_vocab(japanese_sentence, add_readings=True)}\n")
                while new_score not in ["0", "1", "2"]:
                    new_score = input("Invalid input. Please enter a difficulty score (0-2): ")
                difficulty_score = new_score

        # Save the sentence, difficulty score, and ID to a new CSV file
        with open(DIFFICULTY_PATH, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([japanese_sentence, difficulty_score])

        # Save the current index to a file so we can start from there next time
        with open(LAST_INDEX_PATH.format(splitext(basename(args.input_path))[0]), "w") as f:
            f.write(str(i))


if __name__ == '__main__':
    colorama.init()
    parser = ArgumentParser(description="Grade Sentences")
    parser.add_argument("--input_path",
                        required=True,
                        help="Path to input sentences csv file")
    parser.add_argument("--japanese_sentence_key",
                        required=True,
                        help="Key to Japanese sentence in input sentences file")
    parser.add_argument("--english_sentence_key",
                        default=None,
                        help="Key to English sentence translation in input sentences file")
    parser.add_argument("--show_readings",
                        default=False,
                        action="store_true",
                        help="Prints katakana readings for kanji tokens")
    grade_sentences(parser.parse_args())
