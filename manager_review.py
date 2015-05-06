#!/usr/bin/env python3

from sys import stdout, stderr
from itertools import groupby
import textwrap

from corrector import Corrector
from person import people_finder
from scholar import tests_quizzes as tq
from scholar.gradebook import Gradebook
from scholar.person import Person
from util import flatten_list, label_to_attr, num_or_none

question_number_map = { 2: 'Interdependence',
                        3: 'Team Planning',
                        4: 'Team Dynamics',
                        5: 'Interpersonal Relationships',
                        6: 'Comments'
                    }

review_attrs = [ label_to_attr(v) for v in question_number_map.values() ]

class ManagersReview(Person):
    """A manager's review for a single person"""
    def __init__(self, fname, lname, pid):
        self.first_name = fname
        self.last_name = lname
        self.pid = pid
        self.submission_points = 0
        self.comments = ""
        self.__instructor_points = 0
        self.labels = [ quality for quality in question_number_map.values() ]
        for quality in self.labels:
            setattr(self, '_' + label_to_attr(quality), [])
            
    def add_reviews(self, reviews):
        for r in reviews:
            self.add_review(r)
    @property
    def peer_comments(self):
        return self._comments
    
    def add_review(self, review):
        for rr in review.reviews:
            label = '_' + label_to_attr(question_number_map[rr[0]])
            attr = getattr(self, label)
            attr.append(rr[1])
            setattr(self, label, attr)

    def __getitem__(self, label):
        return getattr(self, '_' + label_to_attr(label))

    @property
    def scores(self):
        return { label: self.score_for(label) for label in self.labels if not label == 'Comments' }

    def score_for(self, label):
        scores = [ score for score in self.__getitem__(label) if score is not None ]
        try:
            return sum(scores)/len(scores)
        except ZeroDivisionError:
            return 0

    @property
    def instructor_points(self):
        return self.__instructor_points

    @instructor_points.setter
    def instructor_points(self, val):
        try:
            self.__instructor_points = float(val)
        except ValueError:
            pass
        
    @property
    def points(self):
        """Return string representation of points for inclusion in gradebook"""
        numpoints = sum(self.scores.values()) + self.instructor_points + self.submission_points
        return "{:0.1f}".format(numpoints)
    
    def __repr__(self):
        representation = ""
        for label,score in self.scores.items():
            representation += "{}: {}\n".format(label, score)
        return representation
    
class ManagersReviewResponse():
    
    def __init__(self, responses):
        self.full_name = [ response.result for response in responses if response.question == 1 ][0]
        #super().__init__(fname, lname, pid)
        self.reviews = [ (response.question,response.result) for response in responses if response.question > 1 ]
        
    def __repr__(self):
        return "{} has {} questions".format(self.full_name, len(self.reviews))
    
class ManagersReviewSubmission(Person):
    def __init__(self, submission):
        super().__init__(submission.first_name, submission.last_name, submission.pid)
        self.submission = submission
        self.reviews = [ ManagersReviewResponse(self.submission.responses(p)) for p in range(2,8) ]
        self.submitted = num_or_none(int, submission.submission_order) is not None
        
    def review_for(self, name):
        try:
            return [ review for review in self.reviews if review.full_name == name ][0]
        except IndexError:
            return None

    def __repr__(self):
        return "<ManagersReviewSubmission ({}) {} reviews>".format(super().__repr__(), len(self.reviews))
    
def int_or_none(val):
    try:
        return int(val)
    except ValueError:
        return None
    
def response_filter(q):
    if q[0] > 1 and q[1] == 1:
        return lambda s: s[3:]
    elif q[0] > 1 and q[1] > 1 and q[1] < 6:
        return int_or_none
    else:
        return lambda s: s

def name_collector(result, fuzzy_filter):
    name = result.response(p,1).response.lower().strip()
    return fuzzy_filter(name).full_name

def run(args):
    qs = tq.QuizSubmissions(args.input_file, response_filter=response_filter)

    reviews = [ ManagersReview(r.first_name, r.last_name, r.pid) for r in qs.latest ]
    submissions = [ ManagersReviewSubmission(result) for result in qs.latest if num_or_none(int,result.submission_order) is not None ]

    for submission in submissions:
        review = [ review for review in reviews if review.full_name == submission.full_name ][0]
        review.submission_points = args.submission_points

        
    name_corrector = Corrector( [ review.full_name.lower().strip() for review in reviews ], alias=args.aliases )
    find_people=people_finder(name_corrector)

    def reviewee(review):
        #return review.full_name
        return find_people([r for r in reviews], review.full_name).full_name.lower().strip()
    responses = flatten_list([ submission.reviews for submission in submissions ])
    #for response in sorted(responses, key=reviewee):
    #    print(response)
    #sys.exit(0)

    for k, g in groupby(sorted(responses, key=reviewee), reviewee):
        review = [ review for review in reviews if review.full_name.lower().strip() == k ][0]
        review.add_reviews(g)

        print("{}".format(review.full_name))
        for label,score in review.scores.items():
            print("\t{}: {:0.1f}".format(label,score))
        for comment in review.peer_comments:
            try:
                comment_lines = textwrap.wrap('"' + comment + '"',72)
            except AttributeError:
                stderr.write('AttributeError: {}, {}: attempt to wrap "{}"\n'.format(person.full_name, label, comment))
            except TypeError:
                stderr.write('TypeError: {}, {}: attempt to wrap "{}"\n'.format(person.full_name, label, comment))
            else:
                stdout.writelines( [ '\t' + comment + '\n' for comment in comment_lines ])
        peer_subtotal = sum(review.scores.values())
        print("\tpeer subtotal: {:0.2f}".format(peer_subtotal))
        print("\tsubmission: {}".format(review.submission_points))
        if args.interactive:
            instructor_score = 0
            while instructor_score == 0:
                instructor_input = input('Instructor score for {}: '.format(review.full_name))
                try:
                    instructor_score = float(instructor_input)
                except ValueError:
                    stderr.write("'{}' is not a number\n".format(instructor_input))
            review.instructor_points = instructor_score
            if args.comments:
                review.comments = input('Instructor comments for {}: '.format(review.full_name))
                
        print("Total points for {}: {}".format(review.full_name, review.points))
            #print("{}: {}".format(result.full_name, [ result.response(p,1).response for p in range(2,8) ]))

    if args.gradebook and args.name:
        try:
            gradebook = Gradebook(args.gradebook)
        except FileNotFoundError as e:
            stderr.write('No such file: {}\n'.format(args.gradebook))
        else:
            gradebook.update_item(args.name, reviews)
            gradebook.write(args.gradebook)
            stdout.write('Grades')
            if args.comments:
                stdout.write(' and comments')
            stdout.write('written to {}, item {}\n'.format(args.gradebook, args.name))
            
if __name__ == '__main__':
    import sys
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input csv file exported from Scholar Tests&Quizes')
    parser.add_argument('--interactive','-i', action='store_true', help='be interactive, ask for instructor contribution')
    parser.add_argument('--gradebook', '-g', help='gradebook CSV (no structure, grades only)')
    parser.add_argument('--name','-n', default="Manager's Review 2", help='gradebook item name')
    parser.add_argument('--aliases', '-a', default='aliases.txt', help='location of aliases.txt for fuzzy name matching')
    parser.add_argument('--comments', '-c', action='store_true', help='export comments to gradebook')
    parser.add_argument('--submission-points', default=3, help='number of points just for submitting a manager review')
    
    args = parser.parse_args()

    run(args)
