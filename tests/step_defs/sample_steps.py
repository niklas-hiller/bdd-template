from pytest_bdd import given, when, then
from tests.parser_defs.parsers import Parser

from obj_defs.time import Time

@given(Parser("The time is {time_before}",
              converters = {
                    "time_before": Time.parse
                  }), target_fixture = "time")
def some_setup(time_before : Time):
    assert isinstance(time_before, Time)
    return time_before

@when(Parser("{minutes_amount} minutes pass",
             converters = {
                    "minutes_amount": int
                  }))
def some_action(time : Time, minutes_amount : int):
    assert isinstance(minutes_amount, int)
    time.minutes += minutes_amount

@then(Parser("The time is {time_after}",
             converters = {
                    "time_after": Time.parse
                  }))
def some_assertion(time : Time, time_after : Time):
    assert isinstance(time, Time)
    assert isinstance(time_after, Time)
    assert time.hours == time_after.hours \
        and time.minutes == time_after.minutes \
        and time.seconds == time_after.seconds, \
            f"The expected time was {time_after}, but it was actually {time}"
        
