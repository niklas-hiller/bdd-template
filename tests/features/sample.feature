@SomeMarker
Feature: Check if time passes correctly

    Scenario Outline: Five minutes will pass and time will be updated
        Given The time is <time_before>
        When Five minutes pass
        Then The time is <time_after>

        Examples:
            | time_before   | time_after   |
            | 11:57         | 12:02        |
            | 11:15         | 11:20        |