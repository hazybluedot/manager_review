class Person:
    def __init__(self, fname, lname, pid):
        self.first_name = fname
        self.last_name = lname
        self.pid = pid

    @property
    def full_name(self):
        return self.first_name + " " + self.last_name
    

    def __repr__(self):
        return "{}, {} ({})".format(self.last_name, self.first_name, self.pid)
