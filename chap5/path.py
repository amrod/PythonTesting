from os.path import isfile, isdir, exists, join
from os import makedirs, rmdir, unlink
from unittest import TestCase, main

class path:

    r"""
    Instances of this class represent a file path, and facilitate
    several operations on files and directories.
    Its most surprising feature is that it overloads the division
    operator, so that the result of placing a / operator between two
    paths (or between a path and a string) results in a longer path,
    representing the two operands joined by the system's path
    separator character.
    """
    def __init__(self, target):
        self.target = target

    def exists(self):
        return exists(self.target)

    def isfile(self):
        return isfile(self.target)

    def isdir(self):
        return isdir(self.target)

    def mkdir(self, mode=493):
        makedirs(self.target, mode)

    def rmdir(self):
        if self.isdir():
            rmdir(self.target)
        else:
            raise ValueError('Path does not represent a directory')

    def delete(self):
        if self.exists():
            unlink(self.target)
        else:
            raise ValueError('Path does not represent a file')

    def open(self, mode="r"):
        return open(self.target, mode)

    def __div__(self, other):
        if isinstance(other, path):
            return path(join(self.target, other.target))
        return path(join(self.target, other))

    def __repr__(self):
        return '<path %s>' % self.target

import tempfile
import os
import shutil
from mocker import Mocker


class test_path(TestCase):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.tmpdir2 = tempfile.mkdtemp(dir=self.tmpdir)
        (fd1, self.fn1) = tempfile.mkstemp(dir=self.tmpdir)
        (fd2, self.fn2) = tempfile.mkstemp(dir=self.tmpdir)
        os.write(fd1, 'This is a test.')
        os.close(fd1)
        os.close(fd2)

    def tearDown(self):
        shutil.rmtree(self.tmpdir)

    def test_constructor(self):
        to_test = path(self.tmpdir2)
        self.assertEqual(to_test.target, self.tmpdir2)

    def test_exists(self):
        to_test = path(self.tmpdir2)
        self.assertTrue(to_test.exists(), msg='"%s" exists, but reported as not existing.')

    def test_isfile(self):
        to_test_dir = path(self.tmpdir2)
        to_test_file = path(self.fn1)

        self.assertFalse(to_test_dir.isfile(), msg='"%s" is a directory, not a file.' % to_test_dir)
        self.assertTrue(to_test_file.isfile(), msg='"%s" is a file, not a directory.' % to_test_file)

    def test_isdir(self):
        to_test_dir = path(self.tmpdir2)
        to_test_file = path(self.fn1)

        self.assertTrue(to_test_dir.isdir(), msg='"%s" is a directory, not a file.' % to_test_dir)
        self.assertFalse(to_test_file.isdir(), msg='"%s" is a file, not a directory.' % to_test_file)

    def test_mkdir(self):
        new_dir = os.path.join(self.tmpdir, 'newdir')
        to_test = path(new_dir)
        to_test.mkdir()

        self.assertTrue(os.path.exists(new_dir), msg='Directory was not created: "%s"' % new_dir)

    def test_rmdir(self):
        to_test_dir = path(self.tmpdir2)
        to_test_file = path(self.fn1)

        mocker = Mocker()
        mock_is_dir = mocker.replace(to_test_dir.isdir)
        mock_is_dir()
        mocker.result(True)
        mocker.replay()

        to_test_dir.rmdir()

        mocker.restore()
        mocker.verify()

        self.assertFalse(os.path.exists(self.tmpdir2), msg='Directory was not deleted: "%s"' % self.tmpdir2)
        self.assertRaises(ValueError, to_test_file.rmdir)

    def test_delete(self):
        to_test_dir = path('some\\non-existing\\file')
        to_test_file = path(self.fn1)

        mocker = Mocker()
        mock_exists = mocker.replace(to_test_file.exists)
        mock_exists()
        mocker.result(True)
        mocker.replay()

        to_test_file.delete()

        mocker.restore()
        mocker.verify()

        self.assertFalse(os.path.exists(self.fn1), msg='File was not deleted: "%s"' % self.fn1)
        self.assertRaises(ValueError, to_test_dir.delete)

    def test_open(self):
        to_test = path(self.fn1)
        fd = to_test.open()
        line = fd.readline()
        fd.close()

        self.assertEqual(line, 'This is a test.', msg='Line read from file is not as expected.')

    def test_join(self):
        lp = path(r'path\on\left')
        rp = path(r'path\on\right')
        np = lp / rp
        self.assertEqual(np.target, path(r'path\on\left\path\on\right').target)

if __name__ == '__main__':
    main()