from fugashi import Tagger 
import string
import pytest

# NOTE: The bulk test is written against unidic-3.1.0+2021-08-31, fed with
# corpus cc-100, accessible at:
# https://data.statmt.org/cc-100/ja.txt.xz
path_to_jatxt = "ja.txt"

@pytest.mark.skip(reason="This test requires too much data to run in CI.")
def test_bulk():
    tagger = Tagger()
    
    insufficient_paths = []
    incomplete_hypothesis = []
    
    def print_result(i):
        if insufficient_paths:
            print(f"{i} - Not enough paths (counts = {len(insufficient_paths)}): {', '.join(insufficient_paths)}")
        else:
            print(f"{i} - All lines parsed with enough paths.")
            
        if incomplete_hypothesis:
            print(f"{i} - Original line not recovered (counts = {len(incomplete_hypothesis)}): {', '.join(f'{entry[0]}:{entry[1]}' for entry in incomplete_hypothesis)}")
        else:
            print(f"{i} - All lines recovered")
    
    replace_chars = string.whitespace + '\x00'
    log_interval = 65536
    with open(path_to_jatxt, 'r', encoding='utf8') as fin:
        for i, line in enumerate(fin):
            
            # Tagger ignores whitespace and stops parsing at '\x00'.
            # This preprocessing is done for the completeness criteria
            for c in replace_chars:
                line = line.replace(c, '')
                
            if not line:
                continue
            
            paths = tagger.nbestToNodeList(line, 10)
            if len(paths) != 10:
                insufficient_paths.append(str(i))
            
            for j, p in enumerate(paths):
                if ''.join(w.surface for w in p) != line:
                    incomplete_hypothesis.append((i,j))
            
            if i >= log_interval:
                log_interval*=2
                print_result(i)
                
    print_result('Final')

if __name__ == '__main__':
    test_bulk()
