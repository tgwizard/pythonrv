# -*- coding: utf-8 -*-
import unittest

from pythonrv import rv
from pythonrv.formalrv import formal_spec, make_assert, make_next, make_if

class TestFormalDetails(unittest.TestCase):
    def test_assert_cases(self):
        self.assertEquals(len(make_assert()), 0)

        self.assertTrue(make_assert(True)[0](None))
        self.assertFalse(make_assert(False)[0](None))

        self.assertTrue(make_assert(lambda e: True)[0](None))
        self.assertFalse(make_assert(lambda e: False)[0](None))

        a = make_assert(True, False, lambda e: False, lambda e: e != 5)
        self.assertEquals(len(a), 4)
        self.assertTrue(a[0](None))
        self.assertFalse(a[1](None))
        self.assertFalse(a[2](None))

        self.assertTrue(a[3](None))
        self.assertTrue(a[3](4))
        self.assertFalse(a[3](5))

    def test_if_required_attributes(self):
        with self.assertRaises(AssertionError):
            make_if()
        with self.assertRaises(AssertionError):
            make_if(True)
        with self.assertRaises(AssertionError):
            make_if(exp=False)
        with self.assertRaises(AssertionError):
            make_if(then=False)
        with self.assertRaises(AssertionError):
            make_if(els=False)
        with self.assertRaises(AssertionError):
            make_if(then=False,els=False)
        with self.assertRaises(AssertionError):
            make_if(exp=False,els=False)

    def test_if_cases(self):
        self.assertTrue(make_if(exp=True,then=True)[0](None))
        self.assertTrue(make_if(True,True)[0](None))

        self.assertTrue(make_if(exp=True,then=True,els=False)[0](None))
        self.assertTrue(make_if(True,True,False)[0](None))

        self.assertFalse(make_if(exp=True,then=False)[0](None))
        self.assertFalse(make_if(exp=True,then=False,els=True)[0](None))

        self.assertTrue(make_if(exp=False,then=False)[0](None))
        self.assertTrue(make_if(exp=False,then=False,els=True)[0](None))
        self.assertFalse(make_if(exp=False,then=True,els=False)[0](None))

    def test_no_history(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            s = make_assert(lambda e: (len(e.history) == 1,"Too much history"),
                    make_next(lambda: s))
            return s

        a = M()
        for i in range(20):
            a.m(i)



class TestFormalRV(unittest.TestCase):
    def test_basic_assert(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            return make_assert(True, False, 5 == 3)

        a = M()
        with self.assertRaises(AssertionError):
            a.m(1)
        # second time no error, since we have no loop in the specification
        a.m(1)

    def test_basic_assert_with_message(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            return make_assert((False, "buffy"))

        a = M()
        with self.assertRaises(AssertionError) as e:
            a.m(1)
        self.assertEquals(e.exception.message, "buffy")
        a.m(1)

    def test_basic_assert_with_different_inputs(self):
        for i in range(5):
            class M(object):
                def m(self, x):
                    pass

            @rv.monitor(m=M.m)
            @formal_spec
            def spec2():
                return make_assert(lambda e: e.fn.m.inputs[1] != 2)

            a = M()
            if i == 2:
                with self.assertRaises(AssertionError):
                    a.m(i)
            a.m(-1)
            a.m(123)

    def test_next(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            a = make_assert(False)
            return make_next(a)

        a = M()
        a.m(1)
        with self.assertRaises(AssertionError):
            a.m(1)
        a.m(1)

    def test_more_assert_with_next_loop(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            asserts = make_assert(True,
                    lambda e: e.fn.m.inputs[1] > 0,
                    lambda e: e.fn.m.inputs[1] != 5,
                    make_next(lambda: asserts))

            return asserts

        a = M()

        a.m(1)
        a.m(2)
        with self.assertRaises(AssertionError):
            a.m(0)
        a.m(1337)
        with self.assertRaises(AssertionError):
            a.m(5)
        a.m(98789374)
        with self.assertRaises(AssertionError):
            a.m(5)
        with self.assertRaises(AssertionError):
            a.m(-123487689)

    def test_simple_if(self):
        class M(object):
            def m(self, x):
                pass

        @rv.monitor(m=M.m)
        @formal_spec
        def spec():
            return make_if(True, make_assert(False))

        a = M()
        with self.assertRaises(AssertionError):
            a.m(0)
        a.m(0)
        a.m(0)
        a.m(0)

    def test_simple_if_else(self):
        for i in range(2):
            class M(object):
                def m(self, x):
                    pass

            @rv.monitor(m=M.m)
            @formal_spec
            def spec():
                return make_if(lambda e: e.fn.m.inputs[1] == 0,
                        make_assert((False,"heisenberg0")),
                        make_assert((False,"heisenberg1")))

            a = M()
            with self.assertRaises(AssertionError) as e:
                a.m(i)
            self.assertEquals(e.exception.message, "heisenberg%d" % i)

            a.m(0)
            a.m(0)
            a.m(0)
