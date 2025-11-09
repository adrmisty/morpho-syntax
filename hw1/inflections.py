from file import to_json

# Corpus tags -> https://universaldependencies.org/treebanks/el_gdt/index.html
INFLECTED = ["ADJ", "DET", "NOUN", "NUM", "PRON", "VERB", "PROPN", "ADV", "AUX"]
NOT_INFLECTED = ["CCONJ", "PART", "SCONJ", "ADP"]

# --------------------------------------------------------------------------------------------------------------
# η	ο	DET	DET	Case=Nom|Definite=Def|Gender=Fem|Number=Sing|PronType=Art
# ηττήθηκε	ηττώμαι	VERB	VERB	Aspect=Perf|Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Pass
# με	με	ADP	ADP	_
# --------------------------------------------------------------------------------------------------------------

def store_in(inflections:dict, word:str, lemma, pos, ann):
    """
    Creates/Updates an entry for a lemma with its respective POS and,
    if inflected, a new word form with its respective annotations.

    Parameters
    ----------
    inflections : dict
        dictionary to save lemma-word-annotation info to
    word : str
        form of a lemma with specific annotations
    lemma : str
        base word the form derives from
    pos : str
        identifier for the part of speech
    ann : list
        list of annotations for a given word form

    Returns
    -------
    inflections : dictionary
        updated with the new information
    """
    annotations = ann.split("|")
    
    # create entry
    if lemma not in inflections:
        # special case: contractions
        if "+" in pos:
            inflections[word] = {'pos': pos, 'annotations': annotations} 

        else:
            # inflected case
            if pos in INFLECTED:
                if lemma is None:
                    lemma = word

                # save the inflections for a lemma in a given word form

                inflections[lemma] = {'pos': pos, 'inflections': {word:annotations}}

            # no inflection! word = lemma
            else:
                inflections[word] = {'pos': pos} 

    else:
        # add new inflections for a lemma
        try:
            if pos in INFLECTED:
                inflections[lemma]['inflections'][word] = annotations
                
        except: 
            # there exists a previous entry for a synonym
            # which is not in its inflected form
            # therefore, delete previous one
            inflections[lemma] = {'pos': pos, 'inflections': {word:annotations}}
            return inflections

    return inflections

def update_contraction(lines, i):
    """
    For contracted multi-word forms (i.e. positional adverbs and determinants),
    process a word form's respective individual parts and include their POS
    and annotation information in the inflections entry.

    These individual parts, asumming a basic contraction of 2 words, are
    considered to be the next two lines in processing.

    Parameters
    ----------
    lines : list
        word, lemma, pos and annotations information
    i : int
        index of the line being processed at the moment

    Returns
    -------
    pos : str
        new, combined part of speech for a contraction (i.e. ADP+DET)
    annotations : str
        new, combined annotations of the contraction
    """

    pos = []
    annotations = []

    for j in range(2):

        # eof
        if i >= len(lines):
            break
        
        # next line
        i += 1
        line = lines[i].strip()
        if not line:
            continue

        info = line.split('\t')
        if len(info) < 5:
            continue
        _, _, next_pos, _, next_anns = info

        # Append the POS and features to the buffer
        pos.append(next_pos)
        if (next_anns != "_"):
            annotations.append(next_anns)
    
    # i.e. "ADP+DET" for positional adverb and determinant contractions
    pos = "+".join(pos)
    annotations = "|".join(annotations)

    return pos, annotations

def update(inflections, info, lines, i):
    """
    Updates the inflections being built with new information regarding a given word,
    where this info includes:
        - the word
        - its lemma (base form)
        - its pos (part of speech)
        - annotations
    
    Parameters
    ----------
    inflections : dictionary
        key is a given lemma, related to a specific part of speech and morphological annotations
    info : tuple
        word, lemma, pos and annotations information
    lines : list
        lines being processed from the file
    i : int
        index of the line being processed at the moment

    Returns
    -------
    inflections : dictionary
        updated with the new information
    """
    
    word, lemma, pos, _, ann = info
           
    # lemma or POS is "_"
    if lemma == "_" or pos == "_":
        pos, ann = update_contraction(lines, i)
    inflections = store_in(inflections, word, lemma, pos, ann)

    return inflections

def get_inflections(filepath: str):
    """
    From an annotated .txt file, each line being made up of a word tab-separated
    with its respective tags, process them to be added to a inflections.

    Parameters
    ----------
    filpeath : str
        filepath of the .txt annotated file

    Returns
    -------
    inflections : dict
        dictionary containing a inflections of word-tag pairs
    """

    # dictionary that stores word-lemma-annotation associations
    inflections = {} 

    # read and process file
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        i = 0

        while i < len(lines):            
            # each word is followed by 4 tab-separated-values
            tabs = lines[i].strip().split('\t')
            if len(tabs) != 5:
                continue
            inflections = update(inflections, tabs, lines, i)
            i += 1


    return to_json(inflections, "inflections.json", filepath)
