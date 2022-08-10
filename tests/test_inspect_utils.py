import inspect
import textwrap

import pytest

from qmonus_plugin_builder.libs import inspect_utils


class Data(object):
    def standard(
        self,
        id: str,
        name: str = 'name',
    ):
         # comment1

        # comment2
        a: int = 3
        b = 3 + \
3
        c = """
        aaa
        bbb
ccc
    """
        if 10 == \
    20:
            pass

        async def aa():
            await aa()
            raise Exception()
        return

    def comment(self): # comment1
        # comment2
        a = 1
        a = 2

    def one_line_1(self): 1 + \
                         2 + \
                           3

    def one_line_2(self): a = b"""
        aaa
        bbb"""; ("aaa",
        "bbb"); """aaa
        bbb
        ccc"""


@pytest.mark.parametrize('test_data', [
    {
        "args": {
            "code": "    a = 3",
            "size": None,
        },
        "expected": "a = 3"
    },
    {
        "args": {
            "code": "    a = 3",
            "size": 2,
        },
        "expected": "  a = 3"
    },
    {
        "args": {
            "code": inspect.getsource(Data.standard),
            "size": None,
        },
        "expected": textwrap.dedent('''\
            def standard(
                self,
                id: str,
                name: str = 'name',
            ):
                 # comment1

                # comment2
                a: int = 3
                b = 3 + \\
            3
                c = """
                aaa
                bbb
            ccc
            """
                if 10 == \\
            20:
                    pass

                async def aa():
                    await aa()
                    raise Exception()
                return
        ''')
    },
    {
        "args": {
            "code": inspect.getsource(Data.comment),
            "size": None,
        },
        "expected": textwrap.dedent('''\
            def comment(self): # comment1
                # comment2
                a = 1
                a = 2
        ''')
    },
    {
        "args": {
            "code": inspect.getsource(Data.one_line_1),
            "size": None,
        },
        "expected": textwrap.dedent('''\
            def one_line_1(self): 1 + \\
                                 2 + \\
                                   3
        ''')
    },
    {
        "args": {
            "code": inspect.getsource(Data.one_line_2),
            "size": None,
        },
        "expected": textwrap.dedent('''\
            def one_line_2(self): a = b"""
                aaa
                bbb"""; ("aaa",
                "bbb"); """aaa
                bbb
                ccc"""
                ''')
    },
])
def test_outdent_works(test_data: dict):
    code = inspect_utils.outdent(**test_data['args'])
    assert code == test_data['expected']


@pytest.mark.parametrize('test_data', [
    {
        "args": {
            "func": Data.standard,
        },
        "expected": textwrap.dedent('''\
             # comment1

            # comment2
            a: int = 3
            b = 3 + \\
            3
            c = """
            aaa
            bbb
            ccc
            """
            if 10 == \\
            20:
                pass

            async def aa():
                await aa()
                raise Exception()
            return
        ''')
    },
    {
        "args": {
            "func": Data.comment,
        },
        "expected": textwrap.dedent('''\
            # comment1
            # comment2
            a = 1
            a = 2
        ''')
    },
    {
        "args": {
            "func": Data.one_line_1,
        },
        "expected": textwrap.dedent('''\
            1 + \\
            2 + \\
             3
        ''')
    },
    {
        "args": {
            "func": Data.one_line_2,
        },
        "expected": textwrap.dedent('''\
            a = b"""
            aaa
            bbb"""; ("aaa",
            "bbb"); """aaa
            bbb
            ccc"""
        ''')
    },
])
def test_get_function_code_works(test_data: dict):
    code = inspect_utils.get_function_code(**test_data['args'])
    assert code == test_data['expected']
