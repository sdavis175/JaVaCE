# http://japanese-lesson.com/characters/hiragana/index.html
HIRAGANA = set("あかさたなはまやらわ"
               "いきしちにひみり"
               "うくすつぬふむゆる"
               "えけせてねへめれ"
               "おこそとのほもよろをん"
               "がざだば"
               "ぎじぢび"
               "ぐずづぶ"
               "げぜでべ"
               "ごぞどぼ"
               "ぱぴぷぺぽ"
               "きゃしゃちゃにゃひゃみゃりゃぎゃじぁぢぁびゃぴゃ"
               "きゅしゅちゅにゅひゅみゅりゅぎゅじゅぢゅびゅぴゅ"
               "きょしょちょにょひょみょりょぎょじょぢょびょぴょ"
               "っぁぃぅぇぉゔー")
# http://japanese-lesson.com/characters/katakana/index.html
KATAKANA = set("アカサタナハマヤラワ"
               "イキシチニヒミリ"
               "ウクスツヌフムユル"
               "エケセテネヘメレ"
               "オコソトノホモヨロヲン"
               "ガザダバ"
               "ギジヂビ"
               "グズヅブ"
               "ゲゼデベ"
               "ゴゾドボ"
               "パピプペポ"
               "キャシャチャニャヒャミャリャギャジャヂャビャピャ"
               "キュシュチュニュヒュミュリュギュジュヂュビュピュ"
               "キョショチョニョヒョミョリョギョジョヂョビョピョ"
               "ッァィゥェォヴー")
KANA = HIRAGANA.union(KATAKANA)
ROMANJI = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
NUMBERS = set("0123456789")
SYMBOLS = set("、・,，。‥…．.！！?？”\"’'￥「」※＊*×・＃#＄$％%＾^＆&（(）)　\n\t\r_=＝ー-＋+/\\")


def contains_kanji(word: str) -> bool:
    for c in word:
        if c not in KANA.union(SYMBOLS).union(ROMANJI).union(NUMBERS):
            return True
    return False


def only_katakana(word: str) -> bool:
    for c in word:
        if c not in KATAKANA:
            return False
    return True


def only_romanji(word: str) -> bool:
    for c in word:
        if c not in ROMANJI.union(NUMBERS).union(SYMBOLS):
            return False
    return True
