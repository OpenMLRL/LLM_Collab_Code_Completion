class ArgumentParser:
    """
    This is a class for parsing command line arguments to a dictionary.
    """

    def __init__(self):
        """
        Initialize the fields.
        self.arguments is a dict that stores the args in a command line
        self.requried is a set that stores the required arguments
        self.types is a dict that stores type of every arguments.
        >>> parser.arguments
        {'key1': 'value1', 'option1': True}
        >>> parser.required
        {'arg1'}
        >>> parser.types
        {'arg1': 'type1'}
        """
        self.arguments = {}
        self.required = set()
        self.types = {}

    def parse_arguments(self, command_string):
        """
        Parses the given command line argument string and invoke _convert_type to stores the parsed result in specific type in the arguments dictionary.
        Checks for missing required arguments, if any, and returns False with the missing argument names, otherwise returns True.
        :param command_string: str, command line argument string, formatted like "python script.py --arg1=value1 -arg2 value2 --option1 -option2"
        :return tuple: (True, None) if parsing is successful, (False, missing_args) if parsing fails,
            where missing_args is a set of the missing argument names which are str.
        >>> parser.parse_arguments("python script.py --arg1=value1 -arg2 value2 --option1 -option2")
        (True, None)
        >>> parser.arguments
        {'arg1': 'value1', 'arg2': 'value2', 'option1': True, 'option2': True}
        """
        args = command_string.split()[2:]
        parsed_args = {}
        for arg in args:
            if arg.startswith('--'):
                key, value = arg[2:].split('=', 1)
                parsed_args[key] = value
            elif arg.startswith('-'):
                key = arg[1:]
                parsed_args[key] = True
            else:
                parsed_args[arg] = True
        for key, value in parsed_args.items():
            if key in self.types:
                try:
                    self.arguments[key] = self._convert_type(key, value)
                except ValueError:
                    self.arguments[key] = value
            else:
                self.arguments[key] = value
        missing = self.required - set(self.arguments.keys())
        if missing:
            return (False, missing)
        return (True, None)

    def get_argument(self, key):
        """
        Retrieves the value of the specified argument from the arguments dictionary and returns it.
        :param key: str, argument name
        :return: The value of the argument, or None if the argument does not exist.
        >>> parser.arguments
        {'arg1': 'value1', 'arg2': 'value2', 'option1': True, 'option2': True}
        >>> parser.get_argument('arg2')
        'value2'
        """
        return self.arguments.get(key, None)

    def add_argument(self, arg, required=False, arg_type=str):
        """
        Adds an argument to self.types and self.required.
        Check if it is a required argument and store the argument type.
        If the argument is set as required, it wull be added to the required set.
        The argument type and name are stored in the types dictionary as key-value pairs.
        :param arg: str, argument name
        :param required: bool, whether the argument is required, default is False
        :param arg_type:str, Argument type, default is str
        >>> parser.add_argument('arg1', True, 'int')
        >>> parser.required
        {'arg1'}
        >>> parser.types
        {'arg1': 'int'}
        """
        self.required.add(arg)
        self.types[arg] = arg_type

    def _convert_type(self, arg, value):
        """
        Try to convert the type of input value by searching in self.types.
        :param value: str, the input value in command line
        :return: return corresponding value in self.types if convert successfully, or the input value oherwise
        >>> parser.types
        {'arg1': int}
        >>> parser._convert_type('arg1', '21')
        21
        """
        if arg in self.types:
            type_func = self.types[arg]
            try:
                return type_func(value)
            except (ValueError, TypeError):
                return value
        return value

import unittest

class ArgumentParserTestParseArguments(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser()

    # key value arguments
    def test_parse_arguments_1(self):
        command_str = "script --name=John --age=25"
        self.parser.add_argument("name")
        self.parser.add_argument("age", arg_type=int)

        result, missing_args = self.parser.parse_arguments(command_str)

        self.assertTrue(result)
        self.assertIsNone(missing_args)
        self.assertEqual(self.parser.get_argument("name"), "John")
        self.assertEqual(self.parser.get_argument("age"), 25)

    # switches options
    def test_parse_arguments_2(self):
        command_str = "script --verbose -d"
        self.parser.add_argument("verbose", arg_type=bool)
        self.parser.add_argument("d", arg_type=bool)

        result, missing_args = self.parser.parse_arguments(command_str)

        self.assertTrue(result)
        self.assertIsNone(missing_args)
        self.assertEqual(self.parser.get_argument("verbose"), True)
        self.assertEqual(self.parser.get_argument("d"), True)

    # miss required
    def test_parse_arguments_3(self):
        command_str = "script --name=John"
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=True, arg_type=int)

        result, missing_args = self.parser.parse_arguments(command_str)

        self.assertFalse(result)
        self.assertEqual(missing_args, {"age"})

    def test_parse_arguments_4(self):
        command_str = "script --name=John"
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=False, arg_type=int)

        result, missing_args = self.parser.parse_arguments(command_str)

        self.assertTrue(result)
        self.assertEqual(missing_args, None)

    def test_parse_arguments_5(self):
        command_str = "script --name=John"
        self.parser.add_argument("name")
        self.parser.add_argument("age", arg_type=int)

        result, missing_args = self.parser.parse_arguments(command_str)

        self.assertTrue(result)
        self.assertEqual(missing_args, None)

