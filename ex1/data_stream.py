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

    # Defining return value if no data is available to return
    # A sentinel is a special value used as a signal, like '-1'
    EMPTY_SENTINEL: tuple[int, str] = (-1, "No data available")

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
            return self.EMPTY_SENTINEL
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


class DataStream:
    def __init__(self) -> None:
        self._procs: list[DataProcessor] = []

    def register_processor(self, proc: DataProcessor) -> None:
        if (isinstance(proc, DataProcessor)):
            self._procs.append(proc)
        else:
            raise Exception("None DataProcessor passed")

    def process_stream(self, stream: list[Any]) -> None:
        for data in stream:
            for proc in self._procs:
                if proc.validate(data):
                    proc.ingest(data)
                    break
            else:
                print("DataStream error - Can't process element in stream: "
                      f"{data}")

    def print_processors_stats(self) -> None:
        if not self._procs:
            print("No processor found, no data")
            return
        for proc in self._procs:
            class_name = proc.__class__.__name__
            print(f"{class_name[:-9]} Processor: total {proc._data_rank} "
                  f"items processed, remaining {len(proc._data)} on processor")


def main() -> None:
    print("=== Code Nexus - Data Stream ===\n")

    print("Initialize Data Stream...")
    data_stream = DataStream()

    print("== DataStream statistics ==\n")
    data_stream.print_processors_stats()

    print("\nRegistering Numeric Processor\n")
    num_proc = NumericProcessor()
    data_stream.register_processor(num_proc)

    test_batch = ['Hello world', [3.14, -1, 2.71],
                  [{'log_level': 'WARNING',
                   'log_message': 'Telnet access! Use ssh instead'},
                  {'log_level': 'INFO',
                   'log_message': 'User wil is connected'}],
                  42, ['Hi', 'five']
                  ]
    print(f"Send first batch of data on stream: {test_batch}")
    data_stream.process_stream(test_batch)

    print("== DataStream statistics ==")
    data_stream.print_processors_stats()

    print("\nRegistering other data processors")
    text_proc = TextProcessor()
    log_proc = LogProcessor()
    data_stream.register_processor(text_proc)
    data_stream.register_processor(log_proc)

    print("Send the same batch again")
    data_stream.process_stream(test_batch)

    print("== DataStream statistics ==")
    data_stream.print_processors_stats()

    print("\nConsume some elements from the data processors: "
          "Numeric 3, Text 2, Log 1")

    for _ in range(3):
        num_proc.output()
    for _ in range(2):
        text_proc.output()
        log_proc.output()

    print("== DataStream statistics ==")
    data_stream.print_processors_stats()


if __name__ == "__main__":
    main()
