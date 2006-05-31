# vim:sw=4:et

class Aspect(object):
    """Aspect defines the aspect interface that should be implemented by
    aspects.
    """

    def __init__(self, method):
        """This method takes the optional arguments given to the
        weave_method() function.
        """
        pass

    def before(self):
        """Code executed before the weaved method is executed.
        """
        pass

    def after(self, retval, exc):
        """Code executed after the weaved method has been executed.
        """
        pass

def weave_method(method, advice_class, *advice_args, **advice_kwargs):
    advice = advice_class(method, *advice_args, **advice_kwargs)
    advice_before = advice.before
    advice_after = advice.after

    def invoke_advice(*args, **kwargs):
        advice_before()
        try:
            retval = method(*args, **kwargs)
        except Exception, e:
            advice_after(None, e)
            raise
        else:
            advice_after(retval, None)
            return retval

    # Replace the method with our weaved one.
    try:
        class_ = method.im_class
    except:
        # The method is actually a simple function, wrap it in its namespace;
        method.func_globals[method.func_name] = invoke_advice
    else:
        #name = method.__name__
        setattr(class_, method.__name__, invoke_advice)
    return invoke_advice


class LoggerAspect(Aspect):

    def __init__(self, method):
        self.method = method

    def before(self):
        print 'entering', self.method

    def after(self, retval, exc):
        print 'leaving', self.method,
        if exc:
            print 'with exception %s(%s)' % (exc.__class__, exc)
        else:
            print 'with return value', retval


class ReferenceAspect(Aspect):
    """This reference keeps track of objects created by a method.
    A weak reference to those objects is created and appended to reflist.
    """

    def __init__(self, method, reflist):
        self.method = method
        self.reflist = reflist

    def after(self, retval, exc):
        import weakref
        if retval:
            self.reflist.append(weakref.ref(retval))


class TimerAspect(Aspect):
    """This aspect tracks the execution time of a function/method, a bit like
    a profiler.
    The time spend in a function/method is printed to stdout.
    """

    def __init__(self, method):
        import time
        self.timer = time.time
        self.method = method
        self.total_time_spend = 0.0

    def before(self):
        self.current_time = self.timer()

    def after(self, retval, exc):
        elapsed = self.timer() - self.current_time
        self.total_time_spend += elapsed
        print 'Time spend in %s: %f (total: %f)' % (self.method.__name__, elapsed, self.total_time_spend)


if __name__ == '__main__':

    def test_func(arg1, arg2):
        print 'test_func(): arg1:', arg1, ', arg2:', arg2

    weave_method(test_func, LoggerAspect)
    print 'testing test_func()'
    test_func('a', 'b')

    class TestClass(object):

        def test_meth(self, arg1, arg2):
            print 'TestClass.test_meth(): arg1:', arg1, ', arg2:', arg2

        def test_exc(self):
            raise ValueError, 'HELP'

    #print dir(TestClass.test_meth)
    #print TestClass.test_meth.im_class
    #print TestClass.test_meth.im_func
    #print TestClass.test_meth.im_self
    weave_method(TestClass.test_meth, LoggerAspect)
    weave_method(TestClass.test_exc, LoggerAspect)

    tc = TestClass()
    tc.test_meth(1, 2)
    try:
        tc.test_exc()
    except ValueError, e:
        print 'Caught expected exception', e
        import traceback
        traceback.print_exc()
    else:
        raise 'HUH'
