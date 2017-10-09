class Filter:

    def matches(self, path):
        """ Return True if filter applies to path. False otherwise """
        raise NotImplementedError

    def parse(self, path):
        """ Return an dict of parsed file properties (optional) """
        return {}

    def __str__(self):
        """ Return filter name and properties """
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % str(self)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
