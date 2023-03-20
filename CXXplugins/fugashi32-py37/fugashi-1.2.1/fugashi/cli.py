from fugashi import GenericTagger, Tagger, build_dictionary
import sys
import fileinput

def main():
    """
    This is a simple wrapper for fugashi so you can test it from the command line.
    Like the mecab binary, it treats each line of stdin as one sentence. You can
    pass tagger arguments here too.
    """
    args = ' '.join(sys.argv[1:])

    # This should work if you specify a different dictionary,
    # but it should also work with the pip unidic.
    # Try the GenericTagger and then try the Unidic tagger.
    try:
        tagger = GenericTagger(args, quiet=True)
    except RuntimeError:
        tagger = Tagger(args)

    for line in fileinput.input([]):
        print(tagger.parse(line.strip()))

def info():
    """Print configuration info."""
    args = ' '.join(sys.argv[1:])
    try:
        tagger = GenericTagger(args, quiet=True)
    except RuntimeError:
        tagger = Tagger(args)
    #TODO get the fugashi version here too
    print("Fugashi dictionary info:")
    print("-----")
    for di in tagger.dictionary_info:
        for field in 'version size charset filename'.split():
            print( (field + ':').ljust(10), di[field])
        print('-----')

def build_dict():
    """EXPERIMENTAL A wrapper for MeCab's user dictionary building command.
    
    This also defaults to utf8.
    """
    # TODO simplify using pip-installed dictionaries as base
    args = sys.argv[0] + " -f utf8 -t utf8 " + ' '.join(sys.argv[1:])
    print(args)
    build_dictionary(args)
