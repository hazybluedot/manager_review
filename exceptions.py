class UnknownPersonError(Exception):
    pass

class UniquePersonError(Exception):
    def __init__(self, name, found):
        super(Exception, self).__init__(name)
        self.name = name
        self.found = found

    def message(self):
        return "multiple people found for '{}'".format(self.name)

    def __str__(self):
        return self.message()
