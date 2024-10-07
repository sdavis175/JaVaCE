import json
import urllib.request
from traceback import print_exc

ANKI_CONNECT_URI = 'http://localhost:8765'
WORD_FIELD = "Word"
DECK = "current"


# Request & invoke code from https://github.com/FooSoft/anki-connect#python
def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}


def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request(ANKI_CONNECT_URI, requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def anki_sync():
    cur_card_ids = invoke("findCards", query=f"deck:{DECK}")
    cur_note_ids = invoke("cardsToNotes", cards=cur_card_ids)
    cur_cards = invoke("cardsInfo", cards=cur_card_ids)
    cur_notes = invoke("notesInfo", notes=cur_note_ids)
    words = []
    for note in cur_notes:
        try:
            card_id = note["cards"][0]
            card = next((card for card in cur_cards if card["cardId"] == card_id), None)

            word = note["fields"][WORD_FIELD]["value"]
            leech = True if len(note["tags"]) and note["tags"][0] == "leech" else False
            ivl = card["interval"]

            # Potentially add logic here depending on card interval, leech
            if ivl > 0:
                words.append(word)
        except Exception as e:
            print(f"Skipping note: {note}")
            print_exc()

    with open("anki.txt", "w", encoding="utf-8") as anki_file:
        for word in words:
            anki_file.write(f"{word}\n")


if __name__ == '__main__':
    anki_sync()
