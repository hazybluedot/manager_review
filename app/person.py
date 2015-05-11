from util import num_or_string, issumable, levenshtein
from scholar.gradebook import GradebookItem
from .exceptions import UniquePersonError
from sys import stdout

def name_prompt(prompt, people, name):
    person = None

    while (person is None):
        print(prompt)
        choices = [ person for person in sorted(people, key=lambda s: levenshtein(s.full_name.lower(), name)) ][:5]
        for number,choice in enumerate(choices):
            print("{}) {}".format(number+1, choice.full_name))
        user_choice = input('Choose one or write in: ')
        try:
            person =  choices[int(user_choice)-1]
        except ValueError as e:
            return user_choice #TODO: move looping until valid name into here?
        except IndexError as e:
            print("Invalid selection")

    return person.full_name

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
              #real_name = input(prompt[:1].upper() + prompt[1:]).lower().strip()
              real_name = name_prompt(prompt[:1].upper() + prompt[1:], people, name).lower().strip()
              found = [ person for person in people if person.full_name.lower().strip() == real_name ]
              self.name_corrector.add_alias(name.lower().strip(), real_name)
              
        if len(found) == 0:
            raise UnknownPersonError(name)
        elif len(found) > 1:
            raise UniquePersonError(name, found)

        return found[0]

    def __call__(self, people, name, **kwargs):
        return self.find_person(people, name, **kwargs)
