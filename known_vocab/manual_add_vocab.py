def manual_add():
    # Prompt user for a Japanese word
    japanese_word = input("Enter a known Japanese word: ")

    # Open the file for reading
    with open("manual.txt", "r", encoding="utf-8") as f:
        # Read the contents of the file into a list of lines
        lines = f.readlines()

    # Check if the word is already in the file
    if f"{japanese_word}\n" in lines:
        print("The word is already in the file!")
    else:
        # Open the file for appending
        with open("manual.txt", "a", encoding="utf-8") as f:
            # Write the word to the file followed by a newline character
            f.write(f"{japanese_word}\n")
            print("The word has been added to the file.")


if __name__ == '__main__':
    manual_add()
