# CodeGenerator Output
**Agent**: CodeGenerator
**Execution Order**: 3
**Timestamp**: 2025-07-04 08:42:40

---

## Code Implementation

### Project Structure

```
project/
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── entities.py
│   │   └── enums.py
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── repositories.py
│   │   └── file_utils.py
│   ├── application/
│   │   ├── __init__.py
│   │   ├── test_case_manager.py
│   │   ├── test_runner.py
│   │   └── report_generator.py
├── data/
│   ├── test_cases.json
│   └── test_results.json
└── tests/
    ├── test_domain.py
    ├── test_infrastructure.py
    └── test_application.py
```

### Main Implementation

```python
# src/main.py
import os
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.application.test_case_manager import TestCaseManager
from src.application.test_runner import TestRunner
from src.application.report_generator import ReportGenerator

# Define data file paths
DATA_DIR = "data"
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")
TEST_RESULTS_FILE = os.path.join(DATA_DIR, "test_results.json")

def initialize_data_directory() -> None:
    """Ensures the data directory exists."""
    os.makedirs(DATA_DIR, exist_ok=True)
    # Create empty JSON files if they don't exist
    for file_path in [TEST_CASES_FILE, TEST_RESULTS_FILE]:
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                f.write('[]')

def main_menu() -> None:
    """Displays the main menu and handles user input."""
    initialize_data_directory()

    test_case_repo = JSONFileTestCaseRepository(TEST_CASES_FILE)
    test_result_repo = JSONFileTestExecutionResultRepository(TEST_RESULTS_FILE)

    test_case_manager = TestCaseManager(test_case_repo)
    test_runner = TestRunner(test_case_repo, test_result_repo)
    report_generator = ReportGenerator(test_case_repo, test_result_repo)

    while True:
        print("\n--- Simple Test Workflow ---")
        print("1. Define New Test Case")
        print("2. List All Test Cases")
        print("3. Run Test Case")
        print("4. View Test Report")
        print("5. Exit")

        choice = input("Enter your choice: ").strip()

        if choice == '1':
            define_test_case(test_case_manager)
        elif choice == '2':
            list_test_cases(test_case_manager)
        elif choice == '3':
            run_test_case_workflow(test_case_manager, test_runner)
        elif choice == '4':
            view_test_report(report_generator)
        elif choice == '5':
            print("Exiting workflow. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

def define_test_case(manager: TestCaseManager) -> None:
    """Prompts user to define a new test case and saves it."""
    print("\n--- Define New Test Case ---")
    name = input("Enter test case name: ").strip()
    if not name:
        print("Test case name cannot be empty.")
        return

    steps_list: List[str] = []
    print("Enter execution steps (type 'done' on a new line to finish):")
    step_num = 1
    while True:
        step = input(f"Step {step_num}: ").strip()
        if step.lower() == 'done':
            break
        if step:
            steps_list.append(step)
        step_num += 1

    if not steps_list:
        print("At least one step is required.")
        return

    expected_results = input("Enter expected results: ").strip()
    if not expected_results:
        print("Expected results cannot be empty.")
        return

    try:
        test_case = manager.create_test_case(name, steps_list, expected_results)
        print(f"Test Case '{test_case.name}' (ID: {test_case.id}) defined successfully!")
    except Exception as e:
        print(f"Error defining test case: {e}")

def list_test_cases(manager: TestCaseManager) -> None:
    """Lists all defined test cases."""
    print("\n--- All Test Cases ---")
    test_cases = manager.list_test_cases()
    if not test_cases:
        print("No test cases defined yet.")
        return

    for tc in test_cases:
        print(f"ID: {tc.id}")
        print(f"  Name: {tc.name}")
        print(f"  Steps:")
        for i, step in enumerate(tc.steps):
            print(f"    {i+1}. {step}")
        print(f"  Expected Results: {tc.expected_results}")
        print("-" * 30)

def run_test_case_workflow(test_case_manager: TestCaseManager, test_runner: TestRunner) -> None:
    """Guides user through running a test case and recording its result."""
    print("\n--- Run Test Case ---")
    test_cases = test_case_manager.list_test_cases()
    if not test_cases:
        print("No test cases to run. Please define some first.")
        return

    print("Available Test Cases:")
    for i, tc in enumerate(test_cases):
        print(f"{i+1}. {tc.name} (ID: {tc.id})")

    try:
        choice_index = int(input("Enter the number of the test case to run: ")) - 1
        if not (0 <= choice_index < len(test_cases)):
            print("Invalid test case number.")
            return
        
        selected_test_case_id = test_cases[choice_index].id
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    test_case = test_case_manager.get_test_case(selected_test_case_id)
    if not test_case:
        print(f"Test case with ID {selected_test_case_id} not found.")
        return

    print(f"\n--- Executing Test Case: '{test_case.name}' (ID: {test_case.id}) ---")
    print("\nExecution Steps:")
    for i, step in enumerate(test_case.steps):
        input(f"Step {i+1}: {step} (Press Enter when done with this step)") # User interaction for steps

    print("\nExpected Results:")
    print(test_case.expected_results)
    input("Review expected results. (Press Enter to continue to result recording)")

    print("\n--- Record Test Result ---")
    print("Select Outcome:")
    outcomes = [o.name for o in TestOutcome]
    for i, outcome_name in enumerate(outcomes):
        print(f"{i+1}. {outcome_name}")

    outcome_choice = input("Enter outcome number: ").strip()
    try:
        selected_outcome = TestOutcome[outcomes[int(outcome_choice) - 1]]
    except (ValueError, IndexError):
        print("Invalid outcome choice. Defaulting to 'Blocked'.")
        selected_outcome = TestOutcome.BLOCKED

    comments = input("Add comments (optional): ").strip()
    evidence_path = input("Path to evidence (optional, e.g., screenshot.png): ").strip() or None

    try:
        result = test_runner.record_result(
            selected_test_case_id,
            selected_outcome,
            comments,
            evidence_path
        )
        print(f"Test result recorded for '{test_case.name}' (Result ID: {result.id}) with outcome: {result.outcome.name}")
    except Exception as e:
        print(f"Error recording test result: {e}")

def view_test_report(generator: ReportGenerator) -> None:
    """Generates and displays a test report."""
    print("\n--- Test Report ---")
    summary = generator.generate_summary_report()
    detailed = generator.generate_detailed_report()

    print("\n--- Summary Report ---")
    print(f"Total Test Cases: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Blocked: {summary['blocked']}")
    print(f"Skipped: {summary['skipped']}")

    print("\n--- Detailed Report (Last Result Per Test Case) ---")
    if not detailed:
        print("No test results available for detailed report.")
        return
    
    for item in detailed:
        print(f"Test Case: {item['test_case_name']} (ID: {item['test_case_id']})")
        if item['last_result']:
            result = item['last_result']
            print(f"  Last Run: {result['timestamp']}")
            print(f"  Outcome: {result['outcome']}")
            if result['comments']:
                print(f"  Comments: {result['comments']}")
            if result['evidence_path']:
                print(f"  Evidence: {result['evidence_path']}")
        else:
            print("  No runs recorded yet.")
        print("-" * 30)


if __name__ == "__main__":
    main_menu()

```

