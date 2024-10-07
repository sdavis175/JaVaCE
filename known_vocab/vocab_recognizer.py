from known_vocab.kana import contains_kanji, only_katakana, only_romanji

from sudachipy import tokenizer, dictionary
from colorama import Fore, Style


class VocabRecognizer:
    def __init__(self, anki_data_path="./known_vocab/anki.txt", manual_data_path="./known_vocab/manual.txt"):
        self.sudachi_tokenizer = dictionary.Dictionary(dict="full").create(tokenizer.Tokenizer.SplitMode.A)

        # Load vocab
        with open(anki_data_path, "r", encoding="utf-8") as anki_file:
            anki_raw = anki_file.read().splitlines()
        with open(manual_data_path, "r", encoding="utf-8") as manual_file:
            manual_raw = manual_file.read().splitlines()
        raw_known_vocab = set(anki_raw + manual_raw)

        # Tokenize vocab to dictionary form
        self.known_vocab_list = []
        for known_vocab in raw_known_vocab:
            self.known_vocab_list.append([morpheme.dictionary_form()
                                          for morpheme in self.sudachi_tokenizer.tokenize(known_vocab)])
        self.known_vocab_list.sort(key=lambda x: len(x), reverse=True)  # Sort from longest -> shortest

    def mark_known_vocab(self, sentence,
                         prefix_mark=Fore.GREEN, postfix_mark=Style.RESET_ALL,
                         mark_katakana_as_known=True, mark_particles_as_known=True, mark_romanji_as_known=True,
                         return_print_str=True, skip_easy_known=False, add_readings=False,
                         sentence_bert_tokenized=None):
        sentence_tok = self.sudachi_tokenizer.tokenize(sentence)
        sentence_dict = [morpheme.dictionary_form() for morpheme in sentence_tok]
        sentence_surf = [morpheme.surface() for morpheme in sentence_tok]
        sentence_pos = [morpheme.part_of_speech() for morpheme in sentence_tok]
        sentence_readings = [morpheme.reading_form() for morpheme in sentence_tok]

        if sentence_bert_tokenized is not None:
            # Add any placeholder "" to the parts where there is sub-words
            for i in range(len(sentence_bert_tokenized)):
                if "#" in sentence_bert_tokenized[i]:
                    sentence_dict.insert(i, "")
                    sentence_surf.insert(i, "")
                    sentence_pos.insert(i, ["", "", "", "", ""])

            assert len(sentence_bert_tokenized) == len(sentence_dict), sentence

        print_str = ""
        known_tokens = []
        i = 0
        while i < len(sentence_dict):
            match_found = False
            for vocab_word in self.known_vocab_list:
                if (len(vocab_word) == 1 and
                    ((mark_particles_as_known and sentence_pos[i][0] == "助詞") or
                     (mark_katakana_as_known and only_katakana(sentence_dict[i])) or
                     (mark_romanji_as_known and only_romanji(sentence_dict[i])))) or \
                        sentence_dict[i:i + len(vocab_word)] == vocab_word:
                    # Found a string that matches the total vocabulary words
                    mark_known = True
                    # Maybe add logic here for conditionally marking it as known (for things like bad matches)

                    if mark_known:
                        print_str += prefix_mark

                    print_str += "".join(sentence_surf[i:i + len(vocab_word)])
                    if add_readings and contains_kanji("".join(sentence_surf[i:i + len(vocab_word)])):
                        print_str += f"({''.join(sentence_readings[i:i + len(vocab_word)])})"

                    if mark_known:
                        for _ in range(len(vocab_word)):
                            if skip_easy_known and not (
                                    len(vocab_word) == 1 and
                                    (only_romanji(sentence_dict[i]) or
                                     only_katakana(sentence_dict[i]) or
                                     sentence_pos[i][0] == "助詞")):
                                known_tokens.append(True)
                            elif not skip_easy_known:
                                known_tokens.append(True)
                        print_str += postfix_mark

                    else:
                        for _ in range(len(vocab_word)):
                            known_tokens.append(False)

                    i += len(vocab_word)
                    match_found = True
                    break

            if not match_found:
                print_str += "".join(sentence_surf[i])

                if add_readings and contains_kanji("".join(sentence_surf[i])):
                    print_str += f"({''.join(sentence_readings[i])})"

                if sentence_surf[i] == "":
                    # BERT Placeholder, just redo whatever the last known action was
                    known_tokens.append(known_tokens[-1])
                else:
                    known_tokens.append(False)

                i += 1

        if not skip_easy_known:
            assert len(known_tokens) == len(sentence_dict)

        if return_print_str:
            return print_str
        else:
            return known_tokens