class ArgumentParserTestGetArgument(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser()

    # key exists
    def test_get_argument_1(self):
        self.parser.arguments = {"name": "John"}
        result = self.parser.get_argument("name")
        self.assertEqual(result, "John")

    # key not exists
    def test_get_argument_2(self):
        self.parser.arguments = {"name": "John", "age": 25}
        result = self.parser.get_argument("age")
        self.assertEqual(result, 25)

    def test_get_argument_3(self):
        self.parser.arguments = {"name": "John", "age": "25", "verbose": True}
        result = self.parser.get_argument("verbose")
        self.assertEqual(result, True)

    def test_get_argument_4(self):
        self.parser.arguments = {"name": "Amy", "age": 25, "verbose": True, "d": True}
        result = self.parser.get_argument("d")
        self.assertEqual(result, True)

    def test_get_argument_5(self):
        self.parser.arguments = {"name": "John", "age": 25, "verbose": True, "d": True, "option": "value"}
        result = self.parser.get_argument("option")
        self.assertEqual(result, "value")


class ArgumentParserTestAddArgument(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser()

    def test_add_argument(self):
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=True, arg_type=int)

        self.assertEqual(self.parser.required, {"age"})
        self.assertEqual(self.parser.types, {"name": str, "age": int})

    def test_add_argument_2(self):
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=False, arg_type=int)
        self.parser.add_argument("verbose", arg_type=bool)

        self.assertEqual(self.parser.required, set())
        self.assertEqual(self.parser.types, {"name": str, "age": int, "verbose": bool})

    def test_add_argument_3(self):
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=False, arg_type=int)
        self.parser.add_argument("verbose", arg_type=bool)
        self.parser.add_argument("d")

        self.assertEqual(self.parser.required, set())
        self.assertEqual(self.parser.types, {"name": str, "age": int, "verbose": bool, "d": str})

    def test_add_argument_4(self):
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=False, arg_type=int)
        self.parser.add_argument("verbose", arg_type=bool)
        self.parser.add_argument("d")
        self.parser.add_argument("option")

        self.assertEqual(self.parser.required, set())
        self.assertEqual(self.parser.types, {"name": str, "age": int, "verbose": bool, "d": str, "option": str})

    def test_add_argument_5(self):
        self.parser.add_argument("name")
        self.parser.add_argument("age", required=False, arg_type=int)
        self.parser.add_argument("verbose", arg_type=bool)
        self.parser.add_argument("d")
        self.parser.add_argument("option")
        self.parser.add_argument("option2", arg_type=bool)

        self.assertEqual(self.parser.required, set())
        self.assertEqual(self.parser.types, {"name": str, "age": int, "verbose": bool, "d": str, "option": str, "option2": bool})


class ArgumentParserTestConvertType(unittest.TestCase):

    def setUp(self):
        self.parser = ArgumentParser()

    def test_convert_type_1(self):
        self.parser.types = {"age": int}
        result = self.parser._convert_type("age", "25")
        self.assertEqual(result, 25)

    # fail
    def test_convert_type_2(self):
        self.parser.types = {"age": int}
        result = self.parser._convert_type("age", "twenty-five")
        self.assertEqual(result, "twenty-five")

    def test_convert_type_3(self):
        self.parser.types = {"age": int}
        result = self.parser._convert_type("age", "25")
        self.assertEqual(result, 25)

    def test_convert_type_4(self):
        self.parser.types = {"age": int, "verbose": bool}
        result = self.parser._convert_type("verbose", "True")
        self.assertEqual(result, True)
    
    def test_convert_type_5(self):
        self.parser.types = {"age": int, "verbose": bool}
        result = self.parser._convert_type("verbose", "False")
        self.assertEqual(result, True)


class ArgumentParserTestMain(unittest.TestCase):
    def test_main(self):
        parser = ArgumentParser()
        command = "script --arg1=21 --option1 -arg2 value -option2"

        parser.add_argument('arg1', required=True, arg_type=int)
        parser.add_argument('arg2')

        self.assertEqual(parser.required, {'arg1'})
        self.assertEqual(parser.types, {'arg1': int, 'arg2': str})
        self.assertEqual(parser.arguments, {})

        parser.parse_arguments(command)
        arguments = {'arg1': 21, 'option1': True, 'arg2': 'value', 'option2': True}
        self.assertEqual(parser.arguments, arguments)