### Supporting Modules

```python
# src/domain/enums.py
from enum import Enum

class TestOutcome(Enum):
    """
    Represents the possible outcomes of a test execution.
    """
    PASS = "Pass"
    FAIL = "Fail"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"


# src/domain/entities.py
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.enums import TestOutcome

class TestCase:
    """
    Represents a single test case definition.

    Attributes:
        id (str): Unique identifier for the test case.
        name (str): Descriptive name of the test case.
        steps (List[str]): List of execution steps.
        expected_results (str): Detailed expected outcome of the test.
    """
    def __init__(self, id: str, name: str, steps: List[str], expected_results: str) -> None:
        if not id:
            raise ValueError("Test Case ID cannot be empty.")
        if not name:
            raise ValueError("Test Case name cannot be empty.")
        if not steps:
            raise ValueError("Test Case steps cannot be empty.")
        if not expected_results:
            raise ValueError("Test Case expected results cannot be empty.")

        self.id = id
        self.name = name
        self.steps = steps
        self.expected_results = expected_results

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TestCase object to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "steps": self.steps,
            "expected_results": self.expected_results
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TestCase":
        """Creates a TestCase object from a dictionary."""
        if not all(k in data for k in ["id", "name", "steps", "expected_results"]):
            raise ValueError("Missing required keys in test case data.")
        return TestCase(
            id=data["id"],
            name=data["name"],
            steps=data["steps"],
            expected_results=data["expected_results"]
        )

class TestExecutionResult:
    """
    Represents the outcome of a single test case execution.

    Attributes:
        id (str): Unique identifier for the test execution result.
        test_case_id (str): ID of the test case that was executed.
        timestamp (datetime): Timestamp of when the test was executed.
        outcome (TestOutcome): The result of the test execution (Pass, Fail, etc.).
        comments (str): Additional comments about the execution.
        evidence_path (Optional[str]): Path to any evidence (e.g., screenshot).
    """
    def __init__(self,
                 id: str,
                 test_case_id: str,
                 timestamp: datetime,
                 outcome: TestOutcome,
                 comments: str = "",
                 evidence_path: Optional[str] = None) -> None:
        if not id:
            raise ValueError("Test Execution Result ID cannot be empty.")
        if not test_case_id:
            raise ValueError("Test Case ID for result cannot be empty.")
        if not isinstance(timestamp, datetime):
            raise TypeError("Timestamp must be a datetime object.")
        if not isinstance(outcome, TestOutcome):
            raise TypeError("Outcome must be a TestOutcome enum member.")

        self.id = id
        self.test_case_id = test_case_id
        self.timestamp = timestamp
        self.outcome = outcome
        self.comments = comments
        self.evidence_path = evidence_path

    def to_dict(self) -> Dict[str, Any]:
        """Converts the TestExecutionResult object to a dictionary."""
        return {
            "id": self.id,
            "test_case_id": self.test_case_id,
            "timestamp": self.timestamp.isoformat(),  # Store as ISO format string
            "outcome": self.outcome.value,
            "comments": self.comments,
            "evidence_path": self.evidence_path
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "TestExecutionResult":
        """Creates a TestExecutionResult object from a dictionary."""
        if not all(k in data for k in ["id", "test_case_id", "timestamp", "outcome"]):
            raise ValueError("Missing required keys in test execution result data.")
        
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
            outcome = TestOutcome(data["outcome"])
        except ValueError as e:
            raise ValueError(f"Invalid data format for timestamp or outcome: {e}")

        return TestExecutionResult(
            id=data["id"],
            test_case_id=data["test_case_id"],
            timestamp=timestamp,
            outcome=outcome,
            comments=data.get("comments", ""),
            evidence_path=data.get("evidence_path")
        )


# src/infrastructure/file_utils.py
import json
import os
from typing import List, Dict, Any

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads JSON data from a specified file path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries read from the JSON file.
                              Returns an empty list if the file does not exist or is empty.
    
    Raises:
        json.JSONDecodeError: If the file contains invalid JSON.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        # Optionally, back up the corrupted file and return empty data
        # For simplicity, just re-raising for now
        raise
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        raise

def write_json_file(file_path: str, data: List[Dict[str, Any]]) -> None:
    """
    Writes a list of dictionaries as JSON data to a specified file path.

    Args:
        file_path (str): The path to the JSON file.
        data (List[Dict[str, Any]]): The list of dictionaries to write.

    Raises:
        IOError: If there's an issue writing to the file.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"Error writing to file {file_path}: {e}")
        raise


# src/infrastructure/repositories.py
import uuid
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from src.domain.entities import TestCase, TestExecutionResult
from src.infrastructure.file_utils import read_json_file, write_json_file

class AbstractTestCaseRepository(ABC):
    """Abstract base class for Test Case repositories."""

    @abstractmethod
    def save(self, test_case: TestCase) -> None:
        """Saves or updates a test case."""
        pass

    @abstractmethod
    def find_by_id(self, test_case_id: str) -> Optional[TestCase]:
        """Finds a test case by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[TestCase]:
        """Returns all test cases."""
        pass

    @abstractmethod
    def delete(self, test_case_id: str) -> bool:
        """Deletes a test case by its ID. Returns True if deleted, False otherwise."""
        pass

class JSONFileTestCaseRepository(AbstractTestCaseRepository):
    """
    Concrete implementation of TestCaseRepository using a JSON file for storage.
    """
    def __init__(self, file_path: str) -> None:
        """
        Initializes the repository with the path to the JSON file.

        Args:
            file_path (str): The path to the JSON file where test cases are stored.
        """
        self.file_path = file_path

    def _load_data(self) -> List[Dict[str, Any]]:
        """Loads raw dictionary data from the JSON file."""
        return read_json_file(self.file_path)

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Saves raw dictionary data to the JSON file."""
        write_json_file(self.file_path, data)

    def save(self, test_case: TestCase) -> None:
        """
        Saves or updates a test case in the JSON file.

        Args:
            test_case (TestCase): The TestCase object to save.
        """
        data = self._load_data()
        updated = False
        for i, tc_dict in enumerate(data):
            if tc_dict["id"] == test_case.id:
                data[i] = test_case.to_dict()
                updated = True
                break
        if not updated:
            data.append(test_case.to_dict())
        self._save_data(data)

    def find_by_id(self, test_case_id: str) -> Optional[TestCase]:
        """
        Finds a test case by its ID from the JSON file.

        Args:
            test_case_id (str): The ID of the test case to find.

        Returns:
            Optional[TestCase]: The TestCase object if found, None otherwise.
        """
        data = self._load_data()
        for tc_dict in data:
            if tc_dict["id"] == test_case_id:
                return TestCase.from_dict(tc_dict)
        return None

    def find_all(self) -> List[TestCase]:
        """
        Returns all test cases from the JSON file.

        Returns:
            List[TestCase]: A list of all TestCase objects.
        """
        data = self._load_data()
        return [TestCase.from_dict(tc_dict) for tc_dict in data]

    def delete(self, test_case_id: str) -> bool:
        """
        Deletes a test case by its ID from the JSON file.

        Args:
            test_case_id (str): The ID of the test case to delete.

        Returns:
            bool: True if the test case was deleted, False if not found.
        """
        data = self._load_data()
        initial_len = len(data)
        new_data = [tc_dict for tc_dict in data if tc_dict["id"] != test_case_id]
        if len(new_data) < initial_len:
            self._save_data(new_data)
            return True
        return False


class AbstractTestExecutionResultRepository(ABC):
    """Abstract base class for Test Execution Result repositories."""

    @abstractmethod
    def save(self, result: TestExecutionResult) -> None:
        """Saves a test execution result."""
        pass

    @abstractmethod
    def find_by_id(self, result_id: str) -> Optional[TestExecutionResult]:
        """Finds a test execution result by its ID."""
        pass

    @abstractmethod
    def find_all(self) -> List[TestExecutionResult]:
        """Returns all test execution results."""
        pass

    @abstractmethod
    def find_by_test_case_id(self, test_case_id: str) -> List[TestExecutionResult]:
        """Returns all execution results for a specific test case ID."""
        pass

class JSONFileTestExecutionResultRepository(AbstractTestExecutionResultRepository):
    """
    Concrete implementation of TestExecutionResultRepository using a JSON file for storage.
    """
    def __init__(self, file_path: str) -> None:
        """
        Initializes the repository with the path to the JSON file.

        Args:
            file_path (str): The path to the JSON file where test execution results are stored.
        """
        self.file_path = file_path

    def _load_data(self) -> List[Dict[str, Any]]:
        """Loads raw dictionary data from the JSON file."""
        return read_json_file(self.file_path)

    def _save_data(self, data: List[Dict[str, Any]]) -> None:
        """Saves raw dictionary data to the JSON file."""
        write_json_file(self.file_path, data)

    def save(self, result: TestExecutionResult) -> None:
        """
        Saves a test execution result to the JSON file.

        Args:
            result (TestExecutionResult): The TestExecutionResult object to save.
        """
        data = self._load_data()
        data.append(result.to_dict())
        self._save_data(data)

    def find_by_id(self, result_id: str) -> Optional[TestExecutionResult]:
        """
        Finds a test execution result by its ID from the JSON file.

        Args:
            result_id (str): The ID of the test execution result to find.

        Returns:
            Optional[TestExecutionResult]: The TestExecutionResult object if found, None otherwise.
        """
        data = self._load_data()
        for res_dict in data:
            if res_dict["id"] == result_id:
                return TestExecutionResult.from_dict(res_dict)
        return None

    def find_all(self) -> List[TestExecutionResult]:
        """
        Returns all test execution results from the JSON file.

        Returns:
            List[TestExecutionResult]: A list of all TestExecutionResult objects.
        """
        data = self._load_data()
        return [TestExecutionResult.from_dict(res_dict) for res_dict in data]

    def find_by_test_case_id(self, test_case_id: str) -> List[TestExecutionResult]:
        """
        Returns all execution results for a specific test case ID.

        Args:
            test_case_id (str): The ID of the test case.

        Returns:
            List[TestExecutionResult]: A list of TestExecutionResult objects for the given test case ID.
        """
        data = self._load_data()
        return [TestExecutionResult.from_dict(res_dict) for res_dict in data if res_dict["test_case_id"] == test_case_id]


# src/application/test_case_manager.py
import uuid
from typing import List, Optional, Dict, Any

from src.domain.entities import TestCase
from src.infrastructure.repositories import AbstractTestCaseRepository

class TestCaseManager:
    """
    Manages the lifecycle of test case definitions (CRUD operations).
    Interacts with the TestCaseRepository for data persistence.
    """
    def __init__(self, test_case_repository: AbstractTestCaseRepository) -> None:
        """
        Initializes the TestCaseManager with a test case repository.

        Args:
            test_case_repository (AbstractTestCaseRepository): The repository for test cases.
        """
        self.test_case_repo = test_case_repository

    def create_test_case(self, name: str, steps: List[str], expected_results: str) -> TestCase:
        """
        Creates a new test case and saves it.

        Args:
            name (str): The name of the test case.
            steps (List[str]): The execution steps.
            expected_results (str): The expected outcome.

        Returns:
            TestCase: The newly created TestCase object.
        
        Raises:
            ValueError: If input data is invalid.
        """
        if not name or not steps or not expected_results:
            raise ValueError("Name, steps, and expected results cannot be empty.")
        
        test_case_id = str(uuid.uuid4())
        test_case = TestCase(id=test_case_id, name=name, steps=steps, expected_results=expected_results)
        self.test_case_repo.save(test_case)
        return test_case

    def get_test_case(self, test_case_id: str) -> Optional[TestCase]:
        """
        Retrieves a test case by its ID.

        Args:
            test_case_id (str): The ID of the test case.

        Returns:
            Optional[TestCase]: The TestCase object if found, None otherwise.
        """
        return self.test_case_repo.find_by_id(test_case_id)

    def update_test_case(self, test_case_id: str, new_data: Dict[str, Any]) -> bool:
        """
        Updates an existing test case with new data.

        Args:
            test_case_id (str): The ID of the test case to update.
            new_data (Dict[str, Any]): A dictionary containing the fields to update.
                                        Allowed keys: 'name', 'steps', 'expected_results'.

        Returns:
            bool: True if the test case was updated, False if not found.
        """
        test_case = self.test_case_repo.find_by_id(test_case_id)
        if not test_case:
            return False
        
        if 'name' in new_data and new_data['name']:
            test_case.name = new_data['name']
        if 'steps' in new_data and new_data['steps']:
            if not isinstance(new_data['steps'], list) or not all(isinstance(s, str) for s in new_data['steps']):
                raise TypeError("Steps must be a list of strings.")
            test_case.steps = new_data['steps']
        if 'expected_results' in new_data and new_data['expected_results']:
            test_case.expected_results = new_data['expected_results']
        
        self.test_case_repo.save(test_case)
        return True

    def delete_test_case(self, test_case_id: str) -> bool:
        """
        Deletes a test case by its ID.

        Args:
            test_case_id (str): The ID of the test case to delete.

        Returns:
            bool: True if the test case was deleted, False if not found.
        """
        return self.test_case_repo.delete(test_case_id)

    def list_test_cases(self) -> List[TestCase]:
        """
        Lists all defined test cases.

        Returns:
            List[TestCase]: A list of all TestCase objects.
        """
        return self.test_case_repo.find_all()


# src/application/test_runner.py
import uuid
from datetime import datetime
from typing import Optional

from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome
from src.infrastructure.repositories import AbstractTestCaseRepository, AbstractTestExecutionResultRepository

class TestRunner:
    """
    Facilitates the execution of test cases and recording of their results.
    """
    def __init__(self,
                 test_case_repository: AbstractTestCaseRepository,
                 test_execution_result_repository: AbstractTestExecutionResultRepository) -> None:
        """
        Initializes the TestRunner with repositories for test cases and results.

        Args:
            test_case_repository (AbstractTestCaseRepository): Repository for test case definitions.
            test_execution_result_repository (AbstractTestExecutionResultRepository): Repository for test execution results.
        """
        self.test_case_repo = test_case_repository
        self.test_result_repo = test_execution_result_repository

    def record_result(self,
                      test_case_id: str,
                      outcome: TestOutcome,
                      comments: str = "",
                      evidence_path: Optional[str] = None) -> TestExecutionResult:
        """
        Records the outcome of a test case execution.

        Args:
            test_case_id (str): The ID of the test case that was executed.
            outcome (TestOutcome): The result of the execution (Pass, Fail, etc.).
            comments (str): Optional comments about the execution.
            evidence_path (Optional[str]): Optional path to evidence (e.g., screenshot).

        Returns:
            TestExecutionResult: The newly created TestExecutionResult object.

        Raises:
            ValueError: If the test_case_id is not found or outcome is invalid.
        """
        test_case = self.test_case_repo.find_by_id(test_case_id)
        if not test_case:
            raise ValueError(f"Test Case with ID '{test_case_id}' not found.")
        
        if not isinstance(outcome, TestOutcome):
            raise TypeError("Outcome must be a valid TestOutcome enum member.")

        result_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        test_result = TestExecutionResult(
            id=result_id,
            test_case_id=test_case_id,
            timestamp=timestamp,
            outcome=outcome,
            comments=comments,
            evidence_path=evidence_path
        )
        self.test_result_repo.save(test_result)
        return test_result

    # The 'run_test_case' logic with user interaction will be in main.py, 
    # and it will call record_result after user input.


# src/application/report_generator.py
from typing import Dict, Any, List, Optional
from collections import defaultdict

from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome
from src.infrastructure.repositories import AbstractTestCaseRepository, AbstractTestExecutionResultRepository

class ReportGenerator:
    """
    Generates various reports based on test case definitions and execution results.
    """
    def __init__(self,
                 test_case_repository: AbstractTestCaseRepository,
                 test_execution_result_repository: AbstractTestExecutionResultRepository) -> None:
        """
        Initializes the ReportGenerator with repositories.

        Args:
            test_case_repository (AbstractTestCaseRepository): Repository for test case definitions.
            test_execution_result_repository (AbstractTestExecutionResultRepository): Repository for test execution results.
        """
        self.test_case_repo = test_case_repository
        self.test_result_repo = test_execution_result_repository

    def generate_summary_report(self) -> Dict[str, int]:
        """
        Generates a summary report of test execution outcomes.
        For each test case, it considers only its latest execution result.

        Returns:
            Dict[str, int]: A dictionary with counts for total tests, passed, failed, blocked, skipped.
        """
        all_test_cases = self.test_case_repo.find_all()
        all_results = self.test_result_repo.find_all()

        latest_results_per_test_case: Dict[str, TestExecutionResult] = {}
        for result in all_results:
            if result.test_case_id not in latest_results_per_test_case or \
               result.timestamp > latest_results_per_test_case[result.test_case_id].timestamp:
                latest_results_per_test_case[result.test_case_id] = result

        summary: Dict[str, int] = {
            "total_tests": len(all_test_cases),
            "passed": 0,
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "not_run": 0 # Test cases defined but never executed
        }

        for tc in all_test_cases:
            if tc.id in latest_results_per_test_case:
                outcome = latest_results_per_test_case[tc.id].outcome
                if outcome == TestOutcome.PASS:
                    summary["passed"] += 1
                elif outcome == TestOutcome.FAIL:
                    summary["failed"] += 1
                elif outcome == TestOutcome.BLOCKED:
                    summary["blocked"] += 1
                elif outcome == TestOutcome.SKIPPED:
                    summary["skipped"] += 1
            else:
                summary["not_run"] += 1

        return summary

    def generate_detailed_report(self) -> List[Dict[str, Any]]:
        """
        Generates a detailed report listing each test case and its latest execution result.

        Returns:
            List[Dict[str, Any]]: A list of dictionaries, each containing test case info
                                   and its latest result (if any).
        """
        all_test_cases = self.test_case_repo.find_all()
        all_results = self.test_result_repo.find_all()

        latest_results_per_test_case: Dict[str, TestExecutionResult] = {}
        for result in all_results:
            if result.test_case_id not in latest_results_per_test_case or \
               result.timestamp > latest_results_per_test_case[result.test_case_id].timestamp:
                latest_results_per_test_case[result.test_case_id] = result
        
        detailed_report: List[Dict[str, Any]] = []

        for tc in all_test_cases:
            report_item: Dict[str, Any] = {
                "test_case_id": tc.id,
                "test_case_name": tc.name,
                "expected_results": tc.expected_results,
                "steps": tc.steps,
                "last_result": None
            }
            if tc.id in latest_results_per_test_case:
                latest_res = latest_results_per_test_case[tc.id]
                report_item["last_result"] = {
                    "id": latest_res.id,
                    "timestamp": latest_res.timestamp.isoformat(),
                    "outcome": latest_res.outcome.value,
                    "comments": latest_res.comments,
                    "evidence_path": latest_res.evidence_path
                }
            detailed_report.append(report_item)
        
        return detailed_report

```

