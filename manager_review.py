#!/usr/bin/env python3

grade_scale = { 3: 5,
               2: 4,
               1: 2,
               0: 0
}

points_for_submission = 5
total_points = 50

import csv
import sys
import re

from itertools import groupby
from operator import attrgetter, itemgetter
import textwrap
import argparse

from corrector import Corrector
from exceptions import UnknownPersonError, UniquePersonError
from util import flatten_list, issumable
from person import people_finder, Person, PersonReview
from gradebook import Gradebook

response_filter_regex = re.compile(r'Part [1-6], (Question [1-6]), Response')

pivot_column = re.compile(r'Part [2-6], Question 1, Response')

question_number_map = { 2: 'Interdependence',
                        3: 'Team Planning',
                        4: 'Team Dynamics',
                        5: 'Interpersonal Relationships',
                        6: 'Comments'
                    }

question_labels = { v: k for k,v in question_number_map.items() }

def question_label_sort_key(key):
    return question_labels[key]

question_map = { re.compile(r'Question {}'.format(num)): label for num,label in question_number_map.items() }

people = []

def question_label(question):
    for qregexp,label in question_map.items():
        if qregexp.match(question):
            return label
    return None

def filter_by_latest_submission(people):
    """Return a list of unique people selecting by choosing each
submission with max submission order"""
    
    result = [ max(g, key=attrgetter('submission_order'))
               for k, g in groupby(people, lambda x: getattr(x, 'last_name') + getattr(x, 'first_name')) ]
    return result
            
def split_responses(row, pivot_column, fieldnames):
    """Take a single row containing a person's response, pivot on
pivot_column adding each pivoted entry as a response this person made"""
    
    person = Person(row['Last Name'], row['First Name'], row['User Name'])
    person.section = row['Part 1, Question 1, Response']
    person.group_num = int(row['Part 1, Question 2, Response'])
    person.submission_order = int(row['Order of Submission (1=first)'])
    
    current_name = None
    for key in fieldnames:
        if pivot_column.match(key):
            current_name = row[key][3:] # values have a '1: ' prefix, what remains after this is the name
            person.responses[current_name] = PersonReview(current_name, response_filter=response_filter_regex)
        elif current_name is not None:
            person.responses[current_name].add_response(key, row[key])

    return person

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='input csv file exported from Scholar Tests&Quizes')
    parser.add_argument('--interactive','-i', action='store_true', help='be interactive, ask for instructor contribution')
    parser.add_argument('--gradebook', '-g', help='gradebook CSV (no structure, grades only)')
    parser.add_argument('--name','-n', default="Manager's Review", help='gradebook item name')
    parser.add_argument('--output', '-o', default=sys.stdout, help='output file')
    parser.add_argument('--comments', '-c', action='store_true', help='export comments to gradebook')
    args = parser.parse_args()

    people = None    
    with open(args.input_file, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        people = filter_by_latest_submission([ split_responses(row, pivot_column, reader.fieldnames) for num,row in enumerate(reader) ])
        
    # fuzzy name corrector to ease handling of misspelled names
    name_corrector = Corrector( [ person.full_name.lower().strip() for person in people ] )
    try:
        name_corrector.load_aliases('aliases.txt')
    except FileNotFoundError:
        pass
    find_person = people_finder(name_corrector)

    # collect reviews
    reviews = flatten_list([ person.responses.values() for person in people ])    
    for review in reviews:
        try:
            person = find_person(people, review.name)
            person.add_review(review)
        except UnknownPersonError as e:
            sys.stderr.write(str(e) + '\n')
        except UniquePersonError as e:
            sys.stderr.write(str(e) + '\n')

    name_corrector.save_aliases('aliases.txt')
                         
    for person in people:
        person.grade_scale = grade_scale
        scores = { question_label(question): score for question,score in person.scores.items() }
        sys.stdout.write('{}:\n'.format(person.full_name))
        responses = { question_label(question): review for question,review in person.reviews.items() if question_label(question) }

        subtotal = sum(scores.values()) + points_for_submission
        for label in sorted(responses, key=question_label_sort_key):
            review = responses[label]
            score = None
            if not label == 'Comments':
                score = scores[label]

            if score is not None:
                sys.stdout.write('\t{}: {:0.2} ({})\n'.format(label, score, review))
            elif label == 'Comments':
                for comment in review:
                    try:
                        comment_lines = textwrap.wrap('"' + comment + '"',72)
                    except AttributeError:
                        sys.stderr.write('AttributeError: {}, {}: attempt to wrap "{}"\n'.format(person.full_name, label, comment))
                    except TypeError:
                        sys.stderr.write('TypeError: {}, {}: attempt to wrap "{}"\n'.format(person.full_name, label, comment))
                    else:
                        sys.stdout.writelines( [ '\t' + comment + '\n' for comment in comment_lines ])
                if args.comments:
                    person.comments = "\n".join(review)

        sys.stdout.write('\tsubtotal: {:0.3} ({:0.3} left)\n'.format(subtotal, total_points-subtotal))
        sys.stdout.write('\n')
        if args.interactive:
            instructor_score = 0
            while instructor_score == 0:
                instructor_input = input('Instructor score: ')
                try:
                    instructor_score = float(instructor_input)
                except ValueError:
                    sys.stderr.write("'{}' is not a number\n".format(instructor_input))

            person.total_score = subtotal+instructor_score
        else:
            person.total_score = subtotal + 25
        
    if args.gradebook and args.name:
        try:
            gradebook = Gradebook(args.gradebook)
        except FileNotFoundError as e:
            sys.stderr.write('No such file: {}\n'.format(args.gradebook))
        else:
            gradebook.update_item(args.name, people)
            gradebook.write(args.gradebook)
