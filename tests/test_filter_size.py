from organize.filters import FileSize
import mock

def test_matching():
    situations = [
        (1, FileSize(smaller='1b', bigger='2b'), False),
        (1, FileSize(bigger='1b', smaller='2b'), True),
        (1, FileSize(bigger='1.000001b'), False),
        (1, FileSize(smaller='1.000001B'), True),
        (1, FileSize(smaller='1.000001'), True),
        (1, FileSize(smaller='1', bigger='0.001kb'), True),
        (0, FileSize(smaller='1'), True),
        (0, FileSize(bigger='1'), False),
        (0, FileSize(smaller='1', bigger='1b'), False),
        (100000000000, FileSize(bigger='99.99999GB'), True),
        (42, FileSize(), True),
    ]

    for mocksize, filter, result in situations:
        # override '_get_file_size' class function to return the byte values specified in the test
        def new_get_file_size(self, _):
            return mocksize
        with mock.patch.object(FileSize, '_get_file_size', new=new_get_file_size):
            assert filter.matches('/whatever/path') == result
