from util import num_or_string, issumable
from scholar.gradebook import GradebookItem
from exceptions import UniquePersonError

class ReviewItem(GradebookItem):
    dimensions = [ 'interdependence', 'team planning', 'team dynamics', 'interpersonal relationships' ] 
    def __init__(pid, name):
        super(GradebookItem, self).__init__(pid,name)

class Question:
    def __init__(self, name, response, total_points):
        self.name = name
        self.response = response
        self.points = 0
        self.total_points = total_points
        
    def __repr__(self):
        return '<Question: {} "{}" ({}/{})>'.format(self.name, self.response, self.points, self.total_points)
    
class Person:
    def __init__(self, last_name, first_name, pid):
        self.last_name = last_name
        self.first_name = first_name
        self.pid = pid
        self.submission_order = None
        self.responses = {}
        self.reviews = {}
        self.grade_scale = None
        self.total_score = 0
        self.comments = None
        
    @property
    def full_name(self):
        return self.first_name + ' ' + self.last_name

    @property
    def points(self):
        return "{:0.1f}".format(float(self.total_score))

    def add_review(self, review):
        for key, value in review.responses.items():
            key = key.strip()
            if key in self.reviews:
                self.reviews[key]  += [num_or_string(value)]
            else:
                self.reviews[key] = [num_or_string(value)]
        
    @property
    def scores(self):
        def num_or_scale(num):
            if self.grade_scale:
                try:
                    return self.grade_scale[num]
                except KeyError:
                    return num
            else:
                return num
            
        def make_score(results):
            numbers = [ num_or_scale(num) for num in results if issumable(num) ]
            score = None
            if len(numbers) > 0:
                score = sum(numbers)/len(numbers)
            return score
        
        return { question: make_score(review) for question,review in self.reviews.items() if make_score(review) is not None }
            
            
    def __repr__(self):
        return '<Person({}, {}, {}): {}>'.format(self.last_name, self.first_name, self.pid,
                                                  ','.join([ r.__repr__() for r in self.responses.values()])
        )
        
class PersonReview:
    def __init__(self, name, response_filter=None):
        self.name = name
        self.responses = {}
        self.response_filter = response_filter
        
    def add_response(self, key, value):
        if self.response_filter:
            m = self.response_filter.match(key)
            if m:
                self._add_response(m.group(1),value)
        else:
            self._add_respose(key,value)

    def _add_response(self, key, value):
        if key in self.responses:
            self.responses[key].append(value)
        else:
            self.responses[key] = value

    def __repr__(self):
        return '<Review({}): responses({})>'.format(self.name, ','.join([ "'{}'".format(k) for k in self.responses.keys()]))

class people_finder:
    """Find people by fuzzy matching names"""
    
    def __init__(self,name_corrector=None):
        self.name_corrector = name_corrector
        
    def find_person(self, people, name):
        normalized_name = name.lower().strip()
        found = [ person for person in people if person.full_name.lower().strip() == normalized_name ]

        if len(found) == 0:
            if self.name_corrector:
                normalized_name = self.name_corrector.correct(normalized_name)
                found = [ person for person in people if person.full_name.lower().strip() == normalized_name ]
            while (len(found) < 1):
                real_name = input('Who is {}? '.format(name)).lower().strip()
                found = [ person for person in people if person.full_name.lower().strip() == real_name ]
                self.name_corrector.add_alias(name.lower().strip(), real_name)
                
        if len(found) == 0:
            raise UnknownPersonError(name)
        elif len(found) > 1:
            raise UniquePersonError(name, found)

        return found[0]

    def __call__(self, people, name):
        return self.find_person(people, name)
