import csv
from operator import itemgetter, attrgetter
from itertools import groupby
import re

from .person import Person

response_filter_regex = re.compile(r'Part ([1-9]+), Question ([1-9]+), (.*)')

def question_id(field):
    m = response_filter_regex.match(field)
    if m:
        return (int(m.group(1)), int(m.group(2)))
    return None

fields = {
    'pid': 'User Name',
    'order': 'Order of Submission (1=first)',
    'firstname': 'First Name',
    'lastname': 'Last Name'
}

def response_attribute(r):
    if response_filter_regex.match(r).group(3).lower() == 'response':
        return 'response'
    return 'comments'

class QuestionResponse:
    def __init__(self, part, question, response, **kwargs):
        self.part = part
        self.question = question
        self.response = None
        self.comments = None
        for k,r in response.items():
            setattr(self, response_attribute(k), r)

        response_filter = kwargs.pop('response_filter', None)
        if response_filter:
            self.response = response_filter(self.qid)(self.response)

    @property
    def result(self):
        return self.response
    
    @property
    def qid(self):
        return (self.part, self.question)

    def __repr__(self):
        return '<QuestionResponse {} {}>'.format((self.part, self.question), (self.response, self.comments))

class QuizSubmission(Person):
    def __init__(self, row, **kwargs):
        super().__init__(row[fields['firstname']], row[fields['lastname']], row[fields['pid']])
        self.submission_order = row[fields['order']]
        self._responses = [ QuestionResponse(k[0], k[1], { k: row[k] for k in g }, **kwargs)
                           for k, g in groupby(sorted([ k for k in row.keys() if question_id(k) ], key=question_id), question_id) ]
            
    def response_map(self, fn):
        return { fn(k): v for k,v in self._responses }

    def value_map(self, fn):
        return { k: fn(k)(v) for k,v in self._responses }

    def responses(self,part,question=None):
        """Return all responses for a single part, or a single response for a
particular part and question number"""
        
        if question:
            return [ r for r in self._responses if r.qid == (part,question) ][0]
        return [ r for r in self._responses if r.part == part ]

    def __repr__(self):
        return "<QuizSubmisson {}: {} questions>".format(super().__repr__(), len(self._responses))
    
class QuizSubmissions:
    def __init__(self, filename, **kwargs):
        self.rows = []
        print("opening quiz submission file {}".format(filename))
        with open(filename, 'r', encoding='utf8') as f:
            reader = csv.DictReader(f)
            self.fieldnames = reader.fieldnames
            self.responses = [ QuizSubmission(row, **kwargs) for row in reader ]

    @property
    def latest(self):
        return [ max(g, key=attrgetter('submission_order'))
               for k, g in groupby(sorted(self.responses, key=attrgetter('full_name')), attrgetter('full_name')) ]

    def latest_for(self, pid):
        try:
            return sorted([ row for row in self.rows if row[pid_field] == pid ], key=itemgetter('Order of Submission (1=first)'))[-1]
        except IndexError:
            return None

    @property    
    def keys(self):
        return [ row[pid_field] for row in self.results ]

        
if __name__ == '__main__':
    import sys

    qs = QuizSubmissions(sys.argv[1])
    results = qs.latest
    
