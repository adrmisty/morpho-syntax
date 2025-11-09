import re, json, sys

TO_IGNORE = ["PUNCT", "Foreign=Yes", "SYM", "Abbr=Yes", "X"]

def from_json(filepath):
    """
    Reads a dictionary from a filepath into a JSON object.

    Parameters
    ----------
    filepath : str
        file path the JSON dictionary is stored in

    Returns
    -------
    dictjson : json
        dictionary object
    """
    with open(filepath, 'r', encoding='utf-8') as file:
        dictjson = json.load(file)
    return dictjson

def to_json(dictionary, ext, filepath):
    """
    Saves a dictionary representing into a file, in a specific filepath.

    Parameters
    ----------
    dictionary : dict
        multi-level dictionary object containing lexicon information
    ext : str
        filename extension, i.e. "lexicon.txt" or "inflections.json"
    filepath : str
        file path the information was initially processed from

    Returns
    -------
    path : str
        filepath of the file containing the dictionary
    """
    path = filepath.replace("tagged.txt", ext)
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(dictionary, file, indent=4, ensure_ascii=False)
        print(f"> Inflections saved to: {path}!")
        return path
    except Exception as e:
        print(f"> An error ocurred when saving the inflections: {e}")

def to_txt(lines, filepath, ext):
    """
    Saves a tab-separated lexicon such that each line displays a lemma,
    its stem and its inflectional class tag.

    Parameters
    ----------
    entries : list
        list of lexicon entry strings
    filepath : str
        file path the information was initially processed from

    Returns
    -------
    path : str
        filepath of the file containing the lexicon
    """

    path = filepath.replace("inflections.json", ext)
    lines.sort()
    try:
        with open(path, 'w', encoding='utf-8') as f:
            for lexeme in lines:
                f.write(lexeme + '\n')
            print(f"> Lexicon saved to: {path}!")
            return path
    except Exception as e:
        print(f"(!) An error ocurred when saving the lexicon: {e}\n")
        sys.exit(-1)

def from_conllu(filepath):
    """
    From the Dependency Tree file for Modern Greek in .conllu format, extract all word and annotations information
    and copy it onto a new clean text file.

    This processing includes several tasks, such as the removal of:
        - foreign names written in Greek alphabet
        - punctuation marks
        - cardinal and ordinal numerals
    
    The resulting file should present the following format:
        - several groups of words belonging to the same sentence, with a blank line as a separator
        - each line in the group contains tab-separated values
            * the first value is the word to analyze, the second its base value (lexeme), followed by morpholog. annotations
        - words are not lowercased by default in order to avoid losing information related to proper nouns

    Parameters
    ----------
    filepath : str
        filepath of the .conllu file containing UDT information

    Returns
    -------
    path : str
        filepath of newly-created file
    """

    # read corpus file (.conllu)
    with open(filepath, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    txt = []
    for line in lines:
        # skip comments / blank lines
        if line.startswith("#"):
            continue

        # i.e. "2	Μάντσεστερ	Μάντσεστερ	X	X	Foreign=Yes	4	nsubj	_	_"
        parts = line.split('\t', 1)
        
        if len(parts) > 1:
            annotations = parts[1].split('\t')
            # annotations to ignore and numbers [0,9]
            if (any(n in TO_IGNORE for n in annotations)  or re.search(r'\d', annotations[0])):
                continue 

            to_add = parts[1].split('\t', 5)
            word = f"{to_add[0].lower()}\t"
            txt.append(word + ('\t'.join(to_add[1:-1])) + "\n")
    
    # write results
    path = filepath.rsplit('.', 1)[0] + ".txt"
    with open(path, 'w', encoding='utf-8') as file:
        file.writelines(txt)

    # ηττήθηκε	ηττώμαι	VERB	VERB	Aspect=Perf|Mood=Ind|Number=Sing|Person=3|Tense=Past|VerbForm=Fin|Voice=Pass
    print(f"> {filepath} processed and saved to: {path}!")
    return path
