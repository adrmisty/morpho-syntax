# -----------------------------------------------------------------------------------------

noun_classes = {
        "noun-masc-ος" : "NounMascOs",
        "noun-masc-ας" : "NounMascAs",
        "noun-masc-ης" : "NounMascIs",
        "noun-neut-ι" : "NounNeutI",
        "noun-neut-μα": "NounNeutMa",
        "noun-neut-ο" : "NounNeutO",
        "noun-fem-α" : "NounFemA",
        "noun-fem-η": "NounFemI"
    }

adj_classes = {
        "adj-ός" : "AdjOs1",
        "adj-ος" : "AdjOs2",
        "adj-ής" : "AdjIs",
        "adj-ης" : "AdjIs2",
        "adj-ύς" : "AdjUs"
    }

verb_classes = {
        "verb-a" : "VerbA",
        "verb-παθ" : "VerbPath"
    }

classes = {
    'Noun' : noun_classes,
    'Adj' : adj_classes,
    'Verb' : verb_classes
}

def process_lexicon(txt_file, pos):
    """
    Processes all supported nouns, adjectives and verbs in a .txt lexicon
    and assigns them to a specific inflectional class tag.

    Parameters
    ----------
    txt_file : str
        path containing .txt lexicon file
    """

    with open(txt_file, 'r', encoding='utf-8') as file:
        lexicon_lines = file.readlines()

    entries = []
    pos_classes = classes[pos]

    for line in lexicon_lines:
        parts = line.strip().split('\t')
        if len(parts) == 3:
            word, stem, pos = parts
            
            if pos in pos_classes:
                e = f"{word}:{stem} {pos_classes[pos]} ;"
                entries.append(e)

    return entries

def insert(entries, pos, lines):
    """
    Inserts a set of entries in the lines of a text file 

    Parameters
    ----------
    words : list
        list of words to insert into the file lines
    pos : str
        defines the POS category at which to insert the entries
    lines : list
        lines to be updated by insertion

    """
    # insertion point for nouns (after 'LEXICON Noun')
    for i, line in enumerate(lines):
        if line.strip() == f"LEXICON {pos}":
            j = i + 1
            break
    else:
        raise ValueError("> LEXICON {pos} section not found in the lexc file.")

    updated_lines = (
        lines[:j] +
        ["\n".join(entries) + "\n"] +
        lines[j:]
    )

    return updated_lines



def expand_lexc(txt_file, lexc_file, pos):
    """
    Reads a lexicon text file and expands it by adding nouns, verbs and adjectives
    to their respective identified inflectional class.

    Parameters
    ----------
    txt_file : str
        path to the text file containing the lexicon to analyze
    lexc_file : str
        path to the existing .lexc file to expand
    """
    entries = process_lexicon(txt_file, pos)

    with open(lexc_file, 'r', encoding='utf-8') as file:
        lexc_lines = file.readlines()

    new_lexc = insert(entries, pos, lexc_lines)
    
    with open(lexc_file, 'w', encoding='utf-8') as file:
        file.writelines(new_lexc)

    print(f"> Updated lexc file written with [LEXICON {pos}] to {lexc_file}.")

# must be done step by step , use 'el-empty.lexc' as basis for adding lexicon words
expand_lexc('./hw2/lexc/data/el-lexicon.txt', './hw2/lexc/data/el-full.lexc', 'Noun')
expand_lexc('./hw2/lexc/data/el-lexicon.txt', './hw2/lexc/data/el-full.lexc', 'Adj')
expand_lexc('./hw2/lexc/data/el-lexicon.txt', './hw2/lexc/data/el-full.lexc', 'Verb')

# ^ once all runs above are executed, .lexc file will include all el-lexicon.txt supported words
