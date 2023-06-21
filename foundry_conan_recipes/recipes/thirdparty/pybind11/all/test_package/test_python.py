import Pybind11TestModule

def testAddInts():
    assert "addInts" in dir(Pybind11TestModule)
    c = Pybind11TestModule.addInts(3, -7)
    assert isinstance(c, int)
    assert c == -4

def testSqrtFloats():
    assert "sqrtFloat" in dir(Pybind11TestModule)
    c = Pybind11TestModule.sqrtFloat(49.0)
    assert isinstance(c, float)
    assert c == 7.0

def testGetString():
    assert "getString" in dir(Pybind11TestModule)
    s = Pybind11TestModule.getString()
    try:
        assert isinstance(s, basestring)  # Python 2.
    except NameError:
        assert isinstance(s, str)  # Python 3.
    assert s == "does this work?"

def testGetVector():
    assert "getVector" in dir(Pybind11TestModule)
    v = Pybind11TestModule.getVector(13)
    assert isinstance(v, list)
    assert len(v) == 13
    for idx, elem in enumerate(v):
        assert isinstance(elem, int)
        assert elem == idx * idx

def testPythonVersion():
    assert "getPythonVersion" in dir(Pybind11TestModule)
    module_ver = Pybind11TestModule.getPythonVersion()

    # Check the version matches the interpreter version.
    from sys import version_info as ver
    interp_ver = "%d.%d.%d" % (ver.major, ver.minor, ver.micro)
    assert module_ver == interp_ver

testAddInts()
testSqrtFloats()
testGetString()
testGetVector()
testPythonVersion()
