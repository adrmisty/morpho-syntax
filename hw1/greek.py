import re, os, unicodedata
from file import from_json, to_txt

LEMMA_SUFFIXES = ["αω", "εω", "αμαι", "ωμαι", "ομαι", "ος", "ης", "ας", "μα", "ιο", "α", "η", "ο", "ω"]

# ------ VERBS
# https://omilo.com/greek-verbs-for-beginners/
# for verbs, the lemma is first person singular, present
# conjugations A-B1-B2 and passive verbs
VERB_CLASSES = { #
    "b1": ["άω","έω"], # B1 (also with "ώ")
    "b2": ["ώ"], # B2
    "a": ["ω"], # A, first conjugation
    "παθ": ["άμαι", "ώμαι", "ομαι", "ται"], # passive
}

# ------ NOUNS and PRONOUNS
# https://www.foundalis.com/lan/grknouns.htm
# for gender-variable (pro)nouns, lemma is masc singular
NOUN_CLASSES = {
    # masculine
    "masc-ος": ["ος"],  # άνθρωπος - man
    "masc-ας": ["ας"],  #  πατέρας - father
    "masc-ης": ["ης", "ής"],  # ποιητής - poet
    # neuter
    "neut-μα": ["μα"],  # πρόβλημα - problem
    "neut-ι": ["ι", "ός"], # σπίτι - house, ποτάμι/ός - river
    "neut-ο": ["ο", "ό"],   # βιβλίο - book, βουνό - mount
    # feminine
    "fem-α": ["α"],  # χώρα - country
    "fem-η": ["η", "ή"],  # ψυχή - soul
} 

# ------ ADJECTIVES
# https://www.greekgrammar.eu/pdffiles/adjectives.pdf
# for adjectives, lemma is masc singular
ADJ_CLASSES = {
    "ός": ["ρός", "νός", "ακός", "ικός", "ός"],    # καλός - good, πικρός - bitter, πιθανός - possible
    "ος": ["ινος", "ιος", "ος"], # αρχαίος - ancient, δερμάτινος - leather
    "ής": ["ής"],   # σταχτής - ash 
    "ης": ["ης"], # ζηλιάρης - jealous
    "ύς": ["ύς"],  # βαθύς -- deep
}

# ------ POS
CLASSES = {
    "ADJ": ADJ_CLASSES,
    "VERB": VERB_CLASSES,
    "NOUN": NOUN_CLASSES, # noun <-> pron endings
    "PRON": NOUN_CLASSES,
    #"PROPN": NOUN_CLASSES
}


def remove_tonos(word):
    """
    Auxiliary function that removes the τόνος (accents) in order to facilitate
    finding a potential stem for a group of several words and their lemma.

    Parameters
    ----------
    word : str
        word, with potential τόνος

    Returns
    -------
    removed : str
        normalized representation of the parameter word, without accents
    """
    removed = ''.join(
        char for char in unicodedata.normalize('NFD', word)
        if unicodedata.category(char) != 'Mn')
    return removed.lower()

def get_stem(lemma, words):
    """
    Extracts the common τόνος-less, lowercase, stem/root for a list of words referring to a specific lemma, in a given inflectional class.
    
    Parameters
    ----------
    lemma : str
        base form of these word forms
    words : list
        list of word inflections stemming from a specific lemma
    suffixes : list
        list of word suffixes their specific inflectional class present

    Returns
    -------
    stem : str
        common root of these words
    """
    lemma_tonos = remove_tonos(lemma)
    words_tonos = [remove_tonos(form) for form in words]

    # Get initial stem based on common prefix of normalized forms
    stem = os.path.commonprefix([lemma_tonos] + words_tonos)

    # too short, remove a potential suffix
    if len(stem) < 4 or len(words)<2:
        for suffix in LEMMA_SUFFIXES:
            if lemma_tonos.endswith(suffix):
                stem = re.sub(f"{suffix}$", "", lemma_tonos)
                break
    return stem

def get_class(lemma, pos):
    """
    For a list of word forms that represent inflections of the same lemma in terms of gender, number and case,
    relate its endings to a specific pattern in its respective part of speech.

    Parameters
    ----------
    words : list
        word forms of a given lemma
    pos : str
        part of speech of these words 
    Returns
    -------
    suffixes : list
        list of word endings that the words in this POS class present
    """
    for tag, endings in CLASSES[pos].items():
        if any(lemma.endswith(end) for end in endings):
            return tag

    if (pos == "VERB"):
        return "";
    return None # non-generalization

def analyze_inflections(lemma, words, pos):
    """
    For a list of word forms that represent inflections of the same lemma in terms of gender, number and case,
    extract their stem and the inflectional class that they belong to.

    Parameters
    ----------
    lemma : str
        base form of these word forms
    words : list
        word forms of a given lemma
    pos : str
        part of speech these words are 

    Returns
    -------
    stem : str
        common root of the words, their longest possible common prefix
    class_tag : str
        identifier for the suffix pattern class they belong to in their respective POS
    """
    stem = get_stem(lemma, words)    
    class_tag = get_class(lemma, pos)

    if class_tag is None:
        stem = lemma
        class_tag = pos.lower()
    else:
        class_tag = "-".join((pos.lower(), class_tag)) # i.e. verb-b, verb-παθ
    return stem, class_tag

def get_greek_lexicon(filepath):
    """
    From a JSON dictionary containing lemma-pos-word-annotation associations, derive a lexicon
    such that each line contains the following tab-separated-values: [lemma \t stem \t inflectional_class_tag].

    Stem and inflectional class derivation is only done for _explicitly predictable_ parts of speech: nouns, adjectives and adverbs.
    For non-inflectional classes, or those with higher complexity and unpredictability (i.e. articles and determinants in Greek),
    the stem is the lemma itself.

    Parameters
    ----------
    filepath : str
        filepath of the dictionary

    Returns
    -------
    lexpath : list
        list of lexicon entries including lemma, stem and inflectional class-tag
    """

    # load dictionary
    dict = from_json(filepath)
    TO_STEM = ["ADJ", "NOUN", "VERB", "PRON", "PROPN"]

    # each line: [lemma \t stem \t inflectional_class]
    lexicon = []
    
    for lemma, info in dict.items():
        pos = info.get("pos")
        inflections = info.get("inflections", [])

        # no inflections!
        if pos not in TO_STEM:
            stem = lemma
            class_tag = pos.lower()

        # inflected!
        else:
            words = [word for word in inflections]
            stem, class_tag = analyze_inflections(lemma, words, pos)

        # new lexicon entry!
        lexicon.append(f"{lemma}\t{stem}\t{class_tag}")

    return to_txt(lexicon, filepath, "lexicon.txt")
