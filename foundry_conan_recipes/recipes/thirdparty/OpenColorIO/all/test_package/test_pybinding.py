import PyOcioBindTestModule
import PyOpenColorIO

t = PyOpenColorIO.DisplayTransform()
# Ensure that this returns true as it is a transform type.
if (not PyOcioBindTestModule.checkPyOCIOTransform(t)):
    raise Exception("Test Failed, {} should be an OCIO Transform".format(t))

# Ensure that this returns false, as this is definitely not a transform type
a = 2
if (PyOcioBindTestModule.checkPyOCIOTransform(a)):
    raise Exception("Test Failed, {} is not an OCIO Transform type".format(a))
