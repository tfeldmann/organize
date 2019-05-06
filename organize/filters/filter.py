from collections import namedtuple

TargetsFoldersSettings = namedtuple('TargetsFoldersSettings', 'match_files_rec')

class Filter:

    def matches(self, path):
        """ Return True if filter applies to path. False otherwise """
        raise NotImplementedError

    def parse(self, path):
        """ Return an dict of parsed file properties (optional) """
        return {}

    def targets_folders_settings(self):
        return TargetsFoldersSettings(match_files_rec=False)

    def __str__(self):
        """ Return filter name and properties """
        return self.__class__.__name__

    def __repr__(self):
        return '<%s>' % str(self)

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__) and
            self.__dict__ == other.__dict__)
