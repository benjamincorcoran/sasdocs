import pytest
from sasdocs.objects import SASFile

def test_sasfile_not_processed():
    nullFile = SASFile("aabbcc")
    assert 'path' not in nullFile.__dict__.keys()