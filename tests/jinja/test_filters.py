from mm_base3.server.jinja import empty


def test_empty():
    assert empty(None) == ""
    assert empty("") == ""
    assert empty([]) == ""
    assert empty(0) == 0
