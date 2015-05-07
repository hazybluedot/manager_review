#!/usr/bin/env python3

from sys import stdout, stderr
from itertools import groupby
import textwrap
from os import name as os_name

from app.corrector import Corrector
from app.person import people_finder
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
    def __init__(self, fname, lname, pid, **kwargs):
        self.first_name = fname
        self.last_name = lname
        self.pid = pid
        self.section = None
        self.group = None
        response = kwargs.pop('response', None)
        if response is not None:
            self.section = response.responses(1,1).result
            self.group = response.responses(1,2).result
        self.submission_points = 0.0
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
        if review.section is not None:
            self.section = review.section
        if review.group is not None:
            self.group = review.group    
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
    def peer_score(self):
        return sum(self.scores.values())

    @property
    def points(self):
        """Return string representation of points for inclusion in gradebook"""
        numpoints = self.peer_score + self.instructor_points + self.submission_points
        return "{:0.1f}".format(numpoints)

    @points.setter
    def points(self, total_points):
        total_points = float(total_points)
        self.instructor_points = total_points - (self.peer_score + self.submission_points)
        
    def __repr__(self):
        representation = ""
        for label,score in self.scores.items():
            representation += "{}: {}\n".format(label, score)
        return representation
    
class ManagersReviewResponse():
    
    def __init__(self, responses, section, group):
        self.full_name = [ response.result for response in responses if response.question == 1 ][0]
        self.section = section
        self.group = group
        #super().__init__(fname, lname, pid)
        self.reviews = [ (response.question,response.result) for response in responses if response.question > 1 ]
        
    def __repr__(self):
        return "{} has {} questions".format(self.full_name, len(self.reviews))
    
class ManagersReviewSubmission(Person):
    def __init__(self, submission):
        def has_name(p):
            return len(self.submission.responses(p,1).response.strip()) > 0
        super().__init__(submission.first_name, submission.last_name, submission.pid)
        self.submission = submission
        self.section = self.submission.responses(1,1).result
        self.group = self.submission.responses(1,2).result
        self.reviews = [ ManagersReviewResponse(self.submission.responses(p), self.section, self.group) for p in range(2,8) if has_name(p) ]
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

def prompt_for_score(review):
    instructor_score = 0
    if os_name == 'nt':
        print("Press Ctrl+C and then Enter to quit (changes will be saved)")
    while instructor_score == 0:
        instructor_prompt = 'Instructor score for {}'.format(review.full_name)
        if review.instructor_points > 0:
            instructor_prompt += ' ({:0.1f})'.format(review.instructor_points)
        instructor_prompt += ':'
                
        instructor_input = input(instructor_prompt)

        try:
            instructor_score = float(instructor_input)
        except ValueError:
            if len(instructor_input) == 0 and review.instructor_points > 0:
                return review.instructor_points
            stderr.write("'{}' is not a number\n".format(instructor_input))
    return instructor_score

def prompt_for_comments(review, args):
    if args.comments:
        if len(review.comments.strip()) > 0:
            print('Current instructor comments: "{}"'.format(review.comments))
        instructor_comments = input('Instructor comments for {}: '.format(review.full_name))
        return instructor_comments
    
def collect_responses(responses, reviews, reviewee, gradebook, args):
    for k, g in groupby(sorted(responses, key=reviewee), reviewee):
        review = [ review for review in reviews if review.full_name.lower().strip() == k ][0]
        review.add_reviews(g)

    def section_team_name(review):
        return review.section + review.group + review.full_name
    
    for review in sorted(reviews, key=section_team_name):
        print("record for {}".format(review.pid))
        record = [ record for record in gradebook.records if record.pid == review.pid][0]
        score = record.score_for(args.name)
        try:
            review.points = score.points
        except TypeError:
            pass
        
        review.comments = score.comments
        
        print("{} ({}, Team {})".format(review.full_name, review.section, review.group))
        for label,score in review.scores.items():
            print("\t{}: {:0.1f}".format(label,score))
        print("\t")
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
        print("\t")
        print("\tpeer subtotal: {:0.2f}".format(peer_subtotal))
        print("\tsubmission: {}".format(review.submission_points))
        if args.interactive:
            try:
                instructor_score = prompt_for_score(review)
            except (KeyboardInterrupt, EOFError):
                print("")
                return
            else:
                review.instructor_points = instructor_score

            try:
                instructor_comments = prompt_for_comments(review, args)
            except (KeyboardInterrupt, EOFError):
                print("")
                return
            else:
                if len(instructor_comments) > 0:
                    review.comments =  instructor_comments
                
        print("Total points for {}: {}".format(review.full_name, review.points))
            #print("{}: {}".format(result.full_name, [ result.response(p,1).response for p in range(2,8) ]))

def run(args):
    qs = tq.QuizSubmissions(args.input_file,
                            response_filter=response_filter,
                            encoding=args.input_file_encoding,
                            delimiter=args.input_file_delimiter)

    reviews = [ ManagersReview(r.first_name, r.last_name, r.pid, response=r) for r in qs.latest ]
    submissions = [ ManagersReviewSubmission(result) for result in qs.latest if num_or_none(int,result.submission_order) is not None ]

    for submission in submissions:
        review = [ review for review in reviews if review.full_name == submission.full_name ][0]
        review.submission_points = args.submission_points

    gradebook = None
    if args.gradebook and args.name:
        try:
            gradebook = Gradebook(args.gradebook, encoding=args.gradebook_encoding, delimiter=args.gradebook_delimiter)
        except FileNotFoundError as e:
            stderr.write('No such file: {}\n'.format(args.gradebook))

        if not gradebook.has_item(args.name):
            stderr.write('{}: no such item in gradebook\n'.format(args.name))
            return
            
    name_corrector = Corrector( [ review.full_name.lower().strip() for review in reviews ], alias=args.aliases )
    find_people=people_finder(name_corrector)

    def reviewee(review):
        #return review.full_name
        return find_people([r for r in reviews], review.full_name, review=review).full_name.lower().strip()

    responses = flatten_list([ submission.reviews for submission in submissions ])
    #for response in sorted(responses, key=reviewee):
    #    print(response)
    #sys.exit(0)

    collect_responses(responses, reviews, reviewee, gradebook, args)
    
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
            stdout.write(" written to {}, item name '{}'\n".format(args.gradebook, args.name))
            
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
    parser.add_argument('--input_file_encoding', default='utf-8', help='encoding of tests&quizzes file')
    parser.add_argument('--input_file_delimiter', default=',', help='delimiting character of tests&quizzes file')
    parser.add_argument('--gradebook_encoding', default='utf=8', help='encoding of gradebook file')
    parser.add_argument('--gradebook_delimiter', default=',', help='delimiting character of gradebook file')
    
    args = parser.parse_args()

    run(args)
