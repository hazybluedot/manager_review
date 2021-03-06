import csv
import re

from util import label_to_attr, num_or_none

base_headers = ['Student Id', 'Student Name', 'Section']
tail_headers = ['Letter Grade', 'Total Points', 'Calculated Grade']
gradebook_regex = re.compile(r'([^()]+) ((?:\([-0R]\)\s)+)?\[([0-9]+)\]$')
gradebook_comment_regex = re.compile(r'Comment\s+:\s+([^()]+)$')

def comment_key(item_name):
    return "Comment : " + item_name

class GradebookError(Exception):
    def __init__(self, message):
        self.message = message
        
    def __str__(self):
        return self.message
    
class NoSuchItem(GradebookError):
    def __init__(self, item_name):
        self.item_name
        super().__init__('{}: no such grade item'.format(self.item_name))

    def __str__(self):
        return self.message

class NoSuchRecord(GradebookError):
    def __init__(self, attr_name, rvalue):
        self.attr_name = attr_name
        self.rvalue = rvalue
        super().__init__("{}: no record with value of '{}'".format(self.attr_name, self.rvalue))


class GradebookItem:
    def __init__(pid, name):
        self.pid = name
        self.name = name
        self.adjust = 0

    @property
    def points(self):
        return "{:0.1f}".format(self._points + self.adjust)
    
class GradebookScore:
    def __init__(self, points, comments):
        self.points = num_or_none(float,points)
        self.comments = comments
        
class GradebookRow:
    def __init__(self, pid, name, section):
        self.student_id = pid
        self.student_name = name
        self.section = section
        self.letter_grade = ''
        self.total_points = ''
        self.calculated_grade = ''

    @property
    def pid(self):
        return self.student_id
    
    @property
    def full_name(self):
        return self.student_name
    
    @property
    def name(self):
        return self.student_name

    def score_for(self, item_name):
        return self.items[item_name]
    
    def __getitem__(self, key):
        value = getattr(self, label_to_attr(key), None)
        if value is not None:
            return value
        m = gradebook_regex.match(key)
        if m:
            key = m.group(1)
        if key in self.items:
            return self.items[key].points
        m = gradebook_comment_regex.match(key)
        if m:
            return self.items[m.group(1)].comments
        raise KeyError(key)
    
class GradebookItem:
    def __init__(self, name, flags, points):
        self.name = name
        self.points = points
        self.release = False
        self.include = True
        self.ungraded_nocredit = False
        if flags:
            if '0' in flags:
                self.ungraded_nocredit = True
            if '-' in flags:
                self.include = False
            if 'R' in flags:
                self.release = True
            
    @property
    def flags(self):
        flags = []
        if not self.include:
            flags.append('-')
        if self.release:
            flags.append('R')
        if self.ungraded_nocredit:
            flags.append('0')
        if len(flags) > 0:
            return " {}".format( " ".join( [ "({})".format(flag) for flag in flags ]))
        return ""
        
    @property
    def label(self):
        return "{}{} [{}]".format(self.name, self.flags, self.points)

    @property
    def comment_label(self):
        return "Comment : {}".format(self.name)
    
    def __repr__(self):
        return self.label
    
    def __str__(self):
        return self.__repr__()

def gradebook_items_from_fieldnames(fieldnames):
    gbitems = []
    for fieldname in fieldnames:
        if fieldname not in base_headers + tail_headers:
            m = gradebook_regex.match(fieldname)
            if m:
                name = m.group(1)
                flags = None
                if m.group(2):
                    flags = [ f.strip('()') for f in m.group(2).split() ]
                points = int(m.group(3))
                gbitems.append(GradebookItem(name, flags, points))
    return gbitems
                

def items_from_row(row, items):
    def score(item):
        return row[item.label]
    def comment(item):
        try:
            return row[item.comment_label]
        except KeyError:
            return ""
    return { item.name: GradebookScore(score(item), comment(item)) for item in items }
        
def record_from_row(row, items):
    person = GradebookRow(row['Student Id'], row['Student Name'], row['Section'])
    for label in tail_headers:
        setattr(person, label_to_attr(label), row[label])
    person.items = items_from_row(row, items)
    return person

def object_to_dict(obj, fieldnames):
    return { key: obj[key] for key in fieldnames }

class Gradebook:    
    def __init__(self, csvfile, mode, **kwargs):
        self.encoding = kwargs.pop('encoding', 'utf8')
        self.delimiter = kwargs.pop('delimiter', ',')
        self.mode = mode
        self.csvfile = csvfile
        self.read(self.csvfile, **kwargs)

    def read(self, filename, **kwargs):
        with open(filename, 'r', encoding=self.encoding) as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)
            #self.has_comments = any([ gradebook_comment_regex.match(fieldname) for fieldname in reader.fieldnames ])
            self.items = gradebook_items_from_fieldnames(reader.fieldnames)
            self.records = [ record_from_row(row, self.items) for row in reader ]

    def get_item(self, item_name):
        try:
            item = [ item for item in self.items if item.name == item_name ][0]
        except IndexError:
            raise NoSuchItem(item)
        return item

    def has_item(self, item_name):
        try:
            self.get_item(item_name)
        except NoSuchItem:
            return False
        else:
            return True

    def record_for(self, attr_name, rvalue):
        try:
            record = [ record for record in self.records if getattr(record, attr_name, None) == rvalue ][0]
        except IndexError:
            raise NoSuchRecord(attr_name, rvalue)
        return record

    def records_for(self, item_name):
        item = self.get_item(item_name)
        records = [ record.items[item_name] for record in self.records ]

    def update_item(self, item_name, scores):
        item = self.get_item(item_name)
        for s in scores:
            record = self.record_for('student_id', s.pid)
            r = GradebookScore(s.points, s.comments)
            record.items[item_name] = r

    @property
    def fieldnames(self):
        fields = base_headers
        for item in self.items:
            fields.append(item.label)
            fields.append(item.comment_label)
        fields = fields + tail_headers
        return fields

    def write(self, filename):
        with open(filename, 'w', newline='', encoding=self.encoding) as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=self.delimiter)
            writer.writeheader()
            for record in self.records:
                writer.writerow(object_to_dict(record, self.fieldnames))

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.mode == 'w':
            self.write(self.csvfile)

    def __repr__(self):
        return "items: {}".format(self.items)

def open_gradebook(fname, mode, **kwargs):
    return Gradebook(fname, mode, **kwargs)

if __name__ == '__main__':
    from sys import argv
    
    gradebook = Gradebook(argv[1])
    print(gradebook)
    for record in gradebook.records:
        print(record.name)
        for item in record.items.items():
            print("\t{}".format(item))
    gradebook.write('test_gradebook.csv')
