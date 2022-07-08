import re
from math import ceil
from typing import Iterable

from .errors import InvalidValue

__all__ = "number", "calculate"


number = int | float


def is_a_number(string: str) -> bool:
    """Returns whether a string is a number."""
    return string.replace(".", "", 1).isdigit()


def to_number(string: str) -> number:
    """Turns a string into a number, either int or float."""
    try:
        float_value = float(string)
        int_value = ceil(float_value)
        return int_value if int_value == float_value else float_value
    except ValueError as exception:
        raise InvalidValue(string) from exception


def calculated(iterable: Iterable[str]) -> tuple[number, ...]:
    """Turns the elements of an iterable into numbers using `to_number`."""
    return tuple(to_number(x) for x in iterable)


def replace(string: str, match: re.Match | str, new: object) -> str:
    """Replaces the match string with the string representation of the new value in the given string."""
    old = match.group() if isinstance(match, re.Match) else match
    return string.replace(old, str(new))


def calculate_exponentials(string: str) -> str:
    """Calculates exponentials in the format "base ^ power"."""
    for match in set(re.finditer(r"[\d\.]+\^[\d\.]+", string[::-1])):
        power, base = (to_number(x[::-1]) for x in match.group().split("^"))
        string = replace(string, match.group()[::-1], base ** power)
    return string


def calculate_add_sub(string: str) -> str:
    """Calculates additions and subtractions."""
    for match in set(re.finditer(r"([\d\.]+[\+-])+[\d\.]+", string)):
        result, *numbers = calculated(re.split(r"[\+-]", match.group()))
        numbers = iter(numbers)
        for char in match.group():
            if char == "+":
                result += next(numbers)
            elif char == "-":
                result -= next(numbers)
        string = replace(string, match, result)
    return string


def calculate_mul_div(string: str) -> str:
    """Calculates multiplications and divisions."""
    for match in set(re.finditer(r"([\d\.]+[\*\/])+[\d\.]+", string)):
        result, *numbers = calculated(re.split(r"[\*\/]", match.group()))
        numbers = iter(numbers)
        for char in match.group():
            if char == "*":
                result *= next(numbers)
            elif char == "/":
                result /= next(numbers)
        string = replace(string, match, result)
    return string


def clean_parantheses(string: str) -> str:
    """Resolves parantheses."""
    for match in set(re.finditer(r"\(.+\)", string)):
        if string == match.group():
            try:
                inner_left: int = 0
                inner_right: int = -1
                for i, char in enumerate(string):
                    if char == "(":
                        inner_left = i
                    elif char == ")":
                        inner_right = i
                        break

                string = replace(
                    string,
                    string[inner_left : inner_right + 1],
                    calculate(string[inner_left + 1 : inner_right]),
                )
                string = clean_parantheses(string)
            except ValueError:
                string = string[1:-1]
            break

        new = str(calculate(match.group()))
        if (
            string.index(match.group()) > 0
            and string[string.index(match.group()) - 1] not in "+-/*(^."
        ):
            new = f"*{new}"
        string = replace(string, match, new)
    return string


def calculate(string: str) -> number:
    """Makes a calculation."""
    string = clean_parantheses(string.replace(" ", ""))
    if not is_a_number(string):
        for operation in (
            calculate_exponentials,
            calculate_mul_div,
            calculate_add_sub,
        ):
            string = operation(string)

    return to_number(string)
