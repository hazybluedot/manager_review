from util import num_or_string, issumable
from scholar.gradebook import GradebookItem
from .exceptions import UniquePersonError
from sys import stdout

class people_finder:
    """Find people by fuzzy matching names"""
    
    def __init__(self,name_corrector=None):
        self.name_corrector = name_corrector
        
    def find_person(self, people, name, **kwargs):
        normalized_name = name.lower().strip()
        found = [ person for person in people if person.full_name.lower().strip() == normalized_name ]
        review = kwargs.pop('review', None)
        if len(found) == 0:
            if self.name_corrector:
                normalized_name = self.name_corrector.correct(normalized_name)
                found = [ person for person in people if person.full_name.lower().strip() == normalized_name ]
            while (len(found) < 1):
                prompt = ""
                if review is not None:
                    prompt += "in section {}, Team {} ".format(review.section, review.group)
                prompt += 'who is "{}"? '.format(name)    
                real_name = input(prompt[:1].upper() + prompt[1:]).lower().strip()
                found = [ person for person in people if person.full_name.lower().strip() == real_name ]
                self.name_corrector.add_alias(name.lower().strip(), real_name)
                
        if len(found) == 0:
            raise UnknownPersonError(name)
        elif len(found) > 1:
            raise UniquePersonError(name, found)

        return found[0]

    def __call__(self, people, name, **kwargs):
        return self.find_person(people, name, **kwargs)
