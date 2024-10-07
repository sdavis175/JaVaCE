from known_vocab.vocab_recognizer import VocabRecognizer

from argparse import ArgumentParser
from pyperclip import paste
from time import sleep, time
import colorama
import csv
import re
from keras.models import load_model, Model
from keras.utils.data_utils import pad_sequences
import tensorflow as tf
from transformers import BertJapaneseTokenizer
import numpy as np
from traceback import print_exc

TOKENIZER_LENGTH = 128
KNOWN_WEIGHT = 10
UNKNOWN_WEIGHT = -10
index2label = {
    0: "Easy",
    1: "Medium",
    2: "Hard"
}

# Main problems:
#   - Tokenizer sucks at dealing with inflections
#       (implement de-tokenizer to get back to dictionary form and also use dictionary lookups for separating words)
#   - Words that are known in kanji but written in hiragana aren't detected
#   - Readings written in katakana (more of a preference to be written in hiragana)
#   - Unable to tweak the model in case the comprehension prediction is wrong
#       (probably save the sentence and new prediction to a file to be trained on later)


def javace(args):
    # Load vocab
    s = time()
    vocab_recognizer = VocabRecognizer()
    print("Finished loading known vocab.")
    if args.print_times:
        print(f"Time taken: {round(time() - s, 2)} seconds.")

    if args.print_comprehension:
        s = time()
        # Don't pre-allocate all my VRAM
        tf.config.experimental.set_memory_growth(tf.config.list_physical_devices("GPU")[0], True)
        model = load_model(args.comprehension_model_path)
        model: Model
        bert_tokenizer = BertJapaneseTokenizer.from_pretrained("cl-tohoku/bert-base-japanese",
                                                               word_tokenizer_type="sudachi",
                                                               sudachi_kwargs={
                                                                   "sudachi_dict_type": "full",
                                                                   "sudachi_split_mode": "A"
                                                               })
        print("Finished loading comprehension model and BERT tokenizer.")
        if args.print_times:
            print(f"Time taken: {round(time() - s, 2)} seconds.")
    else:
        model = None
        bert_tokenizer = None

    # Run clipboard hook
    clipboard = ""
    times = []
    while clipboard != "exit":
        if clipboard != paste():
            s = time()
            clipboard = paste()
            try:
                # Maybe conditionally run this if the clipboard is mostly Japanese
                raw_text = re.sub(r"[\n\r\t ]", "", clipboard)
                raw_text = re.sub(r"。", "。┆", raw_text)
                sentences = [sentence.strip() for sentence in re.split("┆", raw_text) if len(sentence) > 1]
                if args.print_comprehension:
                    # Encode the sentences using the BERT Tokenizer
                    encoded_sentences = bert_tokenizer.batch_encode_plus(sentences,
                                                                         add_special_tokens=True,
                                                                         return_attention_mask=True,
                                                                         padding="max_length",
                                                                         max_length=TOKENIZER_LENGTH,
                                                                         return_tensors="tf",
                                                                         truncation=True)
                    # Create the known embeddings and pad them to length
                    known_vocab_sentences = [vocab_recognizer.mark_known_vocab(sentence,
                                                                               return_print_str=False,
                                                                               sentence_bert_tokenized=bert_tokenizer.
                                                                               tokenize(sentence))
                                             for sentence in sentences]
                    known_embeddings = []
                    for known_vocab_list in known_vocab_sentences:
                        known_embeddings.append(pad_sequences(
                            [np.array([0] + [KNOWN_WEIGHT if known_vocab else UNKNOWN_WEIGHT
                                             for known_vocab in known_vocab_list] + [0])],
                            maxlen=TOKENIZER_LENGTH, dtype=float, padding="post")[0])

                    # Predict the comprehension on all the sentences
                    predicted_comprehensions = np.argmax(model.predict((encoded_sentences["input_ids"],
                                                                        encoded_sentences["token_type_ids"],
                                                                        encoded_sentences["attention_mask"],
                                                                        np.array(known_embeddings, dtype=float)),
                                                                       verbose=False),
                                                         axis=1)
                else:
                    predicted_comprehensions = []

                for sentence_index, sentence in enumerate(sentences):
                    print(vocab_recognizer.mark_known_vocab(sentence,
                                                            mark_katakana_as_known=not args.unmark_katakana,
                                                            mark_particles_as_known=not args.unmark_particles,
                                                            mark_romanji_as_known=not args.unmark_romanji,
                                                            add_readings=args.show_readings))

                    if args.print_comprehension:
                        print(f"Predicted Comprehension: {index2label[predicted_comprehensions[sentence_index]]}")

                    if args.save_sentences:
                        if len(sentence) > 5:
                            with open(args.sentences_path, "a", newline="", encoding="utf-8") as sentences_file:
                                writer = csv.writer(sentences_file)
                                writer.writerow([sentence])
                    if args.print_times:
                        times.append(time() - s)
                    print("-" * 15)

                if args.print_times:
                    print(f"Time taken: {round(time() - s, 2)} seconds.")
                print("-" * 30)

            except Exception as e:
                print(f"Error while processing clipboard={repr(clipboard)}")
                print_exc()

        sleep(.25)

    if args.print_times:
        # First time is always much longer than the rest, skip it
        print(f"Average time taken per sentence: {round(sum(times[1:])/len(times[1:]), 2)} seconds.")


if __name__ == '__main__':
    colorama.init()
    parser = ArgumentParser(description="JaVaCE - Japanese Vocabulary and Comprehension Estimator")
    parser.add_argument("--print_times",
                        default=False,
                        action="store_true",
                        help="Prints how long tokenizer took")
    parser.add_argument("--show_readings",
                        default=False,
                        action="store_true",
                        help="Prints katakana readings for kanji tokens")
    parser.add_argument("--unmark_katakana",
                        default=False,
                        action="store_true",
                        help="Do not automatically mark katakana words as known")
    parser.add_argument("--unmark_particles",
                        default=False,
                        action="store_true",
                        help="Do not automatically mark grammar particles as known")
    parser.add_argument("--unmark_romanji",
                        default=False,
                        action="store_true",
                        help="Do not automatically mark romanji and numbers as known")
    parser.add_argument("--sentences_path",
                        default=None,
                        help="Path to saved copied sentences to")
    parser.add_argument("--save_sentences",
                        default=False,
                        action="store_true",
                        help="Saved copied sentences to sentences_path")
    parser.add_argument("--print_comprehension",
                        default=False,
                        action="store_true",
                        help="Print comprehension estimator model evaluation on input sentences")
    parser.add_argument("--comprehension_model_path",
                        default=None,
                        help="Path to saved comprehension model")
    javace(parser.parse_args())
