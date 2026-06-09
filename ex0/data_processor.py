from typing import Any
from abc import ABC, abstractmethod

"""
NOTE
The isinstance() function checks if specified object is of the specified type
Example:
    value = 12
    isinstance(value, int)
This would return true as the value is of object int
Note: subclasses like bool would still be accepted because their parent is int

all() returns True if bool(x) is True for all values x in the iterable
Example:
    mixed_dict = [True, False]
    all(x for x in mixed_dict)
This would return False as one of the values inside are not True
Note that this works with functions inside the all() as well
"""


# This is a abstract class. You cannot create a instance of it
class DataProcessor(ABC):
    def __init__(self) -> None:
        self._data: list[tuple[int, str]] = []
        self._data_rank = 0

    # This is a abstractmethod you need to have this in your child class,
    # otherwise you cannot create one
    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    # Outputs the stored data using a list containing tuples
    def output(self) -> tuple[int, str]:
        if not self._data:
            raise Exception("No data available")
        return self._data.pop(0)

    # Helper function to store the data with its rank
    def _store(self, value: str) -> None:
        self._data.append((self._data_rank, value))
        self._data_rank += 1


class NumericProcessor(DataProcessor):
    def ingest(self, data: int | float | list[int | float]) -> None:

        # Takes in data and validates it "Again" to be sure
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

        # Reject bool as it is a subclass of int
        # If converted to str it would display True or False
        if isinstance(data, bool):
            return False
        if isinstance(data, (int, float)):
            return True

        # Checks if everything in the list is either a int or float
        if isinstance(data, list):
            return all(isinstance(x, (int, float))
                       and not isinstance(x, bool) for x in data)

        return False


class TextProcessor(DataProcessor):
    def ingest(self, data: str | list[str]) -> None:

        # Takes in data and validates it "Again" to be sure
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


# ! Only processes Logs in the format of {"log_level: ", "log_message: "}
class LogProcessor(DataProcessor):
    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise Exception("Improper log data")

        if isinstance(data, dict):
            self._store(f"{data['log_level']}: {data['log_message']}")

        # Loops trough the list of dict's and extract it keys
        if isinstance(data, list):
            for d in data:
                self._store(f"{d['log_level']}: {d['log_message']}")

    @staticmethod
    def _is_valid_log(data: Any) -> bool:
        if not isinstance(data, dict):
            return False

        # If the keys don't match the format quit
        keys = set(data.keys())
        if keys != {"log_level", "log_message"}:
            return False

        # Verify that the keys and vales in dict are only strings
        return all(isinstance(k, str) and
                   isinstance(v, str) for k, v in data.items())

    # Checks if everything in the list is either a int or float
    def validate(self, data: Any) -> bool:
        if self._is_valid_log(data):
            return True

        if isinstance(data, list):
            return all(self._is_valid_log(x) for x in data)

        return False


def main() -> None:
    print("=== Code Nexus - Data Processor ===\n")

    print("Testing Numeric Processor...")

    # Creating instance of NumericProcessor
    num_proc = NumericProcessor()

    print(f" Trying to validate input '42': {num_proc.validate(42)}")
    print(f" Trying to validate input 'Hello': {num_proc.validate('Hello')}")

    print(" Test invalid ingestion of string 'foo' without prior validation:")
    try:
        num_proc.ingest("foo")
    except Exception as e:
        print(f" Got exception: {e}")

    print(" Processing data: [1, 2, 3, 4, 5]")
    num_proc.ingest([1, 2, 3, 4, 5])
    print(" Extracting 3 values...")
    for i in range(3):
        rank, value = num_proc.output()
        print(f" Numeric value {rank}: {value}")

    print("\nTesting Text Processor...")
    text_proc = TextProcessor()

    print(f" Trying to validate input '42': {text_proc.validate(42)}")

    print(" Processing data: ['Hello', 'Nexus', 'World']")
    text_proc.ingest(['Hello', 'Nexus', 'World'])
    print(" Extracting 1 value...")
    rank, value = text_proc.output()
    print(f" Text value {rank}: {value}")

    print("\nTesting Log Processor...")
    log_proc = LogProcessor()

    print(f" Trying to validate input 'Hello': {log_proc.validate('Hello')}")

    logs = [
        {"log_level": "NOTICE", "log_message": "Connection to server"},
        {"log_level": "ERROR", "log_message": "Unauthorized access!!"}
    ]
    print(f" Processing data: {logs}")
    log_proc.ingest(logs)
    print(" Extracting 2 values...")
    for i in range(2):
        rank, value = log_proc.output()
        print(f" Log entry {rank}: {value}")


if __name__ == "__main__":
    main()