### Unit Tests

```python
# tests/test_domain.py
import unittest
from datetime import datetime
import uuid

from src.domain.enums import TestOutcome
from src.domain.entities import TestCase, TestExecutionResult

class TestDomainEntities(unittest.TestCase):

    def test_test_case_creation(self):
        # Test valid creation
        tc = TestCase("id1", "Test Login", ["Step 1", "Step 2"], "User logged in")
        self.assertEqual(tc.id, "id1")
        self.assertEqual(tc.name, "Test Login")
        self.assertEqual(tc.steps, ["Step 1", "Step 2"])
        self.assertEqual(tc.expected_results, "User logged in")

        # Test invalid creation (missing fields)
        with self.assertRaises(ValueError):
            TestCase("", "Name", ["step"], "expected")
        with self.assertRaises(ValueError):
            TestCase("id", "", ["step"], "expected")
        with self.assertRaises(ValueError):
            TestCase("id", "Name", [], "expected")
        with self.assertRaises(ValueError):
            TestCase("id", "Name", ["step"], "")

    def test_test_case_to_from_dict(self):
        tc = TestCase("id1", "Test Login", ["Step 1", "Step 2"], "User logged in")
        tc_dict = tc.to_dict()
        
        self.assertIsInstance(tc_dict, dict)
        self.assertEqual(tc_dict["id"], "id1")
        self.assertEqual(tc_dict["name"], "Test Login")
        self.assertEqual(tc_dict["steps"], ["Step 1", "Step 2"])
        self.assertEqual(tc_dict["expected_results"], "User logged in")

        # Test from_dict
        new_tc = TestCase.from_dict(tc_dict)
        self.assertEqual(new_tc.id, tc.id)
        self.assertEqual(new_tc.name, tc.name)
        self.assertEqual(new_tc.steps, tc.steps)
        self.assertEqual(new_tc.expected_results, tc.expected_results)

        # Test from_dict with missing keys
        bad_dict = {"id": "id", "name": "name", "steps": ["s1"]} # Missing expected_results
        with self.assertRaises(ValueError):
            TestCase.from_dict(bad_dict)

    def test_test_execution_result_creation(self):
        now = datetime.now()
        # Test valid creation
        res = TestExecutionResult("res1", "tc1", now, TestOutcome.PASS, "Comments", "/path/to/evidence.png")
        self.assertEqual(res.id, "res1")
        self.assertEqual(res.test_case_id, "tc1")
        self.assertEqual(res.timestamp, now)
        self.assertEqual(res.outcome, TestOutcome.PASS)
        self.assertEqual(res.comments, "Comments")
        self.assertEqual(res.evidence_path, "/path/to/evidence.png")

        # Test creation with default comments/evidence
        res_default = TestExecutionResult("res2", "tc2", now, TestOutcome.FAIL)
        self.assertEqual(res_default.comments, "")
        self.assertIsNone(res_default.evidence_path)

        # Test invalid creation (missing fields, wrong types)
        with self.assertRaises(ValueError):
            TestExecutionResult("", "tc1", now, TestOutcome.PASS)
        with self.assertRaises(ValueError):
            TestExecutionResult("res1", "", now, TestOutcome.PASS)
        with self.assertRaises(TypeError):
            TestExecutionResult("res1", "tc1", "not_a_datetime", TestOutcome.PASS) # type: ignore
        with self.assertRaises(TypeError):
            TestExecutionResult("res1", "tc1", now, "not_an_enum") # type: ignore

    def test_test_execution_result_to_from_dict(self):
        now = datetime.now()
        res = TestExecutionResult("res1", "tc1", now, TestOutcome.PASS, "Comments", "/path/to/evidence.png")
        res_dict = res.to_dict()

        self.assertIsInstance(res_dict, dict)
        self.assertEqual(res_dict["id"], "res1")
        self.assertEqual(res_dict["test_case_id"], "tc1")
        self.assertEqual(datetime.fromisoformat(res_dict["timestamp"]), now)
        self.assertEqual(res_dict["outcome"], "Pass")
        self.assertEqual(res_dict["comments"], "Comments")
        self.assertEqual(res_dict["evidence_path"], "/path/to/evidence.png")

        # Test from_dict
        new_res = TestExecutionResult.from_dict(res_dict)
        self.assertEqual(new_res.id, res.id)
        self.assertEqual(new_res.test_case_id, res.test_case_id)
        self.assertEqual(new_res.timestamp, res.timestamp)
        self.assertEqual(new_res.outcome, res.outcome)
        self.assertEqual(new_res.comments, res.comments)
        self.assertEqual(new_res.evidence_path, res.evidence_path)

        # Test from_dict with missing optional fields
        res_dict_no_opt = {
            "id": "res2", "test_case_id": "tc2", "timestamp": now.isoformat(), "outcome": "Fail"
        }
        new_res_no_opt = TestExecutionResult.from_dict(res_dict_no_opt)
        self.assertEqual(new_res_no_opt.comments, "")
        self.assertIsNone(new_res_no_opt.evidence_path)

        # Test from_dict with invalid outcome string
        bad_dict = {"id": "id", "test_case_id": "tc", "timestamp": now.isoformat(), "outcome": "INVALID"}
        with self.assertRaises(ValueError):
            TestExecutionResult.from_dict(bad_dict)


# tests/test_infrastructure.py
import unittest
import os
import json
from unittest.mock import patch, mock_open
from datetime import datetime

from src.infrastructure.file_utils import read_json_file, write_json_file
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_temp.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_read_json_file_empty_or_non_existent(self):
        self.assertEqual(read_json_file("non_existent.json"), [])
        with open(self.test_file, 'w') as f:
            f.write('')
        self.assertEqual(read_json_file(self.test_file), [])

    def test_read_json_file_valid_data(self):
        test_data = [{"key": "value"}, {"key2": "value2"}]
        with open(self.test_file, 'w') as f:
            json.dump(test_data, f)
        self.assertEqual(read_json_file(self.test_file), test_data)

    def test_read_json_file_invalid_json(self):
        with open(self.test_file, 'w') as f:
            f.write('{invalid json')
        with self.assertRaises(json.JSONDecodeError):
            read_json_file(self.test_file)

    def test_write_json_file(self):
        test_data = [{"item": 1}, {"item": 2}]
        write_json_file(self.test_file, test_data)
        with open(self.test_file, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

class TestJSONFileTestCaseRepository(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_cases_repo.json"
        self.repo = JSONFileTestCaseRepository(self.file_path)
        # Ensure file is empty before each test
        with open(self.file_path, 'w') as f:
            f.write('[]')

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_save_new_test_case(self):
        tc1 = TestCase("tc1", "Login Test", ["Step A"], "Expected A")
        self.repo.save(tc1)
        data = read_json_file(self.file_path)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "tc1")

    def test_update_existing_test_case(self):
        tc1 = TestCase("tc1", "Login Test", ["Step A"], "Expected A")
        self.repo.save(tc1)
        
        tc1_updated = TestCase("tc1", "Login Test Updated", ["Step A", "Step B"], "New Expected")
        self.repo.save(tc1_updated)
        
        data = read_json_file(self.file_path)
        self.assertEqual(len(data), 1) # Should not add a new entry
        self.assertEqual(data[0]["name"], "Login Test Updated")
        self.assertEqual(data[0]["steps"], ["Step A", "Step B"])

    def test_find_by_id(self):
        tc1 = TestCase("tc1", "Test1", ["S1"], "E1")
        tc2 = TestCase("tc2", "Test2", ["S2"], "E2")
        self.repo.save(tc1)
        self.repo.save(tc2)

        found_tc1 = self.repo.find_by_id("tc1")
        self.assertIsNotNone(found_tc1)
        self.assertEqual(found_tc1.name, "Test1")

        not_found = self.repo.find_by_id("tc_non_existent")
        self.assertIsNone(not_found)

    def test_find_all(self):
        tc1 = TestCase("tc1", "Test1", ["S1"], "E1")
        tc2 = TestCase("tc2", "Test2", ["S2"], "E2")
        self.repo.save(tc1)
        self.repo.save(tc2)

        all_tcs = self.repo.find_all()
        self.assertEqual(len(all_tcs), 2)
        self.assertIn("Test1", [tc.name for tc in all_tcs])
        self.assertIn("Test2", [tc.name for tc in all_tcs])

    def test_delete_test_case(self):
        tc1 = TestCase("tc1", "Test1", ["S1"], "E1")
        self.repo.save(tc1)
        
        deleted = self.repo.delete("tc1")
        self.assertTrue(deleted)
        self.assertIsNone(self.repo.find_by_id("tc1"))
        self.assertEqual(len(self.repo.find_all()), 0)

        not_deleted = self.repo.delete("tc_non_existent")
        self.assertFalse(not_deleted)


class TestJSONFileTestExecutionResultRepository(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_results_repo.json"
        self.repo = JSONFileTestExecutionResultRepository(self.file_path)
        with open(self.file_path, 'w') as f:
            f.write('[]')

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)

    def test_save_test_result(self):
        res1 = TestExecutionResult("res1", "tc1", datetime.now(), TestOutcome.PASS)
        self.repo.save(res1)
        data = read_json_file(self.file_path)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["id"], "res1")

    def test_find_by_id(self):
        res1 = TestExecutionResult("res1", "tc1", datetime(2023, 1, 1), TestOutcome.PASS)
        res2 = TestExecutionResult("res2", "tc2", datetime(2023, 1, 2), TestOutcome.FAIL)
        self.repo.save(res1)
        self.repo.save(res2)

        found_res1 = self.repo.find_by_id("res1")
        self.assertIsNotNone(found_res1)
        self.assertEqual(found_res1.test_case_id, "tc1")

        not_found = self.repo.find_by_id("res_non_existent")
        self.assertIsNone(not_found)

    def test_find_all(self):
        res1 = TestExecutionResult("res1", "tc1", datetime(2023, 1, 1), TestOutcome.PASS)
        res2 = TestExecutionResult("res2", "tc2", datetime(2023, 1, 2), TestOutcome.FAIL)
        self.repo.save(res1)
        self.repo.save(res2)

        all_res = self.repo.find_all()
        self.assertEqual(len(all_res), 2)
        self.assertIn("tc1", [r.test_case_id for r in all_res])
        self.assertIn("tc2", [r.test_case_id for r in all_res])

    def test_find_by_test_case_id(self):
        res1_tc1 = TestExecutionResult("res1", "tc1", datetime(2023, 1, 1), TestOutcome.PASS)
        res2_tc1 = TestExecutionResult("res2", "tc1", datetime(2023, 1, 2), TestOutcome.FAIL)
        res3_tc2 = TestExecutionResult("res3", "tc2", datetime(2023, 1, 3), TestOutcome.SKIPPED)
        self.repo.save(res1_tc1)
        self.repo.save(res2_tc1)
        self.repo.save(res3_tc2)

        results_for_tc1 = self.repo.find_by_test_case_id("tc1")
        self.assertEqual(len(results_for_tc1), 2)
        self.assertEqual(results_for_tc1[0].id, "res1")
        self.assertEqual(results_for_tc1[1].id, "res2")

        results_for_tc_non_existent = self.repo.find_by_test_case_id("tc_non_existent")
        self.assertEqual(len(results_for_tc_non_existent), 0)


# tests/test_application.py
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid

from src.application.test_case_manager import TestCaseManager
from src.application.test_runner import TestRunner
from src.application.report_generator import ReportGenerator
from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome
from src.infrastructure.repositories import AbstractTestCaseRepository, AbstractTestExecutionResultRepository

class TestTestCaseManager(unittest.TestCase):
    def setUp(self):
        self.mock_repo = Mock(spec=AbstractTestCaseRepository)
        self.manager = TestCaseManager(self.mock_repo)

    def test_create_test_case_success(self):
        with patch('uuid.uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-000000000001')):
            test_case = self.manager.create_test_case("New Test", ["S1"], "E1")
            self.assertEqual(test_case.name, "New Test")
            self.assertEqual(test_case.id, '00000000-0000-0000-0000-000000000001')
            self.mock_repo.save.assert_called_once()
            # Assert that save was called with a TestCase object
            self.assertIsInstance(self.mock_repo.save.call_args[0][0], TestCase)

    def test_create_test_case_invalid_input(self):
        with self.assertRaises(ValueError):
            self.manager.create_test_case("", ["S1"], "E1")
        with self.assertRaises(ValueError):
            self.manager.create_test_case("Test", [], "E1")
        with self.assertRaises(ValueError):
            self.manager.create_test_case("Test", ["S1"], "")
        self.mock_repo.save.assert_not_called()

    def test_get_test_case(self):
        mock_test_case = TestCase("id1", "Mock Test", ["S1"], "E1")
        self.mock_repo.find_by_id.return_value = mock_test_case
        
        found_test_case = self.manager.get_test_case("id1")
        self.assertEqual(found_test_case, mock_test_case)
        self.mock_repo.find_by_id.assert_called_once_with("id1")

        self.mock_repo.find_by_id.return_value = None
        self.assertIsNone(self.manager.get_test_case("non_existent_id"))

    def test_update_test_case(self):
        mock_test_case = TestCase("id1", "Original Name", ["S1"], "Original Results")
        self.mock_repo.find_by_id.return_value = mock_test_case

        updated = self.manager.update_test_case("id1", {"name": "Updated Name", "steps": ["S1", "S2"]})
        self.assertTrue(updated)
        self.assertEqual(mock_test_case.name, "Updated Name")
        self.assertEqual(mock_test_case.steps, ["S1", "S2"])
        self.mock_repo.save.assert_called_once_with(mock_test_case)

        updated_non_existent = self.manager.update_test_case("non_existent", {"name": "X"})
        self.assertFalse(updated_non_existent)
    
    def test_update_test_case_invalid_steps_type(self):
        mock_test_case = TestCase("id1", "Original Name", ["S1"], "Original Results")
        self.mock_repo.find_by_id.return_value = mock_test_case

        with self.assertRaises(TypeError):
            self.manager.update_test_case("id1", {"steps": "not a list"})
        with self.assertRaises(TypeError):
            self.manager.update_test_case("id1", {"steps": [1, 2]})

    def test_delete_test_case(self):
        self.mock_repo.delete.return_value = True
        deleted = self.manager.delete_test_case("id1")
        self.assertTrue(deleted)
        self.mock_repo.delete.assert_called_once_with("id1")

        self.mock_repo.delete.return_value = False
        not_deleted = self.manager.delete_test_case("non_existent_id")
        self.assertFalse(not_deleted)

    def test_list_test_cases(self):
        mock_tcs = [TestCase("id1", "T1", ["S1"], "E1"), TestCase("id2", "T2", ["S2"], "E2")]
        self.mock_repo.find_all.return_value = mock_tcs
        
        test_cases = self.manager.list_test_cases()
        self.assertEqual(test_cases, mock_tcs)
        self.mock_repo.find_all.assert_called_once()

class TestTestRunner(unittest.TestCase):
    def setUp(self):
        self.mock_tc_repo = Mock(spec=AbstractTestCaseRepository)
        self.mock_res_repo = Mock(spec=AbstractTestExecutionResultRepository)
        self.runner = TestRunner(self.mock_tc_repo, self.mock_res_repo)

    def test_record_result_success(self):
        mock_test_case = TestCase("tc1", "Test Case 1", ["S1"], "E1")
        self.mock_tc_repo.find_by_id.return_value = mock_test_case

        with patch('uuid.uuid4', return_value=uuid.UUID('00000000-0000-0000-0000-000000000002')):
            with patch('src.application.test_runner.datetime') as mock_dt:
                mock_dt.now.return_value = datetime(2023, 1, 1, 10, 0, 0)
                
                result = self.runner.record_result(
                    "tc1", TestOutcome.PASS, "Good run", "/path/to/img.png"
                )
                
                self.assertEqual(result.id, '00000000-0000-0000-0000-000000000002')
                self.assertEqual(result.test_case_id, "tc1")
                self.assertEqual(result.outcome, TestOutcome.PASS)
                self.assertEqual(result.comments, "Good run")
                self.assertEqual(result.evidence_path, "/path/to/img.png")
                self.mock_res_repo.save.assert_called_once()
                self.assertIsInstance(self.mock_res_repo.save.call_args[0][0], TestExecutionResult)

    def test_record_result_test_case_not_found(self):
        self.mock_tc_repo.find_by_id.return_value = None
        with self.assertRaisesRegex(ValueError, "Test Case with ID 'non_existent' not found."):
            self.runner.record_result("non_existent", TestOutcome.FAIL)
        self.mock_res_repo.save.assert_not_called()

    def test_record_result_invalid_outcome_type(self):
        mock_test_case = TestCase("tc1", "Test Case 1", ["S1"], "E1")
        self.mock_tc_repo.find_by_id.return_value = mock_test_case
        
        with self.assertRaises(TypeError):
            self.runner.record_result("tc1", "InvalidOutcome") # type: ignore
        self.mock_res_repo.save.assert_not_called()

class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.mock_tc_repo = Mock(spec=AbstractTestCaseRepository)
        self.mock_res_repo = Mock(spec=AbstractTestExecutionResultRepository)
        self.generator = ReportGenerator(self.mock_tc_repo, self.mock_res_repo)

        # Mock test cases
        self.tc1 = TestCase("tc1", "Login Test", ["s1"], "e1")
        self.tc2 = TestCase("tc2", "Logout Test", ["s2"], "e2")
        self.tc3 = TestCase("tc3", "Profile Test", ["s3"], "e3") # No results for this one

        self.mock_tc_repo.find_all.return_value = [self.tc1, self.tc2, self.tc3]

    def test_generate_summary_report_no_results(self):
        self.mock_res_repo.find_all.return_value = []
        summary = self.generator.generate_summary_report()
        self.assertEqual(summary, {
            "total_tests": 3,
            "passed": 0,
            "failed": 0,
            "blocked": 0,
            "skipped": 0,
            "not_run": 3
        })

    def test_generate_summary_report_with_results(self):
        # Result 1 for tc1 (old Pass)
        res1_tc1_old = TestExecutionResult("res1_tc1", "tc1", datetime(2023, 1, 1), TestOutcome.PASS)
        # Result 2 for tc1 (new Fail)
        res2_tc1_new = TestExecutionResult("res2_tc1", "tc1", datetime(2023, 1, 2), TestOutcome.FAIL)
        # Result 1 for tc2 (Blocked)
        res1_tc2 = TestExecutionResult("res1_tc2", "tc2", datetime(2023, 1, 1), TestOutcome.BLOCKED)
        # Result 2 for tc2 (Skipped - latest)
        res2_tc2 = TestExecutionResult("res2_tc2", "tc2", datetime(2023, 1, 3), TestOutcome.SKIPPED)

        self.mock_res_repo.find_all.return_value = [
            res1_tc1_old, res2_tc1_new, res1_tc2, res2_tc2
        ]

        summary = self.generator.generate_summary_report()
        self.assertEqual(summary, {
            "total_tests": 3,
            "passed": 0,
            "failed": 1,  # tc1's latest is Fail
            "blocked": 0,
            "skipped": 1, # tc2's latest is Skipped
            "not_run": 1  # tc3 has no results
        })

    def test_generate_detailed_report_no_results(self):
        self.mock_res_repo.find_all.return_value = []
        detailed = self.generator.generate_detailed_report()
        self.assertEqual(len(detailed), 3)
        for item in detailed:
            self.assertIsNone(item["last_result"])
            self.assertIn(item["test_case_id"], ["tc1", "tc2", "tc3"])

    def test_generate_detailed_report_with_results(self):
        res1_tc1_old = TestExecutionResult("res1_tc1", "tc1", datetime(2023, 1, 1), TestOutcome.PASS)
        res2_tc1_new = TestExecutionResult("res2_tc1", "tc1", datetime(2023, 1, 2), TestOutcome.FAIL, comments="Latest fail")
        res1_tc2 = TestExecutionResult("res1_tc2", "tc2", datetime(2023, 1, 1), TestOutcome.BLOCKED)

        self.mock_res_repo.find_all.return_value = [
            res1_tc1_old, res2_tc1_new, res1_tc2
        ]

        detailed = self.generator.generate_detailed_report()
        self.assertEqual(len(detailed), 3)

        # Check tc1's latest result
        tc1_report = next(item for item in detailed if item["test_case_id"] == "tc1")
        self.assertIsNotNone(tc1_report["last_result"])
        self.assertEqual(tc1_report["last_result"]["outcome"], "Fail")
        self.assertEqual(tc1_report["last_result"]["comments"], "Latest fail")
        self.assertEqual(tc1_report["last_result"]["id"], "res2_tc1")

        # Check tc2's latest result
        tc2_report = next(item for item in detailed if item["test_case_id"] == "tc2")
        self.assertIsNotNone(tc2_report["last_result"])
        self.assertEqual(tc2_report["last_result"]["outcome"], "Blocked")
        self.assertEqual(tc2_report["last_result"]["id"], "res1_tc2")

        # Check tc3 (no result)
        tc3_report = next(item for item in detailed if item["test_case_id"] == "tc3")
        self.assertIsNone(tc3_report["last_result"])

```

