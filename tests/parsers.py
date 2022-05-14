import parse as base_parse

from pytest_bdd.parsers import StepParser

class Parser(StepParser):
    """parse step parser."""

    def __init__(self, name, *args, **kwargs):
        """Compile parse expression."""
        super().__init__(name)
        if 'converters' in kwargs:
            self.converters = kwargs['converters']
            del kwargs['converters']
        else:
            self.converters = {}
        self.parser = base_parse.compile(self.name, *args, **kwargs)

    def parse_arguments(self, name):
        """Get step arguments.

        :return: `dict` of step arguments
        """
        variables = self.parser.parse(name).named
        for key in variables:
            if key in self.converters:
                variables[key] = self.converters[key](variables[key])
        return variables

    def is_matching(self, name):
        """Match given name with the step name."""
        try:
            return bool(self.parser.parse(name))
        except ValueError:
            return False