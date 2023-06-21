import NanobindTestModule

def testAddInts():
    assert hasattr(NanobindTestModule, 'addInts')
    c = NanobindTestModule.addInts(3, -7)
    assert isinstance(c, int)
    assert c == -4

def testSqrtFloats():
    assert hasattr(NanobindTestModule, 'sqrtFloat')
    c = NanobindTestModule.sqrtFloat(49.0)
    assert isinstance(c, float)
    assert c == 7.0

def testGetString():
    assert hasattr(NanobindTestModule, 'getString')
    s = NanobindTestModule.getString()
    assert s == "does this work?"

def testGetList():
    assert hasattr(NanobindTestModule, 'getList')
    l = NanobindTestModule.getList(13)
    assert isinstance(l, list)
    assert len(l) == 13
    for idx, elem in enumerate(l):
        assert isinstance(elem, int)
        assert elem == idx * idx

def testPythonVersion():
    assert hasattr(NanobindTestModule, 'getPythonVersion')
    module_ver = NanobindTestModule.getPythonVersion()

    # Check the version matches the interpreter version.
    from sys import version_info as ver
    interp_ver = "%d.%d.%d" % (ver.major, ver.minor, ver.micro)
    assert module_ver == interp_ver

testAddInts()
testSqrtFloats()
testGetString()
testGetList()
testPythonVersion()
