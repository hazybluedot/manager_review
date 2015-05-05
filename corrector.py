# see http://norvig.com/spell-correct.html
import re
import collections

alphabet = 'abcdefghijklmnopqrstuvwxyz'
    
def edits1(word):
    splits     = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes    = [a + b[1:] for a, b in splits if b]
    transposes = [a + b[1] + b[0] + b[2:] for a, b in splits if len(b)>1]
    replaces   = [a + c + b[1:] for a, b in splits for c in alphabet if b]
    inserts    = [a + c + b     for a, b in splits for c in alphabet]
    return set(deletes + transposes + replaces + inserts)

class Corrector:
    def __init__(self, training_words):
       self.model = collections.defaultdict(lambda: 1)
       self.aliases = {}
       for f in training_words:
           self.model[f] += 1

    def known_edits2(self, word):
        return set(e2 for e1 in edits1(word) for e2 in edits1(e1) if e2 in self.model)

    def known(self, words):
       return set(w for w in words if w in self.model)

    def add_alias(self, alias, real):
        self.aliases[alias] = real
       
    def correct(self, word, aliases=None):
        if word in self.aliases:
            return self.aliases[word]
        candidates = self.known([word]) or self.known(edits1(word)) or self.known_edits2(word) or [word]
        return max(candidates, key=self.model.get)

    def load_aliases(self, file_name):
        with open(file_name, 'r') as f:
            for line in f:
                alias, real = line.split(':')
                self.aliases[alias.lower().strip()] = real.strip()
    
    def save_aliases(self, file_name):
        with open(file_name, 'w') as f:
            f.writelines([ '{}: {}\n'.format(k,v) for k,v in self.aliases.items() ])
