from os.path import abspath, dirname, join, realpath
from sys import path

path.append(dirname(realpath(__file__)))

ROOT_DIR = abspath(join(dirname(__file__), "../"))
TEST_DIR = join(ROOT_DIR, "tests")
