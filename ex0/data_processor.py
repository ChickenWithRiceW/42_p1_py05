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

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self._data:
            raise Exception("No data available")
        return self._data.pop(0)

    def _store(self, value: str) -> None:
        self._data.append((self._data_rank, value))
        self._data_rank += 1


class NumericProcessor(DataProcessor):
    # Takes in data and validates it "Again" to be sure
    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise Exception("Improper numeric data")

        if isinstance(data, (int, float)):
            self._store(str(data))
            return

        if isinstance(data, list):
            for x in data:
                self._store(str(x))

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
            self._store(data)
            return
        if isinstance(data, list):
            for s in data:
                self._store(s)

    # Validates the input
    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True

        # Checks if everything in the list is a str
        if isinstance(data, list):
            return all(isinstance(x, str) for x in data)

        return False


# ! How tf should I parse this in a good way
# ! Only procceses Logs in the format of {"log_level: ", "log_message: "}
class LogProcessor(DataProcessor):
    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise Exception("Improper log data")

        if isinstance(data, dict):
            self._store(f"{data['log_level']}: {data['log_message']}")

        if isinstance(data, list):
            for d in data:
                for k, v in d.items():
                    self._store(f"{k}: {v}")

    @staticmethod
    def _is_valid_log(data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        if len(data.keys()) != 2:
            return False

        key0, key1 = data.keys()
        if key0 != "log_level" or key1 != "log_message":
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