### Installation and Usage Instructions

```bash
# 1. Clone the repository (if applicable) or create the project structure manually:
#    (Assuming you have a 'project' directory where you want to place the code)
#    cd project

# 2. Create the source and data directories:
mkdir -p src/domain src/infrastructure src/application data
mkdir -p tests

# 3. Create the __init__.py files (important for Python modules):
touch src/__init__.py
touch src/domain/__init__.py
touch src/infrastructure/__init__.py
touch src/application/__init__.py

# 4. Populate the files with the Python code provided above.
#    - Copy content for src/domain/enums.py into project/src/domain/enums.py
#    - Copy content for src/domain/entities.py into project/src/domain/entities.py
#    - Copy content for src/infrastructure/file_utils.py into project/src/infrastructure/file_utils.py
#    - Copy content for src/infrastructure/repositories.py into project/src/infrastructure/repositories.py
#    - Copy content for src/application/test_case_manager.py into project/src/application/test_case_manager.py
#    - Copy content for src/application/test_runner.py into project/src/application/test_runner.py
#    - Copy content for src/application/report_generator.py into project/src/application/report_generator.py
#    - Copy content for src/main.py into project/src/main.py

# 5. For tests, create files in the tests/ directory:
#    - Copy content for tests/test_domain.py into project/tests/test_domain.py
#    - Copy content for tests/test_infrastructure.py into project/tests/test_infrastructure.py
#    - Copy content for tests/test_application.py into project/tests/test_application.py

# 6. Ensure you have Python 3.6+ installed.

# 7. Run the application:
#    Navigate to the 'project' directory (the root of the project).
cd project
python -m src.main

# This will start the command-line interface.

# 8. To run unit tests:
#    Navigate to the 'project' directory.
python -m unittest discover tests
```

---
*Saved by after_agent_callback on 2025-07-04 08:42:40*
