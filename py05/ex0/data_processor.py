from typing import Any
from abc import ABC, abstractmethod

"""
NOTE
The isinstance() function checks if specified object is of the specified type
Example:
    value = 12
    isinstance(value, int)
This would return true as the value is of object int

all() returns True if bool(x) is True for all values x in the iterable
Example:
    mixed_dict = [True, False]
    all(x for x in mixed_dict)
This would return False as one of the values inside are not True
Note that this works with functions inside the all() as well
"""


# This is a abstract class. You cannot create a instance of it
class DataProcessor(ABC):
    def __init__(self):
        self._data = []
        self._data_rank = 0

    # This is a abstractmethod you need to have this in your child class,
    # otherwise you cannot create one
    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        # ? What happens if empty?
        cpy = self._data_rank
        self._data_rank += 1
        return (cpy, self._data.pop(0))


class NumericProcessor(DataProcessor):
    # Takes in data and validates it "Again" to be sure
    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise Exception("Improper numeric data")
        else:
            self._data.append(str(data))

    # Validates the input
    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)):
            return True

        # Checks if everything in the list is eather a int or float
        if isinstance(data, list):
            return all(isinstance(x, (int, float)) for x in data)

        return False


class TextProcessor(DataProcessor):
    # Takes in data and validates it "Again" to be sure
    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise Exception("Improper text data")
        if isinstance(data, str):
            self._data.append(str(data))
            return
        if isinstance(data, list):
            

    # Validates the input
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True

        # Checks if everything in the list is a str
        if isinstance(data, list):
            return all(isinstance(x, str) for x in data)

        return False


class LogProcessor(DataProcessor):
    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise Exception("Improper log data")
        else:
            self._data.append(str(data))

    @staticmethod
    def _is_valid_log(data: Any) -> bool:
        if not isinstance(data, dict):
            return False
        return all(isinstance(k, str) and
                   isinstance(v, str) for k, v in data.items())

    # Checks if everything in the list is eather a int or float
    def validate(self, data: Any) -> bool:
        if self._is_valid_log(data):
            return True

        if isinstance(data, list):
            return all(self._is_valid_log(x) for x in data)

        return False


def main() -> None:
    num_pros = NumericProcessor()
    num_pros.ingest(12)
    num_pros.ingest(1.2)
    print(num_pros.output())
    print(num_pros.output())


if __name__ == "__main__":
    main()