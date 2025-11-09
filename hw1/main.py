from file import from_conllu
from inflections import get_inflections
from greek import get_greek_lexicon
import sys

def main(path):
    """
    Extract the lexicon given by a file containing Universal Dependency Tree information
    for a given language.

    For more information, view https://universaldependencies.org/treebanks/el_gdt/index.html.

    Parameters
    ----------
    path : str
        filepath of the [.conllu] file containing UDT information, view https://github.com/UniversalDependencies/UD_Greek-GDT/blob/master/el_gdt-ud-train.conllu.

    Returns
    -------
    infpath : str
        filepath of the file containing the lemma-word-annotation associations

    lexpath : str
        filepath of the file containing the lexicon

    Author
    -------
    - Adriana Rodríguez Flórez
    - adrirflorez@gmail.com
    - Course: NPFL094 Morphological and Syntactic Analysis
    - Version: ÚFAL 24/25; October 2024 
    """
    # retrieve all lemma-word form associations
    # with the respective inflections and annotations for each
    infpath = get_inflections(from_conllu(path))
   
    # retrieve lexicon from inflections
    # [lemma stem inflectional_class_tag]
    lexpath = get_greek_lexicon(infpath)

    return infpath,lexpath

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("(!) Run: python main.py <filename>\n> python main.py el-tagged.conllu\n")
        sys.exit(1)

    # filename not hardcoded!
    filename = sys.argv[1]
    main(filename)
