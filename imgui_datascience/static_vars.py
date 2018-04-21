import unittest


class Bunch(dict):
    """
    `Bunch` is a dictionary that supports attribute-style access, a la JavaScript.
    See original article here :
    http://code.activestate.com/recipes/52308-the-simple-but-handy-collector-of-a-bunch-of-named/?in=user-97991
    `pip install bunch` will install an official version
    """

    def __init__(self, **kw):
        dict.__init__(self, kw)
        self.__dict__ = self

    def __str__(self):
        state = ["%s=%r" % (attribute, value)
                 for (attribute, value)
                 in self.__dict__.items()]
        return '\n'.join(state)


def static_vars(**kwargs):
    def decorate(func):
        statics = Bunch(**kwargs)
        setattr(func, "statics", statics)
        return func

    return decorate


@static_vars(name="Martin")
def _my_function_with_statics():
    statics = _my_function_with_statics.statics
    return "Hello, {0}".format(statics.name)


class TestStaticVars(unittest.TestCase):
    def test(self):
        msg = _my_function_with_statics()
        self.assertEqual(msg, "Hello, Martin")


if __name__ == '__main__':
    unittest.main()
