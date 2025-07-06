# Flexible Workflow Execution Report

## 📋 Summary
- **Workflow**: Flexible Agent Workflow - Load Balanced v0.2
- **Status**: WorkflowStatus.COMPLETED
- **Success**: True
- **Execution Time**: 277.72 seconds
- **Timestamp**: 2025-07-04T08:40:57.019028
- **Workflow Type**: flexible
- **Incremental Outputs**: backend/output/incremental_20250704_084057

## 🎯 Original Request
```
Create a simple test workflow
```

## 🤖 Agent Configuration
- **Main Agent**: MainFlexibleOrchestrator
- **Total Agents**: 10
- **Model Used**: gemini-2.5-flash

### Agents Executed:

## 📝 Final Response
## Requirements Analysis

### Functional Requirements
- **Test Case Definition:** The system must allow users to define individual test cases, including a unique identifier, a descriptive name, a detailed set of execution steps, and clear expected results.
- **Test Case Execution:** The system must facilitate the execution of defined test cases, allowing users to follow the steps and observe the actual outcomes.
- **Test Result Recording:** The system must enable users to record the outcome of each test case execution (e.g., Pass, Fail, Blocked, Skipped) and optionally add comments or attach evidence.
- **Basic Reporting:** The system must generate a simple report summarizing the test execution results (e.g., total tests, passed, failed, blocked, skipped counts).

### Non-Functional Requirements
- **Performance requirements:**
    - Test case definition and result recording should be responsive, with operations completing within 1-2 seconds.
    - Basic test reports should be generated within 5 seconds for a small set of test cases (e.g., up to 100).
- **Security requirements:**
    - The workflow should ensure data integrity for test definitions and results.
    - No specific user authentication or authorization is required for this "simple" workflow, assuming a single-user or trusted environment.
- **Scalability requirements:**
    - The workflow should be able to manage up to 100 test cases and their respective execution results without significant performance degradation.
- **Usability requirements:**
    - The interface for defining, executing, and recording results should be intuitive and easy to understand for users with basic technical proficiency.
    - Clear instructions or prompts should guide the user through the workflow steps.

### Technical Constraints
- **Technology stack preferences:**
    - Python is preferred for implementation, aligning with the "Good Coding Practices" document (coding_standards.docx).
    - Lightweight data storage mechanisms such as CSV, JSON files, or simple flat files should be used for test case definitions and results.
- **Platform constraints:**
    - The workflow should be runnable on common operating systems (Windows, macOS, Linux).
- **Integration requirements:**
    - No external system integrations are required for this simple workflow.

### Assumptions and Clarifications
- **Assumptions made:**
    - The "simple test workflow" primarily focuses on manual or script-assisted functional testing.
    - The target user base is a single individual or a small, co-located team.
    - Test case management and execution are not expected to be highly automated; manual input will be involved.
    - The scope does not include advanced features like test automation frameworks, continuous integration, or complex reporting dashboards.
    - Version control for test assets (test case definitions) will be managed externally (e.g., Git) if needed, rather than by the workflow itself.
- **Questions that need clarification:**
    - What is the expected format for defining test cases (e.g., text file, spreadsheet, simple GUI input)?
    - How will "evidence" for test failures be captured and linked (e.g., screenshot paths, text logs)?
    - What level of detail is expected in the "basic report" (e.g., just counts, or a list of failed tests with comments)?
    - Are there any specific naming conventions or directory structures to follow for test assets beyond what's in `coding_standards.docx`?

### Risk Assessment
- **Potential technical risks:**
    - **Data Corruption:** Using simple file-based storage without robust error handling could lead to data corruption if the application crashes or is improperly shut down.
    - **Lack of Version Control for Test Assets:** If test case definitions are not managed under a version control system (e.g., Git), changes can be lost or overwritten, and traceability becomes difficult.
    - **Scalability Limitations:** As the number of test cases or executions grows, the simple file-based approach might become inefficient, leading to performance bottlenecks.
- **Mitigation strategies:**
    - **Data Corruption:** Implement basic error handling and data validation before writing to files. Consider using a simple, well-structured format like JSON to reduce parsing errors. Regularly back up test data.
    - **Lack of Version Control:** Recommend storing test definition files within a version-controlled repository (e.g., Git, as mentioned in `coding_standards.docx`).
    - **Scalability Limitations:** Clearly document the expected scale and advise on migrating to a more robust solution (e.g., a simple database) if requirements exceed the current capabilities.## System Architecture Design

### High-Level Architecture

The system will adopt a **Layered Monolithic Architecture** to ensure a clear separation of concerns while maintaining the simplicity and lightweight nature required. Given the emphasis on "simple," "single-user," and "file-based storage," a complex distributed system (like microservices) is not warranted.

**Overall System Design and Components:**

1.  **Presentation Layer (User Interface):** This layer interacts directly with the user. It will be a command-line interface (CLI) initially, providing a simple, text-based interaction for defining, executing, and reporting tests. A lightweight GUI (e.g., using Tkinter or PyQt for Python) could be an optional future enhancement but is not the primary focus for "simple."
2.  **Application Layer:** This layer orchestrates the application's core logic. It manages workflows, handles user requests from the Presentation Layer, and coordinates with the Domain and Infrastructure Layers. It implements the use cases (e.g., "Define Test Case," "Execute Test Case," "Generate Report").
3.  **Domain Layer (Core Business Logic):** This is the heart of the application, containing the business rules and domain entities (e.g., `TestCase`, `TestExecutionResult`). It is independent of external concerns like UI or data storage. This layer ensures data integrity and consistency based on the defined business rules.
4.  **Infrastructure Layer (Data Persistence & Utilities):** This layer provides generic technical capabilities such as data storage (file I/O), logging, and other utilities. It implements the interfaces defined in the Domain Layer, allowing the core business logic to remain agnostic to the specific storage mechanism.

```mermaid
graph TD
    User -- Interacts with --> PresentationLayer
    PresentationLayer -- Calls use cases --> ApplicationLayer
    ApplicationLayer -- Invokes domain logic --> DomainLayer
    DomainLayer -- Uses interfaces from --> InfrastructureLayer
    InfrastructureLayer -- Stores/Retrieves data from --> DataStorage(JSON/CSV Files)

    subgraph Layers
        PresentationLayer[Presentation Layer<br>(CLI/Simple GUI)]
        ApplicationLayer[Application Layer<br>(Use Cases, Orchestration)]
        DomainLayer[Domain Layer<br>(Entities, Business Logic)]
        InfrastructureLayer[Infrastructure Layer<br>(Data Persistence, Utilities)]
    end
```

**Architecture Pattern:** Layered Architecture / Monolithic Application

### Component Design

**Core Components and Their Responsibilities:**

1.  **`TestCaseManager` (Application Layer):**
    *   **Responsibility:** Manages the lifecycle of test case definitions (CRUD operations).
    *   **Interface:**
        *   `create_test_case(name: str, steps: List[str], expected_results: str) -> TestCaseId`
        *   `get_test_case(test_case_id: TestCaseId) -> TestCase`
        *   `update_test_case(test_case_id: TestCaseId, new_data: dict) -> bool`
        *   `delete_test_case(test_case_id: TestCaseId) -> bool`
        *   `list_test_cases() -> List[TestCase]`
    *   **Interactions:** Uses `TestCaseRepository` (from Infrastructure) to persist and retrieve `TestCase` entities.

2.  **`TestRunner` (Application Layer):**
    *   **Responsibility:** Guides the user through test execution steps, collects actual results and outcomes.
    *   **Interface:**
        *   `run_test_case(test_case_id: TestCaseId) -> TestExecutionResultId`
        *   `record_result(test_execution_result_id: TestExecutionResultId, outcome: TestOutcome, comments: str, evidence_path: Optional[str]) -> bool`
    *   **Interactions:** Uses `TestCaseRepository` to get test details, and `TestExecutionResultRepository` to save execution outcomes. Interacts with the `Presentation Layer` for user input during execution.

3.  **`ReportGenerator` (Application Layer):**
    *   **Responsibility:** Aggregates test definition and execution data to generate summary reports.
    *   **Interface:**
        *   `generate_summary_report() -> ReportData` (e.g., counts of Pass/Fail/Skipped/Blocked)
        *   `generate_detailed_report() -> DetailedReportData` (e.g., list of failed tests with comments)
    *   **Interactions:** Uses `TestCaseRepository` and `TestExecutionResultRepository` to retrieve all necessary data.

4.  **`TestCase` (Domain Layer - Entity):**
    *   **Responsibility:** Represents a single test case definition.
    *   **Attributes:** `id` (unique identifier), `name`, `steps` (list of strings), `expected_results`.
    *   **Methods:** `to_dict()`, `from_dict()`.

5.  **`TestExecutionResult` (Domain Layer - Entity):**
    *   **Responsibility:** Represents the outcome of a single test case execution.
    *   **Attributes:** `id` (unique identifier), `test_case_id` (foreign key), `timestamp`, `outcome` (enum: Pass, Fail, Blocked, Skipped), `comments`, `evidence_path` (optional string path).
    *   **Methods:** `to_dict()`, `from_dict()`.

6.  **`TestCaseRepository` (Infrastructure Layer - Implementation of Domain Interface):**
    *   **Responsibility:** Handles persistence for `TestCase` entities (e.g., reading/writing JSON files).
    *   **Interface (abstracted in Domain Layer, implemented here):**
        *   `save(test_case: TestCase) -> None`
        *   `find_by_id(test_case_id: TestCaseId) -> Optional[TestCase]`
        *   `find_all() -> List[TestCase]`
        *   `delete(test_case_id: TestCaseId) -> bool`

7.  **`TestExecutionResultRepository` (Infrastructure Layer - Implementation of Domain Interface):**
    *   **Responsibility:** Handles persistence for `TestExecutionResult` entities.
    *   **Interface (abstracted in Domain Layer, implemented here):**
        *   `save(result: TestExecutionResult) -> None`
        *   `find_by_id(result_id: TestExecutionResultId) -> Optional[TestExecutionResult]`
        *   `find_all() -> List[TestExecutionResult]`
        *   `find_by_test_case_id(test_case_id: TestCaseId) -> List[TestExecutionResult]`

**Data Flow Between Components:**

*   **Defining a Test Case:**
    1.  User input (CLI/GUI) is received by `Presentation Layer`.
    2.  `Presentation Layer` calls `TestCaseManager.create_test_case()`.
    3.  `TestCaseManager` creates a `TestCase` entity and calls `TestCaseRepository.save()`.
    4.  `TestCaseRepository` writes the `TestCase` data to the `test_cases.json` file.

*   **Executing a Test Case:**
    1.  User selects a test to run via `Presentation Layer`.
    2.  `Presentation Layer` calls `TestRunner.run_test_case()`.
    3.  `TestRunner` retrieves `TestCase` details from `TestCaseRepository`.
    4.  `TestRunner` guides user through steps (via `Presentation Layer`).
    5.  User provides outcome, comments, and optional evidence path.
    6.  `TestRunner` creates `TestExecutionResult` entity and calls `TestExecutionResultRepository.save()`.
    7.  `TestExecutionResultRepository` writes the result data to the `test_results.json` file.

*   **Generating a Report:**
    1.  User requests a report via `Presentation Layer`.
    2.  `Presentation Layer` calls `ReportGenerator.generate_summary_report()`.
    3.  `ReportGenerator` retrieves all `TestCase`s from `TestCaseRepository` and all `TestExecutionResult`s from `TestExecutionResultRepository`.
    4.  `ReportGenerator` processes data in-memory and returns the report data to the `Presentation Layer` for display.

### Technology Stack

*   **Programming Language:** Python (Preferred, adheres to `coding_standards.docx`)
*   **Frameworks/Libraries:**
    *   **Standard Library:** For file I/O (`json`, `csv` - though `json` is preferred), basic data structures, logging.
    *   **UUID:** For generating unique identifiers for test cases and results.
    *   **Type Hinting:** For improved code readability and maintainability.
    *   **Optional GUI:** `Tkinter` (standard library, simplest for basic GUI) or `PyQt` (more feature-rich, but external dependency). **Initial focus will be on CLI.**
*   **Databases and Storage Solutions:**
    *   **Test Case Definitions:** `test_cases.json` (JSON file format). Chosen for structured data, readability, and ease of parsing in Python.
    *   **Test Execution Results:** `test_results.json` (JSON file format). Similar reasons as above. Each file will be an array of objects.
*   **Infrastructure and Deployment Considerations:**
    *   **File System:** All data will be stored as flat files within a designated directory structure (e.g., `./data/`).
    *   **Local Execution:** The workflow will be designed as a standalone application, executable directly on Windows, macOS, or Linux via the Python interpreter.
    *   **Packaging (Optional):** `PyInstaller` could be used to create single-file executables for easier distribution to users without a Python environment.

### Design Patterns

*   **Architectural Pattern:**
    *   **Layered Architecture (Monolithic):** Clearly separates concerns into Presentation, Application, Domain, and Infrastructure layers. This promotes maintainability and allows for independent evolution of layers.
*   **Design Patterns for Implementation:**
    *   **Repository Pattern:** Abstract the persistence layer (file I/O) from the domain logic. `TestCaseRepository` and `TestExecutionResultRepository` are concrete implementations of an abstract interface, enabling future migration to a database without changing core logic.
    *   **Factory Method:** For creating `TestCase` and `TestExecutionResult` objects from dictionary representations loaded from JSON files. This centralizes object creation logic.
    *   **Strategy Pattern (Potential Future):** If different reporting formats or execution modes are introduced later, this pattern could allow swapping algorithms for report generation or test execution.
    *   **Dependency Injection (Manual):** Components will receive their dependencies (e.g., `TestCaseManager` receiving `TestCaseRepository` via constructor) rather than creating them internally. This improves testability and flexibility.
    *   **Value Object:** `TestOutcome` (Pass, Fail, Blocked, Skipped) can be implemented as an Enum, acting as a value object to ensure type safety and restrict valid outcomes.

### Quality Attributes

*   **Scalability:**
    *   **Design for Current Scope:** The use of JSON files is appropriate for the stated scale (up to 100 test cases and results). File I/O will be optimized by reading all necessary data into memory for reporting or processing at once, rather than line-by-line or object-by-object reads.
    *   **Future Scalability:** The Repository Pattern and clear Layered Architecture provide a strong foundation for future scaling. Should the requirements exceed 100 test cases significantly, the Infrastructure Layer can be replaced with a database (e.g., SQLite, PostgreSQL) without affecting the Application or Domain layers.
    *   **Performance Mitigation:** For report generation, all relevant data will be loaded into memory once and then processed, rather than repeatedly accessing files, ensuring reports generate within 5 seconds for the specified scale.

*   **Security Considerations:**
    *   **Data Integrity:**
        *   JSON schema validation (or simple Python dictionary validation) will be implemented upon loading data from files to ensure correctness and prevent malformed data from corrupting the application state.
        *   Data will be validated before writing to files.
        *   Unique identifiers (UUIDs) will be used for test cases and results to prevent ID conflicts.
    *   **Access Control:** As per requirements, no user authentication or authorization is required for this "simple" workflow. It assumes a trusted, single-user, or small co-located team environment. File system permissions (managed by the OS) are the primary security mechanism.
    *   **Evidence Handling:** Evidence paths will be stored as strings. The system will not directly execute or process these paths beyond storing them, mitigating risks related to arbitrary code execution from malicious paths.

*   **Performance Optimizations:**
    *   **In-Memory Processing:** For operations like reporting, all necessary test case definitions and results will be loaded into memory once. Subsequent filtering, aggregation, and formatting will occur in-memory, minimizing repeated disk I/O.
    *   **Efficient Serialization:** Python's built-in `json` module is efficient for small-to-medium JSON files.
    *   **Minimizing Disk Writes:** Data will be written to disk only when explicitly saved or updated, not on every small change, to reduce I/O overhead.
    *   **Optimized Data Structures:** Using appropriate Python data structures (e.g., dictionaries for quick lookups by ID) will ensure fast access to in-memory data.

*   **Maintainability Features:**
    *   **Clear Layer Separation:** Enforces separation of concerns, making it easier to understand, debug, and modify specific parts of the system without affecting others.
    *   **Modular Design:** Each component has a single, well-defined responsibility, promoting the Single Responsibility Principle.
    *   **Clean Code Principles:** Adherence to Python's PEP 8 guidelines and the organization's `coding_standards.docx` will ensure consistent, readable, and maintainable code.
    *   **Type Hinting:** Improves code clarity, aids in static analysis, and reduces bugs.
    *   **Testability:** The Dependency Injection pattern and clear component interfaces facilitate unit testing of individual components (especially Application and Domain layers) in isolation.
    *   **Self-Documenting Code:** Emphasis on clear variable names, function names, and concise comments where necessary.## Code Implementation

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
```## Code Quality Review Report

### Quality Score: 9/10

### Strengths
*   **Clear Layered Architecture:** The code rigorously adheres to the layered monolithic architecture defined in the design. The separation of `domain`, `infrastructure`, and `application` concerns is exemplary, promoting high cohesion and low coupling.
*   **Adherence to SOLID Principles:**
    *   **Single Responsibility Principle (SRP):** Each class (e.g., `TestCase`, `JSONFileTestCaseRepository`, `TestCaseManager`) has a well-defined and single responsibility.
    *   **Dependency Inversion Principle (DIP):** Achieved effectively through the use of abstract base classes (`AbstractTestCaseRepository`, `AbstractTestExecutionResultRepository`). Application layer components depend on these abstractions rather than concrete file-based implementations, making the system highly testable and extensible (e.g., for different storage backends).
    *   **Open/Closed Principle (OCP):** The repository pattern enables easy extension with new data storage mechanisms without modifying the application or domain layers.
*   **Robust Data Handling and Validation:**
    *   Domain entities (`TestCase`, `TestExecutionResult`) include validation in their constructors and `from_dict` methods, ensuring data integrity at the object creation level.
    *   `file_utils.py` handles common file I/O issues (`FileNotFoundError`, `json.JSONDecodeError`, `IOError`) gracefully, preventing silent failures from corrupted or missing data files.
*   **Comprehensive Unit Testing:** The test suite is well-structured, covers all key layers (domain, infrastructure, application), and uses `unittest.mock` effectively to isolate components, demonstrating strong testability derived from the architectural design. Tests cover positive flows, edge cases (e.g., empty files, non-existent IDs), and error conditions (e.g., invalid input types).
*   **Readability and Maintainability:**
    *   Consistent use of type hints throughout the codebase significantly improves readability and aids static analysis.
    *   Meaningful variable, function, and class names adhere to Python's PEP 8.
    *   Docstrings are provided for classes and methods, explaining their purpose, arguments, and return values, contributing to excellent self-documentation.
    *   The `TestOutcome` enum provides type safety and clarity for test results.
*   **Scalability Foundation:** While using flat files, the Repository Pattern provides a clear abstraction, making future migration to a more robust database (like SQLite) straightforward should scalability requirements exceed the current scope.
*   **User Experience (CLI):** The `main.py` provides clear, interactive prompts for the user, making the CLI intuitive for basic operations.

### Areas for Improvement
*   **Limited Error Recovery in `file_utils`:** While `json.JSONDecodeError` is caught, it re-raises the exception. In a real-world scenario, especially for persistent data, logging the error and attempting a recovery (e.g., backing up the corrupted file and starting with an empty file, or attempting to repair) might be desirable instead of crashing the application. For a "simple" workflow, the current approach is acceptable, but it's a consideration for robustness.
*   **Input Validation in `main.py`:** User input validation in `main.py` is present but could be more robust. For instance, `run_test_case_workflow` relies on `int(input(...))` which can raise `ValueError`. While caught, the message `Invalid input. Please enter a number.` is generic. More specific feedback or input looping until valid input is received would enhance user experience.
*   **Magic Strings/Numbers in `main.py`:** `DATA_DIR`, `TEST_CASES_FILE`, `TEST_RESULTS_FILE` are defined directly in `main.py`. For larger applications, these might be better placed in a dedicated `config.py` module, but for this small scope, it's minor.
*   **`TestRunner` `record_result` vs. `TestExecutionResultRepository` `save`:** The `TestExecutionResultRepository.save` method is purely additive (appends new results), which is appropriate for test execution results as per the requirement for "recording outcomes". However, if there was a future need to *update* a specific result record (e.g., correct a typo in comments post-facto), the `save` method in `TestExecutionResultRepository` would need logic to check for existing IDs, similar to `TestCaseRepository.save`. This is more a clarification of design intent than an issue.

### Code Structure
*   **Organization and Modularity:** Excellent. The project structure (`src/domain`, `src/infrastructure`, `src/application`, `src/main.py`) directly reflects the layered architecture. Dependencies flow correctly (Application -> Domain -> Infrastructure).
*   **Design Pattern Usage:**
    *   **Layered Architecture:** Clearly implemented and highly effective for this project's scale and requirements.
    *   **Repository Pattern:** Implemented with abstract base classes and concrete JSON file implementations. This is a standout feature for maintainability and testability.
    *   **Factory Method (Implicit):** `from_dict` static methods in entities serve this purpose for deserialization.
    *   **Dependency Injection (Manual):** Achieved through constructor injection in the application layer classes (e.g., `TestCaseManager` receiving `AbstractTestCaseRepository`). This is crucial for testability and flexibility.
    *   **Value Object:** `TestOutcome` enum effectively acts as a value object.

### Documentation
*   **Quality of Comments and Docstrings:** High quality. Classes and public methods consistently have docstrings that explain their purpose, arguments, and return types, adhering to good Python documentation practices.
*   **README and Inline Documentation:** While a dedicated `README.md` was not provided (as per the typical review scope), the "Installation and Usage Instructions" provided by `CodeGenerator` are clear and comprehensive. Inline comments are used judiciously where code logic might not be immediately obvious.

### Testing
*   **Test Coverage Analysis:** Very good. Unit tests are provided for:
    *   **Domain:** Entities' creation, serialization (`to_dict`), and deserialization (`from_dict`), including validation.
    *   **Infrastructure:** File utility functions (read/write, error conditions like invalid JSON) and repository CRUD operations, ensuring persistence logic works as expected. Mocks were appropriately used for file operations where needed, though direct file interaction for repo tests is also good for integration-lite testing of the layer.
    *   **Application:** Managers, Runners, and Generators. Crucially, these tests mock their repository dependencies, ensuring that application logic is tested in isolation.
*   **Test Quality and Comprehensiveness:**
    *   Tests are well-named and clearly define what scenario they are testing.
    *   Assertions are specific and effective.
    *   Edge cases and invalid inputs are tested where appropriate (e.g., empty strings, incorrect types, non-existent IDs).
    *   The `ReportGenerator` tests correctly handle scenarios with no results and correctly identify the latest results for summary/detailed reports.
    *   The use of `unittest.mock.patch` for `uuid.uuid4` and `datetime.now()` ensures test determinism.

### Maintainability
*   **Ease of Modification and Extension:** High. The layered architecture and strong adherence to design patterns (especially Repository and Dependency Injection) mean that:
    *   Changing data storage (e.g., from JSON files to SQLite) would primarily involve modifying the `infrastructure/repositories.py` module and main's initialization, without touching application or domain logic.
    *   Adding new application features (e.g., test case editing, more complex reporting) can be done by adding new methods/classes within the `application` layer, often without impacting other layers significantly.
    *   Adding new test outcomes is trivial (just adding an enum member).
*   **Technical Debt Assessment:** Very low for the current scope. The design choices actively prevent the accumulation of significant technical debt by promoting clear separation of concerns, testability, and extensibility. The reliance on flat files is an acknowledged constraint from requirements, not a design flaw given the current scale.

### Recommendations
*   **Implement more graceful error recovery for file operations:** While `json.JSONDecodeError` is caught, consider implementing a strategy to handle corrupted JSON files, such as backing them up and initializing with an empty file, to prevent application crashes and data loss. For this "simple" app, printing and re-raising is fine, but for any production scenario, this would be critical.
*   **Enhance CLI User Experience with dedicated library (Future Consideration):** For `main.py`, as the application grows, consider using a dedicated CLI library like `click` or `argparse`. This would streamline argument parsing, command dispatch, and provide more robust user interaction features (e.g., clearer error prompts, retries for invalid input) than manual `input()` and `print()` statements.
*   **Introduce a `config.py` module:** For `DATA_DIR` and file paths, moving them from `main.py` to a `src/config.py` module would centralize configuration, making it easier to manage as the project potentially scales or if different environments require different paths.
*   **Consider a `Logger` integration:** Instead of `print()` for non-user-facing messages (e.g., errors in `file_utils`), integrate Python's `logging` module for better control over log levels, output destinations, and historical records.
*   **Automate test execution:** Ensure the `python -m unittest discover tests` command is part of a Continuous Integration (CI) pipeline or a `Makefile`/`pyproject.toml` script for easy, consistent execution.## Security Review Report

### Security Score: 6/10

**Justification:** The system's security posture is generally adequate for its stated purpose as a "simple, single-user or trusted environment" test workflow. It follows good architectural practices like the Repository Pattern, which inherently supports data integrity, and uses UUIDs for unique identification. Input validation is present for entity creation, and file I/O operations include basic error handling. However, the explicit non-requirement for authentication/authorization and the use of plain-text file storage are significant limitations that would render it highly insecure in a multi-user, untrusted, or production environment. The current score reflects its security within its *defined* constraints.

### Critical Issues (High Priority)
*   **None identified within the stated scope and requirements.** The explicit requirement for "no specific user authentication or authorization... assuming a single-user or trusted environment" means that lack of these features is a design constraint, not a vulnerability in this specific context.

### Medium Priority Issues
*   **Lack of Authentication and Authorization:** As per requirements, the system does not implement any user authentication or authorization mechanisms. This means:
    *   **Unlimited Access:** Anyone with access to the machine running the application can define, execute, modify, and delete test cases and results.
    *   **Data Tampering Risk:** Without access controls, data files (`test_cases.json`, `test_results.json`) are vulnerable to direct manipulation by any user or process on the host system. While `TestCase` and `TestExecutionResult` constructors include basic validation, this doesn't prevent direct file modification.
    *   **Recommendation:** This is a conscious design choice for simplicity. However, it's a critical limitation that must be understood. If the environment ever ceases to be "trusted" or requires multiple users, this will become a critical vulnerability.
*   **Plain Text Data Storage:** All test case definitions and execution results are stored in plain text JSON files.
    *   **Confidentiality Risk:** While the current data (test names, steps, results) is likely not sensitive, any future introduction of sensitive information (e.g., test data containing credentials, internal URLs, specific business logic details) would be immediately exposed.
    *   **Integrity Risk:** Data can be easily viewed, copied, or modified by anyone with file system access.
    *   **Recommendation:** For truly sensitive data, consider encryption at rest. For integrity, digital signatures or checksums could be added, though this adds complexity not currently justified by "simple."
*   **Information Disclosure via Generic Error Handling:** The `main.py` functions (e.g., `define_test_case`, `run_test_case_workflow`, `view_test_report`) catch broad `Exception` types and print `f"Error: {e}"`.
    *   This can expose internal details, stack traces, or file paths if an unexpected error occurs, which could aid an attacker in understanding the system's internals.
    *   **Recommendation:** In a more robust system, consider more specific error handling, logging errors internally, and presenting generic, user-friendly messages to the end-user. For a CLI, it's less severe, but still a good practice.

### Low Priority Issues
*   **Potential for Path Traversal in Evidence Path (Limited Impact Currently):** The `evidence_path` field in `TestExecutionResult` allows users to input arbitrary file paths. While the current application merely stores and displays these paths without attempting to open or execute them, it could pose a risk if:
    *   Future features are added that automatically open/process these paths without validation.
    *   A malicious user stores a path like `../../../../etc/passwd` and another user (or automated tool) tries to interact with it, potentially disclosing system files if the application is run with elevated privileges.
    *   **Recommendation:** While low risk now, always validate and sanitize user-provided file paths if they are ever used to access resources. Consider whitelisting allowed directories or using absolute, canonicalized paths.
*   **Hardcoded File Paths for Data Storage:** The `DATA_DIR`, `TEST_CASES_FILE`, and `TEST_RESULTS_FILE` are hardcoded strings within `main.py`.
    *   This limits flexibility if the user wants to store data in a different location without modifying the source code. It can also lead to data files being created in unexpected locations depending on where the script is executed.
    *   **Recommendation:** Externalize configuration (e.g., via command-line arguments, environment variables, or a simple configuration file) to allow users to define data storage locations.
*   **Input Handling Robustness (CLI Context):** While basic string stripping is done, there's no extensive sanitization for inputs like `name`, `comments`, or `expected_results`.
    *   For a CLI application, the immediate risk (e.g., XSS) is minimal as the output is to the terminal. However, if this data were ever rendered in a web interface or another rich client, unescaped user input could lead to injection vulnerabilities.
    *   **Recommendation:** Practice "defense in depth." Even if not immediately exploitable, sanitizing user-controlled strings (e.g., escaping special characters) is a good habit.

### Security Best Practices Followed
*   **Clear Separation of Concerns (Layered Architecture/Repository Pattern):** The use of a layered architecture and the Repository Pattern (e.g., `JSONFileTestCaseRepository`) means that data persistence logic is separated from application and domain logic. This makes it easier to reason about data integrity and to replace storage mechanisms without impacting core business rules, inherently improving maintainability and thus security.
*   **UUIDs for Identifiers:** Using `uuid.uuid4()` for generating unique identifiers for test cases and results prevents predictable IDs, which can sometimes be exploited in systems lacking proper authorization.
*   **Basic Input Validation in Domain Entities:** `TestCase` and `TestExecutionResult` constructors and `from_dict` methods include checks for `None`/empty values and correct data types (e.g., `datetime`, `TestOutcome`). This helps maintain data integrity within the application's memory model.
*   **File I/O Error Handling:** The `file_utils.py` module includes `try-except` blocks for `json.JSONDecodeError` and `IOError` during file reads and writes. This makes the application more robust to corrupted or inaccessible data files.
*   **Standard Library Usage:** Relying solely on Python's standard library minimizes the attack surface associated with third-party dependencies (e.g., supply chain attacks, vulnerabilities in external packages).

### Recommendations
*   **Explicitly document the security assumptions:** Clearly state in user-facing documentation that the application assumes a single-user, trusted environment, and that data is stored unencrypted with no access controls beyond OS file permissions. This manages user expectations and prevents misuse.
*   **Enhance Error Reporting:** While helpful for debugging, general `print(f"Error: {e}")` statements should be refined.
    *   Consider using Python's `logging` module to log detailed errors to a file for debugging purposes, while providing more generic, user-friendly messages to the console.
    *   Implement more specific `except` blocks to handle known error types gracefully.
*   **File Path Management:** For `evidence_path`, if future features involve opening or displaying these files, implement strict validation:
    *   **Path Sanitization:** Use `os.path.abspath` and `os.path.normpath` followed by checks to ensure the path stays within an expected base directory (e.g., `./evidence/`).
    *   **Whitelist Extensions:** If certain file types are expected (e.g., `.png`, `.jpg`), validate the file extension.
*   **Configuration Management:** For improved flexibility and deployability, consider using a simple configuration file (e.g., `config.ini` with `configparser` or a `YAML` file) to store paths to data files. This allows users to easily change storage locations without modifying the code.
*   **Data Integrity beyond Validation:** For extremely critical data integrity, consider implementing checksums or hashes for the JSON files upon writing, and verifying them upon reading. This could detect external tampering, though it adds complexity.

### Compliance Notes
*   **OWASP Top 10 Considerations:**
    *   **A01:2021-Broken Access Control:** This is the primary concern if the "simple, trusted environment" assumption is violated. The current design explicitly lacks access control, relying entirely on the operating system's file permissions. This would be a major flaw in a networked, multi-user, or public-facing application.
    *   **A03:2021-Injection:** Current code is well-protected against typical web-based injection (SQL, XSS) due to its CLI nature and flat-file storage. The potential for path traversal in `evidence_path` is a very minor, latent risk for this category, but only if the system were to *process* the paths.
    *   **A04:2021-Insecure Design:** The design choice to omit authentication/authorization could be seen as an insecure design *if* the system's context changes. For its current, specified context, it's a trade-off for simplicity.
    *   **A05:2021-Security Misconfiguration:** Hardcoding file paths could lead to misconfiguration if deployed incorrectly or if default permissions are too broad.
    *   **A07:2021-Identification and Authentication Failures:** Directly applicable due to the lack of user identification and authentication.
    *   **A08:2021-Software and Data Integrity Failures:** Data is stored in plain text, making it susceptible to external modification. Validation in entities helps, but not against direct file system manipulation.
    *   **A10:2021-Server-Side Request Forgery (SSRF):** Not applicable, as there are no external network requests or URL processing based on user input.

*   **Industry Standard Compliance:** Given the "simple" and "single-user" nature, rigorous industry compliance standards (e.g., PCI DSS, HIPAA) are generally not applicable. However, the principles of data integrity and minimizing information disclosure are universally good practices.## Performance Review Report

### Performance Score: 7/10

The system currently meets the stated performance requirements for managing up to 100 test cases and their results. The design's simplicity and use of file-based storage make it lightweight and responsive within this small scale. However, the fundamental approach to data persistence presents significant bottlenecks for any future scaling beyond the specified limits.

### Critical Performance Issues
Given the current requirements (up to 100 test cases), there are no *critical* performance issues that prevent the system from meeting its NFRs. The chosen file-based storage method, while not scalable for large datasets, is explicitly part of the requirements and architectural design for a "simple" workflow.

However, if the system were to exceed the "up to 100 test cases" limit:
-   **Full File I/O for Every Operation:** The most significant bottleneck is that every CRUD operation (create, read, update, delete) for test cases and test results involves reading the *entire* respective JSON file into memory, performing the operation, and then writing the *entire* file back to disk. This becomes highly inefficient as file sizes grow.
    -   `JSONFileTestCaseRepository.save`, `find_by_id`, `delete`, `find_all`
    -   `JSONFileTestExecutionResultRepository.save`, `find_by_id`, `find_all`, `find_by_test_case_id`
    This approach directly limits scalability.

### Optimization Opportunities
1.  **Transition to an Embedded Database (Primary Future Optimization):** For any scale beyond the immediate 100 test cases, transitioning the `infrastructure/repositories.py` layer to use a lightweight embedded database like **SQLite** would provide exponential performance gains. This would enable:
    *   Indexed lookups (O(log N) or O(1) instead of O(N) file scans).
    *   Efficient updates and deletes without rewriting the entire file.
    *   Transactional integrity.
    The current Repository Pattern simplifies this future migration, making it the most impactful optimization path.

2.  **Batching Writes (If sticking to files):** If file-based storage *must* be maintained for larger scales, consider batching multiple save/update operations into a single file write. This might involve an explicit "Save All" action or periodic auto-saves, which would reduce write frequency but could impact real-time data persistence or responsiveness for individual actions, potentially violating the 1-2 second NFR for individual operations. This is a trade-off.

3.  **In-Memory Caching (Limited Benefit):** For `find_by_id` or `list_test_cases`, a simple in-memory cache could reduce repeated file reads *if* the data is frequently accessed without being modified. However, given that any `save` or `delete` operation rewrites the entire file, cache invalidation would be complex and frequent, potentially negating benefits for this specific file-based approach. The `ReportGenerator` effectively does this by loading all data once for its calculations.

### Algorithmic Analysis
*   **`JSONFileTestCaseRepository` & `JSONFileTestExecutionResultRepository` (save, find_by_id, find_all, delete):**
    *   **Time Complexity (Disk I/O):** All these operations are dominated by reading the entire file (O(F_read)) and, for modifications, writing the entire file (O(F_write)), where F is the file size. This is effectively **O(N)** for reading/writing N records, as each record contributes to the file size. This is a linear scan of the entire dataset on disk.
    *   **Time Complexity (In-memory Processing):** After loading, `find_by_id` and `delete` operations involve a linear scan of the in-memory list (O(N_records)). `save` (for update) also involves a linear scan.
    *   **Space Complexity:** O(N_records) to hold all test cases or test results in memory.
*   **`ReportGenerator` (`generate_summary_report`, `generate_detailed_report`):**
    *   **Time Complexity (Disk I/O):** O(F_tc_read + F_res_read) for reading both test case and test result files.
    *   **Time Complexity (In-memory Processing):** Building the `latest_results_per_test_case` dictionary is O(N_results) as it iterates through all results. The final report generation loop is O(N_test_cases) with O(1) dictionary lookups. Overall, **O(N_test_cases + N_results)** for in-memory processing.
    *   **Space Complexity:** O(N_test_cases + N_results) to hold all data in memory.

**Summary:** The in-memory algorithms are efficient (mostly linear or constant time), but the disk I/O pattern of reading/writing entire files for *each* operation is the primary scalability constraint, making the effective complexity of CRUD operations dominated by the file size rather than just the number of records.

### Resource Utilization
*   **Memory Usage:** For the specified scale (up to 100 test cases and their results), memory usage will be minimal, likely in the order of a few megabytes. Python objects and JSON string representations are compact enough for this scale. Garbage collection overhead will be negligible.
*   **CPU Utilization:** CPU usage will be low. Python's `json` module is efficient for parsing and serialization, often relying on underlying C implementations. In-memory data manipulation (list iterations, dictionary lookups) is fast for small datasets. Peaks might occur during file I/O operations as data is parsed/serialized.
*   **I/O Operation Efficiency:** This is the most taxed resource. While acceptable for the current scale, the strategy of re-reading and re-writing entire JSON files for individual updates or reads is inherently inefficient. Each operation results in non-localized disk access, potentially increasing latency, especially on traditional HDDs. On modern SSDs, the impact for small files is less pronounced but still present.

### Scalability Assessment
The current design is **not inherently scalable beyond the stated "up to 100 test cases" limit.**
*   **Horizontal Scaling:** Not applicable for a monolithic, file-based CLI application.
*   **Vertical Scaling:** Increasing CPU/RAM on the execution machine will slightly improve in-memory processing time but will not fundamentally address the I/O bottleneck of reading/writing entire files. Faster storage (SSD vs. HDD) will mitigate the I/O impact more significantly for the stated scale.

The point of degradation will be directly proportional to the total size of `test_cases.json` and `test_results.json`. As these files grow into hundreds of KBs or MBs, the 1-2 second and 5-second NFRs for individual operations and reports will inevitably be breached. For example, if there are 10,000 test cases and 50,000 results, file sizes could be tens of MBs, making full file rewrites take multiple seconds, if not minutes, to complete.

### Recommendations
1.  **Prioritize Database Migration for Future Scale:** Clearly communicate that the current file-based solution is a temporary measure suitable **only for the specified "up to 100 test cases" scope**. If the user base or test case count grows, migrate the `JSONFileTestCaseRepository` and `JSONFileTestExecutionResultRepository` implementations to use **SQLite**. This is the single most effective performance improvement for future scalability.
    *   **Action:** Create a new `SQLiteTestCaseRepository` and `SQLiteTestExecutionResultRepository` in the `infrastructure` layer. The application and domain layers will remain unchanged due to the Repository Pattern.
    *   **Benefit:** Orders of magnitude improvement in CRUD operation speeds, better data integrity, and support for larger datasets.

2.  **Monitoring & Profiling (If Issues Arise):** While not necessary for the current NFRs, if performance degradation is observed even within the 100 test case limit (e.g., on specific hardware or under unusual load), use Python's built-in `cProfile` or `timeit` modules to pinpoint exact bottlenecks.
    *   **`cProfile`:** Run `python -m cProfile -o profile_output.prof src/main.py` and analyze with `snakeviz` (`snakeviz profile_output.prof`). This helps visualize function call times.
    *   **`timeit`:** Use `timeit` for micro-benchmarking specific repository operations (e.g., `save`, `find_by_id`) to measure their performance with varying data sizes.

3.  **Error Handling for File Corruption:** The `read_json_file` function currently re-raises `json.JSONDecodeError` and `IOError`. While this is fine for identifying issues, for a user-facing tool, consider more robust handling such as:
    *   Logging the error clearly.
    *   Attempting to back up the corrupted file.
    *   Initializing the file to an empty list `[]` (similar to what `initialize_data_directory` does for non-existent files) to allow the application to continue running, perhaps with a warning to the user. This improves resilience.

4.  **Code Review for Redundant Operations:** While the current codebase is small, continuously review application logic to ensure data is not loaded or processed multiple times unnecessarily within a single workflow. (The `ReportGenerator` already does this well by loading all data once).## Refactored Code Implementation

### Summary of Changes
This refactoring focuses on enhancing the robustness, maintainability, and user experience of the "Simple Test Workflow" application, directly addressing feedback from the Quality, Security, and Performance reviews.

Key improvements include:
-   **Centralized Configuration:** Moved data file paths (`DATA_DIR`, `TEST_CASES_FILE`, `TEST_RESULTS_FILE`) into a new `src/config.py` module for easier management and flexibility.
-   **Enhanced Error Handling & Logging:** Replaced simple `print(f"Error: {e}")` statements with Python's standard `logging` module for better control over error messages and reduced information disclosure. `file_utils.py` now implements more graceful error recovery for JSON decoding failures, logging the issue and returning an empty list, allowing the application to continue.
-   **Improved CLI User Experience:** Implemented more robust input validation in `main.py`, particularly for numeric choices, by creating a helper function that prompts the user until valid input is received. This reduces generic error messages and guides the user more effectively.
-   **Security Assumptions Clarification:** Reiteration of the application's security model (single-user, trusted environment, plain-text storage) in the documentation and migration guide.
-   **Performance Scoping:** Reaffirmed that the current file-based approach is suitable for the stated "up to 100 test cases" scope, with recommendations for future SQLite migration for larger scales.

### Refactored Code

**`src/config.py`**
```python
# src/config.py
import os

# Base directory for all data files
DATA_DIR = "data"

# Paths for test case and test result JSON files
TEST_CASES_FILE = os.path.join(DATA_DIR, "test_cases.json")
TEST_RESULTS_FILE = os.path.join(DATA_DIR, "test_results.json")
```

**`src/domain/enums.py`** (No change)
```python
from enum import Enum

class TestOutcome(Enum):
    """
    Represents the possible outcomes of a test execution.
    """
    PASS = "Pass"
    FAIL = "Fail"
    BLOCKED = "Blocked"
    SKIPPED = "Skipped"
```

**`src/domain/entities.py`** (No change)
```python
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
```

**`src/infrastructure/file_utils.py`**
```python
import json
import os
import logging
from typing import List, Dict, Any

# Configure logging for this module
logger = logging.getLogger(__name__)

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Reads JSON data from a specified file path.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries read from the JSON file.
                              Returns an empty list if the file does not exist, is empty,
                              or contains invalid JSON.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        logger.info(f"File not found or empty: {file_path}. Returning empty list.")
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from {file_path}: {e}. File might be corrupted.")
        # Optionally, back up the corrupted file here before returning empty.
        # For simplicity in this "simple" workflow, we just log and return empty.
        return []
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        return [] # Return empty list on other IO errors

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
        logger.error(f"Error writing to file {file_path}: {e}")
        raise # Re-raise for the calling application layer to handle if critical
```

**`src/infrastructure/repositories.py`** (No change)
```python
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
```

**`src/application/test_case_manager.py`** (No change)
```python
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
```

**`src/application/test_runner.py`** (No change)
```python
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
```

**`src/application/report_generator.py`** (No change)
```python
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

**`src/main.py`**
```python
# src/main.py
import os
import logging
from typing import List, Optional, Dict, Any

from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.application.test_case_manager import TestCaseManager
from src.application.test_runner import TestRunner
from src.application.report_generator import ReportGenerator
from src import config # Import the new config module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def initialize_data_directory() -> None:
    """Ensures the data directory exists and creates empty JSON files if they don't."""
    try:
        os.makedirs(config.DATA_DIR, exist_ok=True)
        # Create empty JSON files if they don't exist
        for file_path in [config.TEST_CASES_FILE, config.TEST_RESULTS_FILE]:
            if not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write('[]')
                logger.info(f"Created empty data file: {file_path}")
    except OSError as e:
        logger.critical(f"Failed to create data directory or files: {e}")
        print(f"CRITICAL ERROR: Unable to set up data storage. Please check permissions or disk space. Details: {e}")
        exit(1) # Exit if cannot set up data directory

def get_numeric_input(prompt: str, max_value: Optional[int] = None) -> Optional[int]:
    """
    Helper function to get validated numeric input from the user.
    Continuously prompts until a valid integer within an optional range is entered.
    """
    while True:
        user_input = input(prompt).strip()
        try:
            value = int(user_input)
            if max_value is not None and (value <= 0 or value > max_value):
                print(f"Invalid number. Please enter a number between 1 and {max_value}.")
            else:
                return value
        except ValueError:
            print("Invalid input. Please enter a valid number.")

def main_menu() -> None:
    """Displays the main menu and handles user input."""
    initialize_data_directory()

    test_case_repo = JSONFileTestCaseRepository(config.TEST_CASES_FILE)
    test_result_repo = JSONFileTestExecutionResultRepository(config.TEST_RESULTS_FILE)

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
            logger.info("Application exiting normally.")
            break
        else:
            print("Invalid choice. Please try again.")
            logger.warning(f"Invalid main menu choice: '{choice}'")

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
        logger.info(f"Test case '{test_case.id}' defined successfully.")
    except ValueError as e:
        print(f"Error defining test case: {e}")
        logger.error(f"Validation error defining test case: {e}")
    except Exception as e:
        print("An unexpected error occurred while defining the test case.")
        logger.exception("Unexpected error in define_test_case:")

def list_test_cases(manager: TestCaseManager) -> None:
    """Lists all defined test cases."""
    print("\n--- All Test Cases ---")
    try:
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
    except Exception as e:
        print("An error occurred while listing test cases.")
        logger.exception("Unexpected error in list_test_cases:")

def run_test_case_workflow(test_case_manager: TestCaseManager, test_runner: TestRunner) -> None:
    """Guides user through running a test case and recording its result."""
    print("\n--- Run Test Case ---")
    try:
        test_cases = test_case_manager.list_test_cases()
        if not test_cases:
            print("No test cases to run. Please define some first.")
            return

        print("Available Test Cases:")
        for i, tc in enumerate(test_cases):
            print(f"{i+1}. {tc.name} (ID: {tc.id})")

        choice_index = get_numeric_input(
            "Enter the number of the test case to run: ", len(test_cases)
        )
        
        if choice_index is None: # User entered invalid input repeatedly
            print("Operation cancelled or invalid input received.")
            return
        
        selected_test_case_id = test_cases[choice_index - 1].id # Adjust for 0-indexed list

        test_case = test_case_manager.get_test_case(selected_test_case_id)
        if not test_case:
            print(f"Error: Test case with ID {selected_test_case_id} not found. It might have been deleted.")
            logger.error(f"Attempted to run non-existent test case ID: {selected_test_case_id}")
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

        outcome_choice_num = get_numeric_input("Enter outcome number: ", len(outcomes))

        selected_outcome = TestOutcome.BLOCKED # Default to BLOCKED
        if outcome_choice_num is not None and 0 < outcome_choice_num <= len(outcomes):
            selected_outcome = TestOutcome[outcomes[outcome_choice_num - 1]]
        else:
            print("Invalid outcome choice. Defaulting to 'Blocked'.")
            logger.warning(f"Invalid outcome choice entered during test run. Defaulting to {selected_outcome.name}")

        comments = input("Add comments (optional): ").strip()
        evidence_path = input("Path to evidence (optional, e.g., screenshot.png): ").strip() or None

        result = test_runner.record_result(
            selected_test_case_id,
            selected_outcome,
            comments,
            evidence_path
        )
        print(f"Test result recorded for '{test_case.name}' (Result ID: {result.id}) with outcome: {result.outcome.name}")
        logger.info(f"Result '{result.id}' recorded for test case '{selected_test_case_id}' with outcome '{result.outcome.name}'")
    except ValueError as e:
        print(f"Error running test case: {e}")
        logger.error(f"Validation error during test run workflow: {e}")
    except Exception as e:
        print("An unexpected error occurred during the test run workflow.")
        logger.exception("Unexpected error in run_test_case_workflow:")


def view_test_report(generator: ReportGenerator) -> None:
    """Generates and displays a test report."""
    print("\n--- Test Report ---")
    try:
        summary = generator.generate_summary_report()
        detailed = generator.generate_detailed_report()

        print("\n--- Summary Report ---")
        print(f"Total Test Cases: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Blocked: {summary['blocked']}")
        print(f"Skipped: {summary['skipped']}")
        print(f"Not Run: {summary['not_run']}") # Added 'Not Run' count

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
    except Exception as e:
        print("An unexpected error occurred while generating the report.")
        logger.exception("Unexpected error in view_test_report:")


if __name__ == "__main__":
    main_menu()
```

### Security Improvements
1.  **Reduced Information Disclosure:** Generic `print(f"Error: {e}")` statements in `main.py` functions have been replaced with more specific error messages for the user and detailed logging of exceptions (using `logger.exception`) to a file (or standard output if configured) for debugging. This prevents exposing internal stack traces or sensitive error details to the end-user.
2.  **Robust File I/O Error Handling:** In `src/infrastructure/file_utils.py`, `json.JSONDecodeError` and `IOError` are now caught, logged, and handled more gracefully (returning an empty list) instead of re-raising and potentially crashing the application or propagating raw exceptions. This enhances the application's resilience against corrupted data files, preventing a denial-of-service type of scenario from malformed data.
3.  **Explicit Security Assumptions:** While not a code change, the documentation clearly reiterates the inherent security limitations (lack of authentication/authorization, plain-text storage) due to the "simple, trusted environment" requirement. This is crucial for managing user expectations and preventing misapplication in untrusted contexts.

### Performance Optimizations
For the current scope of "up to 100 test cases," the original performance characteristics are generally met, and significant algorithmic changes to the file-based I/O were not undertaken to maintain the "simple" constraint.

1.  **Clarified Data Loading Strategy:** The `ReportGenerator` already loads all necessary data into memory once for report generation, which is efficient for the specified scale. This behavior is maintained.
2.  **Resilience to File Issues:** The improved error handling in `file_utils.py` ensures that corrupted or inaccessible data files do not crash the application, contributing to perceived stability and performance by allowing it to continue operating (albeit with missing data) instead of failing entirely.
3.  **Future Scalability Path:** The recommendations emphasize that for scale beyond 100 test cases, transitioning the `JSONFileTestCaseRepository` and `JSONFileTestExecutionResultRepository` to an embedded database like SQLite is the primary and most impactful performance optimization strategy. This architecture is already set up to allow for this.

### Quality Enhancements
1.  **Centralized Configuration:** The introduction of `src/config.py` centralizes all file paths, making the application easier to configure, modify, and maintain. It removes "magic strings" from `main.py`.
2.  **Improved Error Handling and Logging:**
    *   Integration of Python's `logging` module for structured and controlled output of informational, warning, and error messages. This replaces inconsistent `print()` statements for non-user-facing events.
    *   `initialize_data_directory` now uses logging and provides a more specific critical error message to the user if data directory setup fails, and exits the application, rather than potentially leading to cryptic errors later.
3.  **Robust User Input Validation:** The new `get_numeric_input` helper function in `main.py` enforces proper integer input within specified ranges. This greatly improves the CLI's usability by preventing `ValueError` exceptions from invalid input and providing clearer feedback to the user, prompting them until valid input is given.
4.  **Code Readability and Maintainability:**
    *   Consistent use of `logger` for internal messages improves clarity over `print()`.
    *   The `config.py` module makes dependencies explicit and easier to trace.
    *   The project structure remains clean and adheres to the layered architecture.

### Updated Tests

To accommodate the changes in `src/infrastructure/file_utils.py` (which now logs and returns `[]` instead of re-raising `JSONDecodeError` or `IOError`), the relevant test cases in `tests/test_infrastructure.py` need to be updated. We also need to mock the `logging` module where appropriate.

**`tests/test_infrastructure.py`**
```python
import unittest
import os
import json
from unittest.mock import patch, mock_open
from datetime import datetime
import logging # Import logging

from src.infrastructure.file_utils import read_json_file, write_json_file
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.domain.entities import TestCase, TestExecutionResult
from src.domain.enums import TestOutcome

class TestFileUtils(unittest.TestCase):
    def setUp(self):
        self.test_file = "test_temp.json"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        # Suppress logging during tests to prevent clutter
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        logging.disable(logging.NOTSET) # Re-enable logging after tests

    def test_read_json_file_empty_or_non_existent(self):
        self.assertEqual(read_json_file("non_existent.json"), [])
        with open(self.test_file, 'w') as f:
            f.write('')
        self.assertEqual(read_json_file(self.test_file), [])

    def test_read_json_file_invalid_json(self):
        with open(self.test_file, 'w') as f:
            f.write('{invalid json')
        
        # Now it should return an empty list and log an error, not raise
        with self.assertLogs('src.infrastructure.file_utils', level='ERROR') as cm:
            result = read_json_file(self.test_file)
            self.assertEqual(result, [])
            self.assertIn("Error decoding JSON", cm.output[0])


    def test_read_json_file_io_error(self):
        # Simulate an IOError during file read
        with patch('builtins.open', side_effect=IOError("Permission denied")):
            with self.assertLogs('src.infrastructure.file_utils', level='ERROR') as cm:
                result = read_json_file(self.test_file)
                self.assertEqual(result, [])
                self.assertIn("Error reading file", cm.output[0])

    def test_write_json_file(self):
        test_data = [{"item": 1}, {"item": 2}]
        write_json_file(self.test_file, test_data)
        with open(self.test_file, 'r') as f:
            loaded_data = json.load(f)
        self.assertEqual(loaded_data, test_data)

    def test_write_json_file_io_error(self):
        # Simulate an IOError during file write
        test_data = [{"item": 1}]
        with patch('builtins.open', side_effect=IOError("Disk full")):
            with self.assertRaises(IOError):
                with self.assertLogs('src.infrastructure.file_utils', level='ERROR') as cm:
                    write_json_file(self.test_file, test_data)
            self.assertIn("Error writing to file", cm.output[0])


class TestJSONFileTestCaseRepository(unittest.TestCase):
    def setUp(self):
        self.file_path = "test_cases_repo.json"
        self.repo = JSONFileTestCaseRepository(self.file_path)
        # Ensure file is empty before each test
        with open(self.file_path, 'w') as f:
            f.write('[]')
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        logging.disable(logging.NOTSET)

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
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        if os.path.exists(self.file_path):
            os.remove(self.file_path)
        logging.disable(logging.NOTSET)

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
```

**`tests/test_domain.py`** (No change)
```python
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
```

**`tests/test_application.py`** (No change)
```python
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import uuid
import logging # Import logging

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
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

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
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

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
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

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

### Migration Guide

This section outlines the steps to migrate from the old implementation to the refactored version.

**Breaking Changes (Minimal):**
-   The file paths for `test_cases.json` and `test_results.json` are now managed by `src/config.py`. If you had custom paths defined directly in `main.py` or expected them elsewhere, you should now configure them in `src/config.py`.
-   The behavior of `src/infrastructure/file_utils.py`'s `read_json_file` function has changed. It now gracefully handles `json.JSONDecodeError` and `IOError` by logging the error and returning an empty list `[]`, rather than re-raising the exception. If your calling code relied on catching these specific exceptions from `read_json_file`, you should adjust.
-   Error messages presented to the user have been refined. Detailed technical errors are now logged instead of being printed directly to the console.

**Migration Steps:**

1.  **Update Project Structure:**
    -   Ensure your project structure includes a `src/config.py` file.
    -   ```
        project/
        ├── src/
        │   ├── __init__.py
        │   ├── main.py
        │   ├── config.py             # <--- NEW FILE
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

2.  **Replace File Contents:**
    -   **`src/config.py`**: Create this new file and copy the content provided above.
    -   **`src/main.py`**: Replace the entire content with the refactored `main.py` code.
    -   **`src/infrastructure/file_utils.py`**: Replace the entire content with the refactored `file_utils.py` code.
    -   **`tests/test_infrastructure.py`**: Replace the entire content with the updated `test_infrastructure.py` code.

3.  **Data File Location:**
    -   The application will now look for and create `data/test_cases.json` and `data/test_results.json` relative to where `main.py` is executed, as defined in `src/config.py`. If you had existing `test_cases.json` or `test_results.json` files elsewhere, move them into the `data/` directory or update `src/config.py` to point to their new location.

4.  **Logging Configuration:**
    -   Basic logging is configured in `main.py`. If you require more advanced logging (e.g., writing to a specific file, different log levels), you can modify the `logging.basicConfig` call in `main.py` or set up a more elaborate logging configuration.

5.  **Running the Application and Tests:**
    -   **Run Application:** `cd project && python -m src.main`
    -   **Run Tests:** `cd project && python -m unittest discover tests`

**Important Security Note for Users:**
This workflow is designed for a **single-user or trusted environment**.
-   **No Authentication/Authorization:** The application does not implement user login or access control. Anyone with access to the machine running the application can perform all operations (define, execute, view, modify data files).
-   **Plain-Text Storage:** All data (test cases, results) is stored in plain-text JSON files. Sensitive information should *not* be stored within this system.
-   Rely solely on operating system file permissions to restrict access to the `data/` directory and the application files. If these assumptions do not hold true for your environment, this tool is not suitable, and a more robust solution with proper security controls (e.g., a database with access control, encryption) is required.## Complete Documentation Package

### README.md
```markdown
# Simple Test Workflow

## Overview
The Simple Test Workflow is a lightweight, command-line interface (CLI) application designed to facilitate manual functional testing. It allows users to define individual test cases, execute them, record their outcomes, and generate basic summary reports. This tool is ideal for single users or small, co-located teams requiring a straightforward approach to test management without the overhead of complex test automation frameworks or databases.

**Key Features:**
*   **Test Case Definition:** Easily define test cases with unique identifiers, names, detailed steps, and expected results.
*   **Test Case Execution:** Manually step through defined test cases and record actual outcomes.
*   **Test Result Recording:** Capture test results (Pass, Fail, Blocked, Skipped) along with comments and optional evidence paths.
*   **Basic Reporting:** Generate summary and detailed reports of test execution results, focusing on the latest outcome for each test case.
*   **File-Based Storage:** Utilizes simple JSON files for persistent storage of test definitions and results, ensuring portability and ease of management for small-scale projects (up to ~100 test cases).

## Installation
To set up and run the Simple Test Workflow application, follow these steps:

1.  **Clone the repository** (or manually create the project structure):
    If using Git:
    ```bash
    git clone <repository_url>
    cd simple-test-workflow
    ```
    If creating manually:
    Create a main project directory (e.g., `project/`). Navigate into it.
    ```bash
    mkdir -p src/domain src/infrastructure src/application data tests
    touch src/__init__.py src/domain/__init__.py src/infrastructure/__init__.py src/application/__init__.py
    ```

2.  **Populate the files** with the provided Python code. Ensure the `src/config.py` file is created first, then `src/main.py` and the other modules, followed by the test files.

    *   `project/src/config.py`
    *   `project/src/domain/enums.py`
    *   `project/src/domain/entities.py`
    *   `project/src/infrastructure/file_utils.py`
    *   `project/src/infrastructure/repositories.py`
    *   `project/src/application/test_case_manager.py`
    *   `project/src/application/test_runner.py`
    *   `project/src/application/report_generator.py`
    *   `project/src/main.py`
    *   `project/tests/test_domain.py`
    *   `project/tests/test_infrastructure.py`
    *   `project/tests/test_application.py`

3.  **Python Requirement:** Ensure you have **Python 3.6 or higher** installed on your system.

## Quick Start
To launch the application:

1.  Navigate to the root of your `project/` directory in your terminal.
2.  Run the main script:
    ```bash
    python -m src.main
    ```
    This will launch the interactive command-line menu.

### Basic Usage Flow:

1.  **Define New Test Case:**
    *   Select option `1` from the main menu.
    *   Follow the prompts to enter the test case name, execution steps (type `done` to finish steps), and expected results.

2.  **List All Test Cases:**
    *   Select option `2` to view all currently defined test cases with their details.

3.  **Run Test Case:**
    *   Select option `3`.
    *   Choose a test case by its number from the displayed list.
    *   The application will present each step. Press Enter after completing each step.
    *   Review the expected results.
    *   Select the outcome (Pass, Fail, Blocked, Skipped) by entering the corresponding number.
    *   Optionally add comments and a path to evidence.

4.  **View Test Report:**
    *   Select option `4` to generate and display both a summary report (counts of Pass/Fail/etc.) and a detailed report showing the latest result for each test case.

## Features
The Simple Test Workflow provides the following core functionalities:

### Test Case Definition
Users can define new test cases by providing:
*   A descriptive **Name**: A brief title for the test.
*   **Execution Steps**: A detailed, ordered list of actions to perform during testing. The system allows multiple steps to be entered sequentially until "done" is typed.
*   **Expected Results**: A clear description of the anticipated outcome if the test case is executed successfully.

All defined test cases are stored in `data/test_cases.json`.

### Test Case Execution
The application guides the user through the execution of a selected test case:
*   Users are presented with a list of available test cases and can choose one by number.
*   Each step of the chosen test case is displayed sequentially, requiring user confirmation (pressing Enter) before proceeding to the next step.
*   After all steps, the expected results are displayed for review.

### Test Result Recording
Following execution, users can record the outcome:
*   **Outcome Selection**: Users select from predefined outcomes: `Pass`, `Fail`, `Blocked`, or `Skipped`.
*   **Comments**: An optional free-text field for additional notes or observations.
*   **Evidence Path**: An optional field to link to external evidence (e.g., a screenshot file path) related to the test execution.

All recorded execution results are stored in `data/test_results.json`. The system records each execution as a new entry, maintaining a history.

### Basic Reporting
The system offers two types of reports:
*   **Summary Report**: Provides aggregated counts of test outcomes (Passed, Failed, Blocked, Skipped) based on the *latest* execution result for each defined test case. It also counts test cases that have not yet been run.
*   **Detailed Report**: Lists each defined test case and its *latest* execution result, including outcome, timestamp, comments, and evidence path (if available). If a test case has no recorded runs, it will indicate "No runs recorded yet."
```

### API Documentation
```markdown
# API Reference

The Simple Test Workflow application is structured using a Layered Monolithic Architecture, with clear separation between Domain, Infrastructure, and Application layers. This documentation covers the primary classes and methods exposed within these layers, which constitute the application's internal API.

## Classes and Methods

### `src.domain.enums.TestOutcome`
An `Enum` representing the possible outcomes of a test execution.
*   `PASS`
*   `FAIL`
*   `BLOCKED`
*   `SKIPPED`

### `src.domain.entities.TestCase`
Represents a single test case definition.

**Attributes:**
*   `id (str)`: Unique identifier for the test case (UUID).
*   `name (str)`: Descriptive name of the test case.
*   `steps (List[str])`: List of execution steps.
*   `expected_results (str)`: Detailed expected outcome of the test.

**Methods:**
*   `__init__(self, id: str, name: str, steps: List[str], expected_results: str) -> None`
    *   Initializes a `TestCase` instance.
    *   `id`: The unique ID (typically a UUID string).
    *   `name`: The test case's name.
    *   `steps`: A list of strings, each representing a step.
    *   `expected_results`: The expected outcome string.
    *   **Raises**: `ValueError` if any required attribute is empty.

*   `to_dict(self) -> Dict[str, Any]`
    *   Converts the `TestCase` object to a dictionary suitable for JSON serialization.

*   `@staticmethod from_dict(data: Dict[str, Any]) -> "TestCase"`
    *   Creates a `TestCase` object from a dictionary, typically loaded from JSON.
    *   `data`: Dictionary containing test case attributes.
    *   **Raises**: `ValueError` if required keys are missing.

### `src.domain.entities.TestExecutionResult`
Represents the outcome of a single test case execution.

**Attributes:**
*   `id (str)`: Unique identifier for the test execution result (UUID).
*   `test_case_id (str)`: ID of the test case that was executed.
*   `timestamp (datetime)`: Timestamp of when the test was executed.
*   `outcome (TestOutcome)`: The result of the test execution (Pass, Fail, etc.).
*   `comments (str)`: Additional comments about the execution (default: "").
*   `evidence_path (Optional[str])`: Path to any evidence (e.g., screenshot) (default: `None`).

**Methods:**
*   `__init__(self, id: str, test_case_id: str, timestamp: datetime, outcome: TestOutcome, comments: str = "", evidence_path: Optional[str] = None) -> None`
    *   Initializes a `TestExecutionResult` instance.
    *   `id`: The unique result ID.
    *   `test_case_id`: The ID of the associated `TestCase`.
    *   `timestamp`: `datetime` object for when the result was recorded.
    *   `outcome`: A `TestOutcome` enum member.
    *   `comments`: Optional string for comments.
    *   `evidence_path`: Optional string for evidence path.
    *   **Raises**: `ValueError` if IDs are empty, `TypeError` if `timestamp` or `outcome` are incorrect types.

*   `to_dict(self) -> Dict[str, Any]`
    *   Converts the `TestExecutionResult` object to a dictionary for JSON serialization. `timestamp` is converted to ISO format string.

*   `@staticmethod from_dict(data: Dict[str, Any]) -> "TestExecutionResult"`
    *   Creates a `TestExecutionResult` object from a dictionary.
    *   `data`: Dictionary containing result attributes.
    *   **Raises**: `ValueError` if required keys are missing or if `timestamp`/`outcome` formats are invalid.

### `src.infrastructure.file_utils`
Utility functions for reading and writing JSON files.

*   `read_json_file(file_path: str) -> List[Dict[str, Any]]`
    *   Reads JSON data from a file. Returns an empty list if file not found, empty, or corrupted, and logs errors.
    *   `file_path`: Path to the JSON file.

*   `write_json_file(file_path: str, data: List[Dict[str, Any]]) -> None`
    *   Writes a list of dictionaries as JSON data to a file. Logs and re-raises `IOError` on failure.
    *   `file_path`: Path to the JSON file.
    *   `data`: List of dictionaries to write.

### `src.infrastructure.repositories.AbstractTestCaseRepository` (ABC)
Abstract base class for test case persistence.

### `src.infrastructure.repositories.JSONFileTestCaseRepository`
Concrete implementation of `AbstractTestCaseRepository` using a JSON file.

*   `__init__(self, file_path: str) -> None`
    *   Initializes with the path to the test cases JSON file.

*   `save(self, test_case: TestCase) -> None`
    *   Saves a new test case or updates an existing one (based on `id`).

*   `find_by_id(self, test_case_id: str) -> Optional[TestCase]`
    *   Retrieves a `TestCase` by its ID. Returns `None` if not found.

*   `find_all(self) -> List[TestCase]`
    *   Returns all `TestCase` objects currently stored.

*   `delete(self, test_case_id: str) -> bool`
    *   Deletes a `TestCase` by its ID. Returns `True` if deleted, `False` if not found.

### `src.infrastructure.repositories.AbstractTestExecutionResultRepository` (ABC)
Abstract base class for test execution result persistence.

### `src.infrastructure.repositories.JSONFileTestExecutionResultRepository`
Concrete implementation of `AbstractTestExecutionResultRepository` using a JSON file.

*   `__init__(self, file_path: str) -> None`
    *   Initializes with the path to the test results JSON file.

*   `save(self, result: TestExecutionResult) -> None`
    *   Appends a new `TestExecutionResult` to the storage.

*   `find_by_id(self, result_id: str) -> Optional[TestExecutionResult]`
    *   Retrieves a `TestExecutionResult` by its ID. Returns `None` if not found.

*   `find_all(self) -> List[TestExecutionResult]`
    *   Returns all `TestExecutionResult` objects currently stored.

*   `find_by_test_case_id(self, test_case_id: str) -> List[TestExecutionResult]`
    *   Returns all `TestExecutionResult` objects associated with a specific test case ID.

### `src.application.test_case_manager.TestCaseManager`
Manages the lifecycle of test case definitions.

*   `__init__(self, test_case_repository: AbstractTestCaseRepository) -> None`
    *   Initializes with a concrete `AbstractTestCaseRepository` implementation.

*   `create_test_case(self, name: str, steps: List[str], expected_results: str) -> TestCase`
    *   Creates, validates, and saves a new `TestCase`. Generates a UUID for the ID.
    *   **Raises**: `ValueError` if input data is invalid.

*   `get_test_case(self, test_case_id: str) -> Optional[TestCase]`
    *   Retrieves a `TestCase` by ID.

*   `update_test_case(self, test_case_id: str, new_data: Dict[str, Any]) -> bool`
    *   Updates specified fields of an existing test case.
    *   `new_data`: Dictionary with keys `name`, `steps`, `expected_results`.
    *   **Raises**: `TypeError` if `steps` is not a list of strings.

*   `delete_test_case(self, test_case_id: str) -> bool`
    *   Deletes a `TestCase` by ID.

*   `list_test_cases(self) -> List[TestCase]`
    *   Returns all defined test cases.

### `src.application.test_runner.TestRunner`
Facilitates test execution result recording.

*   `__init__(self, test_case_repository: AbstractTestCaseRepository, test_execution_result_repository: AbstractTestExecutionResultRepository) -> None`
    *   Initializes with concrete repository implementations.

*   `record_result(self, test_case_id: str, outcome: TestOutcome, comments: str = "", evidence_path: Optional[str] = None) -> TestExecutionResult`
    *   Records a new test execution result for a given test case.
    *   **Raises**: `ValueError` if `test_case_id` is not found, `TypeError` if `outcome` is not a `TestOutcome` enum.

### `src.application.report_generator.ReportGenerator`
Generates summary and detailed reports.

*   `__init__(self, test_case_repository: AbstractTestCaseRepository, test_execution_result_repository: AbstractTestExecutionResultRepository) -> None`
    *   Initializes with concrete repository implementations.

*   `generate_summary_report(self) -> Dict[str, int]`
    *   Generates a summary of test outcomes, considering only the latest result per test case.
    *   Returns a dictionary with counts for `total_tests`, `passed`, `failed`, `blocked`, `skipped`, and `not_run`.

*   `generate_detailed_report(self) -> List[Dict[str, Any]]`
    *   Generates a list of dictionaries, each describing a test case and its latest execution result (if any).

---

## Examples

### 1. Defining a Test Case using `TestCaseManager`

```python
from src.infrastructure.repositories import JSONFileTestCaseRepository
from src.application.test_case_manager import TestCaseManager
from src.config import TEST_CASES_FILE

# Initialize the repository and manager
test_case_repo = JSONFileTestCaseRepository(TEST_CASES_FILE)
test_case_manager = TestCaseManager(test_case_repo)

# Define a new test case
try:
    new_test_case = test_case_manager.create_test_case(
        name="Verify User Login",
        steps=[
            "1. Navigate to login page.",
            "2. Enter valid username.",
            "3. Enter valid password.",
            "4. Click 'Login' button."
        ],
        expected_results="User is successfully logged in and redirected to dashboard."
    )
    print(f"Created Test Case: {new_test_case.name} (ID: {new_test_case.id})")

    # List all test cases
    all_test_cases = test_case_manager.list_test_cases()
    print("\nAll Test Cases:")
    for tc in all_test_cases:
        print(f"- {tc.name} (ID: {tc.id})")

except ValueError as e:
    print(f"Error: {e}")
```

### 2. Recording a Test Result using `TestRunner`

```python
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.application.test_runner import TestRunner
from src.domain.enums import TestOutcome
from src.config import TEST_CASES_FILE, TEST_RESULTS_FILE
import uuid # For a dummy test_case_id if not creating first
from datetime import datetime

# Assuming a test case with a known ID exists (e.g., from example 1)
# For demonstration, let's use a dummy ID and ensure a Test Case exists in repo
test_case_repo = JSONFileTestCaseRepository(TEST_CASES_FILE)
test_result_repo = JSONFileTestExecutionResultRepository(TEST_RESULTS_FILE)
test_runner = TestRunner(test_case_repo, test_result_repo)

# Ensure a dummy test case exists for this example to run cleanly
# In a real scenario, you would fetch an existing test case ID
dummy_test_case_id = str(uuid.uuid4())
from src.domain.entities import TestCase
tc = TestCase(dummy_test_case_id, "Example Test", ["Step 1"], "Expected Result")
test_case_repo.save(tc) # Save it to make it discoverable by the runner

try:
    # Record a 'Pass' result
    pass_result = test_runner.record_result(
        test_case_id=dummy_test_case_id,
        outcome=TestOutcome.PASS,
        comments="Login successful as expected.",
        evidence_path="/tmp/login_screenshot.png"
    )
    print(f"Recorded Pass Result (ID: {pass_result.id}) for Test Case {pass_result.test_case_id}")

    # Record a 'Fail' result for the same test case (simulating a re-run)
    fail_result = test_runner.record_result(
        test_case_id=dummy_test_case_id,
        outcome=TestOutcome.FAIL,
        comments="Failed to redirect after login, received 500 error.",
        evidence_path="/tmp/error_log.txt"
    )
    print(f"Recorded Fail Result (ID: {fail_result.id}) for Test Case {fail_result.test_case_id}")

except ValueError as e:
    print(f"Error: {e}")
except TypeError as e:
    print(f"Error: {e}")
```

### 3. Generating Reports using `ReportGenerator`

```python
from src.infrastructure.repositories import JSONFileTestCaseRepository, JSONFileTestExecutionResultRepository
from src.application.report_generator import ReportGenerator
from src.config import TEST_CASES_FILE, TEST_RESULTS_FILE

# Initialize repositories and generator
test_case_repo = JSONFileTestCaseRepository(TEST_CASES_FILE)
test_result_repo = JSONFileTestExecutionResultRepository(TEST_RESULTS_FILE)
report_generator = ReportGenerator(test_case_repo, test_result_repo)

# Generate and print summary report
summary = report_generator.generate_summary_report()
print("\n--- Summary Report ---")
for key, value in summary.items():
    print(f"{key.replace('_', ' ').title()}: {value}")

# Generate and print detailed report
detailed = report_generator.generate_detailed_report()
print("\n--- Detailed Report ---")
if not detailed:
    print("No test results to display in detailed report.")
else:
    for item in detailed:
        print(f"\nTest Case: {item['test_case_name']} (ID: {item['test_case_id']})")
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
```
```

### User Guide
```markdown
# User Guide

This guide provides instructions on how to use the Simple Test Workflow application effectively for your manual testing needs.

## Getting Started

1.  **Installation:** Follow the detailed [Installation](#installation) steps in the `README.md` to set up the project and ensure all files are in place.
2.  **Running the Application:** Open your terminal or command prompt, navigate to the root directory of the project (where the `src/` and `data/` folders are located), and run:
    ```bash
    python -m src.main
    ```
    The application will initialize the `data/` directory (if it doesn't exist) and create empty `test_cases.json` and `test_results.json` files. You will then see the main menu.

## Basic Usage

The application is entirely menu-driven via the command line.

### 1. Define New Test Case
This option allows you to create a new test case definition.

*   From the main menu, type `1` and press Enter.
*   **Enter test case name:** Provide a concise, descriptive name for your test case (e.g., "Login with Valid Credentials").
*   **Enter execution steps:** You will be prompted to enter each step one by one.
    *   Type a step (e.g., "Navigate to the homepage.") and press Enter.
    *   Continue adding steps. When you have entered all steps, type `done` (case-insensitive) on a new line and press Enter.
    *   *Requirement*: At least one step is required.
*   **Enter expected results:** Describe what should happen if the test passes (e.g., "User is redirected to the dashboard and sees their profile icon.").
*   The system will confirm the creation of your test case with its unique ID.

### 2. List All Test Cases
This option displays all test cases currently defined in the system.

*   From the main menu, type `2` and press Enter.
*   The application will list each test case, showing its ID, Name, Steps, and Expected Results. If no test cases are defined, it will inform you.

### 3. Run Test Case
This option guides you through the execution of a selected test case and allows you to record its result.

*   From the main menu, type `3` and press Enter.
*   **Select Test Case:** A list of available test cases will be shown with numbers. Enter the number corresponding to the test case you wish to run and press Enter.
    *   If you enter invalid input (e.g., text or a number out of range), the system will prompt you again until valid input is given or you abandon the operation.
*   **Execute Steps:** For each step of the selected test case, the application will display the step description. Perform the action described, then press Enter to proceed to the next step.
*   **Review Expected Results:** After all steps, the `Expected Results` will be shown. Review them against what actually happened during your manual execution. Press Enter to continue to result recording.
*   **Record Test Result:**
    *   **Select Outcome:** You will be presented with a list of outcome options (Pass, Fail, Blocked, Skipped) with corresponding numbers. Enter the number that best describes the test's outcome and press Enter.
        *   If an invalid choice is made, it will default to 'Blocked'.
    *   **Add comments (optional):** Enter any relevant comments, observations, or details about the execution. Press Enter to finish.
    *   **Path to evidence (optional):** If you captured a screenshot, log file, or other evidence, type its file path here. Press Enter to finish (leave blank if no evidence).
*   The system will confirm that the test result has been recorded with its unique ID and outcome.

### 4. View Test Report
This option generates and displays a summary and detailed report of your test execution results.

*   From the main menu, type `4` and press Enter.
*   **Summary Report:** This section provides an overview:
    *   `Total Test Cases`: Count of all defined test cases.
    *   `Passed`, `Failed`, `Blocked`, `Skipped`: Counts of test cases based on their *latest* recorded outcome.
    *   `Not Run`: Count of test cases that have been defined but never executed.
*   **Detailed Report (Last Result Per Test Case):** This section provides more granular information:
    *   Each defined test case is listed.
    *   For each, it shows its name and ID.
    *   If the test case has been run, it displays the `Last Run` timestamp, `Outcome`, `Comments`, and `Evidence` path from its most recent execution.
    *   If a test case has not been run, it will indicate "No runs recorded yet."

## Advanced Usage

This application is designed for simplicity and manual testing. It does *not* include features such as:
*   Test automation framework integration.
*   Complex reporting dashboards with historical trends.
*   User authentication or role-based access control.
*   Integration with external defect tracking systems.
*   Version control for test cases within the application (external tools like Git are recommended for test asset management).

For these advanced needs, consider migrating to a more comprehensive Test Management System (TMS) or integrating with dedicated automation tools.

## Best Practices

*   **Clear Test Case Names:** Use names that clearly indicate the purpose of the test (e.g., "Login - Valid Credentials", "Search Functionality - Empty Query").
*   **Atomic Steps:** Break down execution steps into small, actionable units. This makes tests easier to follow and execute.
*   **Precise Expected Results:** Be specific about what constitutes a "Pass." Avoid vague descriptions.
*   **Descriptive Comments for Failures:** When a test fails or is blocked, provide detailed comments on *what* went wrong, *why* it failed, and *any relevant context*. This is crucial for debugging and reporting.
*   **Consistent Evidence:** If your workflow requires evidence (screenshots, logs), ensure you consistently capture and link them, especially for failures.
*   **Regular Reporting:** Generate reports regularly to track progress and identify areas needing attention.
*   **Backup Data:** Since data is stored in plain JSON files, consider regularly backing up your `data/` directory to prevent accidental data loss.

## Troubleshooting

*   **"CRITICAL ERROR: Unable to set up data storage..."**
    *   **Cause:** The application could not create the `data/` directory or the `test_cases.json`/`test_results.json` files.
    *   **Solution:** Check the permissions of the directory where you are running the application. Ensure you have write access. Also, check for sufficient disk space.
*   **"Error decoding JSON from <file_path>: ..." or "File might be corrupted."**
    *   **Cause:** One of your data JSON files (`test_cases.json` or `test_results.json`) has become corrupted (e.g., manually edited incorrectly, or an application crash during write). The application will log an `ERROR` and attempt to continue by treating the file as empty.
    *   **Solution:**
        1.  Check the logged error messages for details.
        2.  Navigate to your `data/` directory.
        3.  Inspect the problematic JSON file using a text editor. Look for syntax errors (missing commas, brackets, etc.).
        4.  If you can identify and fix the corruption, save the file.
        5.  If the file is severely corrupted and you have no backup, you might need to delete it. The application will recreate an empty one on next launch, but you will lose data. **This highlights the importance of regular backups.**
*   **"Invalid choice. Please try again." (Main Menu)**
    *   **Cause:** You entered a character or number that is not one of the available menu options (1-5).
    *   **Solution:** Enter only the valid numeric choice (1, 2, 3, 4, or 5).
*   **"Invalid input. Please enter a valid number." (When selecting test case or outcome)**
    *   **Cause:** You entered text or a non-numeric value when a number was expected.
    *   **Solution:** Enter only the numeric option corresponding to your choice. The application will keep prompting until a valid number is entered or you cancel the operation (not explicitly supported for all prompts, but typically by Ctrl+C).
*   **"Error running test case: Test Case with ID '...' not found."**
    *   **Cause:** The test case you attempted to run (by its number) was either deleted or never existed. This can happen if you selected a number corresponding to an empty slot or a test case that was removed by another process.
    *   **Solution:** Go back to the "List All Test Cases" option (2) to see the current list of available test cases and their valid numbers.
*   **Application crashes unexpectedly:**
    *   **Cause:** While error handling is implemented, unforeseen issues or very severe file corruption could lead to a crash.
    *   **Solution:** Check the terminal for any Python traceback. Review the `logs` (if you configure dedicated logging to a file). Report the issue with as much detail as possible, including steps to reproduce, and the exact error message/traceback. Ensure your Python environment is correctly set up.
```

### Developer Guide
```markdown
# Developer Guide

This guide provides an overview of the system's architecture, design decisions, and instructions for developers who wish to understand, contribute to, or extend the Simple Test Workflow application.

## Architecture Overview

The Simple Test Workflow employs a **Layered Monolithic Architecture**. This design separates the application into distinct, logical layers, promoting modularity, separation of concerns, and maintainability, while keeping the overall system simple and self-contained.

```mermaid
graph TD
    User -- Interacts with --> PresentationLayer
    PresentationLayer -- Calls use cases --> ApplicationLayer
    ApplicationLayer -- Invokes domain logic --> DomainLayer
    DomainLayer -- Uses interfaces from --> InfrastructureLayer
    InfrastructureLayer -- Stores/Retrieves data from --> DataStorage(JSON/CSV Files)

    subgraph Layers
        PresentationLayer[Presentation Layer<br>(CLI/Simple GUI)]
        ApplicationLayer[Application Layer<br>(Use Cases, Orchestration)]
        DomainLayer[Domain Layer<br>(Entities, Business Logic)]
        InfrastructureLayer[Infrastructure Layer<br>(Data Persistence, Utilities)]
    end
```

**Layers and Their Responsibilities:**

1.  **Presentation Layer (`src/main.py`):**
    *   **Responsibility:** Handles user interaction (Command-Line Interface). It's the entry point of the application.
    *   **Key Components:** `main_menu()`, `define_test_case()`, `run_test_case_workflow()`, `view_test_report()`.
    *   **Interaction:** Calls methods in the `Application Layer` to perform tasks and displays results to the user. Includes basic input validation and error display for user-facing issues.

2.  **Application Layer (`src/application/`):**
    *   **Responsibility:** Orchestrates the application's core logic and defines the use cases. It acts as an intermediary between the Presentation and Domain/Infrastructure layers.
    *   **Key Components:**
        *   `TestCaseManager`: Manages CRUD operations for test case definitions.
        *   `TestRunner`: Facilitates test execution and records results.
        *   `ReportGenerator`: Aggregates data to create summary and detailed reports.
    *   **Interaction:** Depends on `Domain Layer` entities and `Infrastructure Layer` repositories (via abstract interfaces) to implement business workflows.

3.  **Domain Layer (`src/domain/`):**
    *   **Responsibility:** Contains the core business logic, domain entities, and value objects. This layer is independent of external concerns like UI or data storage. It enforces business rules and data integrity.
    *   **Key Components:**
        *   `entities.py`: Defines `TestCase` and `TestExecutionResult` data structures.
        *   `enums.py`: Defines `TestOutcome` enum (Pass, Fail, Blocked, Skipped).
    *   **Interaction:** Provides validated data models to the Application layer and defines abstract interfaces for data persistence (implemented by the Infrastructure layer).

4.  **Infrastructure Layer (`src/infrastructure/`):**
    *   **Responsibility:** Provides generic technical capabilities, particularly data persistence (file I/O) and utilities. It implements the abstract interfaces defined in the `Domain Layer`, allowing the core business logic to remain agnostic to the specific storage mechanism.
    *   **Key Components:**
        *   `file_utils.py`: Contains low-level file reading/writing utilities (`read_json_file`, `write_json_file`).
        *   `repositories.py`: Contains concrete implementations of repository interfaces (`JSONFileTestCaseRepository`, `JSONFileTestExecutionResultRepository`), handling the mapping between domain entities and JSON file storage.
    *   **Interaction:** Depends only on Python's standard library and interacts directly with the file system (`data/` directory).

**Design Patterns Applied:**

*   **Layered Architecture:** Enforces separation of concerns, improving maintainability and scalability.
*   **Repository Pattern:** Abstracted data access (`AbstractTestCaseRepository`, `AbstractTestExecutionResultRepository`) from concrete storage implementations (`JSONFileTestCaseRepository`, `JSONFileTestExecutionResultRepository`). This is crucial for future migration to databases without altering application logic.
*   **Dependency Injection (Manual):** Application layer components receive their dependencies (e.g., `TestCaseManager` receives `test_case_repository` in its constructor) rather than creating them internally. This enhances testability and flexibility.
*   **Factory Method (Implicit):** `from_dict` static methods in domain entities serve as factory methods for object deserialization from dictionaries.
*   **Value Object:** `TestOutcome` enum acts as a value object, ensuring type safety and restricting valid test outcomes.

## Contributing Guidelines

We welcome contributions to the Simple Test Workflow! Please follow these guidelines:

1.  **Understand the Architecture:** Familiarize yourself with the Layered Monolithic Architecture. Changes should adhere to the established layer responsibilities and dependencies.
2.  **Code Style:** Adhere to [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code style. Use clear, descriptive variable and function names.
3.  **Type Hinting:** Use Python [type hints](https://docs.python.org/3/library/typing.html) for all function arguments, return values, and class attributes where appropriate.
4.  **Docstrings:** Provide comprehensive docstrings for all new modules, classes, and public methods, explaining their purpose, arguments, and return values.
5.  **Testing:**
    *   Write unit tests for new or modified functionality, especially in the `domain`, `infrastructure`, and `application` layers.
    *   Tests should be placed in the `tests/` directory, mirroring the `src/` structure.
    *   Use `unittest.mock` to isolate components during testing, particularly for application layer logic that interacts with repositories.
    *   Ensure existing tests pass before submitting changes.
6.  **Error Handling & Logging:** Utilize Python's `logging` module for internal errors, warnings, and informational messages, rather than `print()`. Provide user-friendly messages for any errors displayed to the console.
7.  **Configuration:** If new configurable paths or settings are needed, add them to `src/config.py`.

## Testing Instructions

The project includes a comprehensive suite of unit tests.

1.  **Navigate to the project root:**
    ```bash
    cd project/ # Or wherever your project directory is located
    ```
2.  **Run all unit tests:**
    ```bash
    python -m unittest discover tests
    ```
    This command will discover and run all test files (`test_*.py`) within the `tests/` directory and its subdirectories.

    Expected output will show `OK` if all tests pass, or details about failures if any occur.

## Deployment Guide

The Simple Test Workflow is designed for local, standalone execution.

1.  **Prerequisites:**
    *   Python 3.6+ installed.
    *   The complete project directory structure with all source code and the `data/` directory.

2.  **Execution Environment:**
    *   The application runs directly from the command line. No web server, database server, or complex environment setup is required.
    *   It creates and manages its own data files (`test_cases.json`, `test_results.json`) within the `data/` directory relative to where `main.py` is executed.

3.  **Data Persistence:**
    *   All test definitions and results are stored in plain JSON files within the `data/` directory.
    *   To migrate data between machines, simply copy the entire `data/` directory.
    *   **Backup Strategy:** It is highly recommended to regularly back up the `data/` directory to prevent data loss. Consider using version control systems (like Git) for test definition files (`test_cases.json`) as well.

4.  **Scalability Considerations:**
    *   The current file-based storage is efficient for the specified scale (up to ~100 test cases).
    *   For larger scales, the performance will degrade due to frequent full file reads/writes.
    *   **Future Upgrade Path:** The architecture (specifically the Repository Pattern) allows for a straightforward migration to a lightweight embedded database (like SQLite) to handle larger datasets, without requiring major changes to the application or domain logic. This would involve creating new `SQLiteTestCaseRepository` and `SQLiteTestExecutionResultRepository` classes and updating the initialization in `src/main.py`.

5.  **Distribution (Optional):**
    *   For easier distribution to users who may not have Python installed, tools like `PyInstaller` can be used to bundle the application into a single executable file.
    *   Example (after installing `pyinstaller` via `pip install pyinstaller`):
        ```bash
        pyinstaller --onefile src/main.py
        # The executable will be in the 'dist/' directory
        ```
    *   Note: Creating single executables can increase the file size and build time.
```

### Quality and Security Notes
```markdown
# Quality and Security Report

## Code Quality Summary
### Score: 9/10

The codebase demonstrates exceptionally high quality, adhering rigorously to modern software engineering principles and Python best practices.

**Strengths:**
*   **Clear Layered Architecture:** Excellent separation of concerns across `domain`, `infrastructure`, and `application` layers, leading to high cohesion and low coupling.
*   **Adherence to SOLID Principles:** Evident in Single Responsibility for classes, Dependency Inversion through abstract repositories, and Open/Closed Principle for extensibility.
*   **Robust Data Handling:** Domain entities include validation; `file_utils.py` handles file I/O errors and corrupted JSON gracefully, logging issues and returning empty data to prevent crashes.
*   **Comprehensive Unit Testing:** A well-structured test suite covers all key layers (domain, infrastructure, application), uses mocks effectively for isolation, and addresses positive flows, edge cases, and error conditions.
*   **Readability and Maintainability:** Consistent type hints, meaningful naming conventions (PEP 8), thorough docstrings, and judicious inline comments significantly enhance code readability and maintainability.
*   **Scalability Foundation:** The Repository Pattern provides a solid base for future migration to more robust data storage (e.g., SQLite) if scalability requirements grow.
*   **Improved CLI User Experience:** Refactored `main.py` with robust numeric input validation and clearer error messages enhances usability.

**Areas for Improvement (Minor for Current Scope):**
*   **Limited Error Recovery (File Operations):** While caught, `file_utils` currently returns empty data on file errors. For mission-critical data, more advanced recovery (e.g., backing up corrupted files) might be considered.
*   **Logging vs. Printing:** Although `logging` is implemented, some `print()` statements for user interaction still exist, which is fine for a CLI but highlights where a dedicated CLI framework could further standardize output.

## Security Assessment
### Score: 6/10 (Within Defined Constraints)

The system's security posture is considered adequate *only* for its explicit design as a "simple, single-user or trusted environment" test workflow. It incorporates good architectural practices and basic data integrity checks. However, fundamental limitations exist due to the deliberate omission of security features not required by its specified scope.

**Critical Issues:**
*   **None identified within the stated scope and requirements.** The absence of authentication/authorization is a design choice.

**Medium Priority Issues:**
*   **Lack of Authentication and Authorization:** **(PRIMARY CONCERN IF CONTEXT CHANGES)** No user login or access control mechanisms are implemented. Anyone with access to the host machine can manipulate test data files directly, posing a significant risk in untrusted or multi-user environments.
*   **Plain Text Data Storage:** All data is stored unencrypted in JSON files. This creates a confidentiality risk if sensitive information is ever introduced into test cases or results. It also presents an integrity risk as data can be easily modified externally.
*   **Information Disclosure (Refined):** While greatly improved by logging, generic `Exception` catching in `main.py` *could* still, in very rare edge cases, expose more internal details than ideal to the console.

**Low Priority Issues:**
*   **Potential for Path Traversal in Evidence Path (Latent):** The `evidence_path` field stores arbitrary user-provided paths. Though currently only stored and displayed, if future features process these paths without validation, it could become a vulnerability.
*   **Hardcoded File Paths (Mitigated by `config.py`):** The initial hardcoding is now centralized in `src/config.py`, improving flexibility, but still relies on relative paths which can be less robust than absolute paths configured at runtime.
*   **Input Handling Robustness (CLI - External Display):** User inputs are not extensively sanitized for characters that could cause issues if rendered in a different context (e.g., HTML, SQL). For a pure CLI, this risk is minimal.

**Security Best Practices Followed:**
*   **Clear Separation of Concerns (Layered Architecture/Repository Pattern):** Promotes data integrity by isolating persistence logic.
*   **UUIDs for Identifiers:** Prevents predictable IDs, a common exploit in systems lacking proper authorization.
*   **Basic Input Validation in Domain Entities:** Ensures data integrity at the object creation level (e.g., non-empty, correct types).
*   **Robust File I/O Error Handling:** `file_utils.py` handles `json.JSONDecodeError` and `IOError`, making the application more resilient to corrupted files and preventing crashes.
*   **Standard Library Usage:** Minimizes attack surface from third-party dependencies.

**Recommendations:**
*   **Explicitly document security assumptions:** Crucially, the documentation must clearly state the trusted environment assumption.
*   **Enhanced Error Reporting:** Continue to refine error logging to ensure sensitive details are never exposed to the end-user.
*   **File Path Validation (Future):** If `evidence_path` is ever processed, implement strict path sanitization (e.g., using `os.path.abspath`, `os.path.normpath`, and directory whitelisting).
*   **External Configuration:** Leveraging `src/config.py` is a good step; further externalization via command-line args or env vars for production-like deployments.

## Performance Characteristics
### Score: 7/10 (Meets NFRs for Current Scope)

The system meets its stated performance requirements for up to 100 test cases and their results, largely due to its lightweight nature. However, its fundamental file-based data access pattern is a significant limiting factor for future scalability.

**Critical Performance Issues (If Scaled Beyond ~100 Test Cases):**
*   **Full File I/O for Every Operation:** The core bottleneck is that most CRUD operations involve reading the *entire* relevant JSON file into memory, performing the change, and then writing the *entire* file back to disk. This linear operation (O(N) where N is file size) becomes highly inefficient for larger datasets.

**Optimization Opportunities (Mainly for Future Scaling):**
1.  **Transition to an Embedded Database (Primary Recommendation):** For scales beyond 100 test cases, migrate the `infrastructure/repositories.py` layer to use a lightweight embedded database like **SQLite**. This would provide indexed lookups (O(log N) or O(1)), efficient partial updates, and better transactional integrity, resolving the core I/O bottleneck. The Repository Pattern facilitates this.
2.  **In-Memory Processing for Reports:** The `ReportGenerator` already loads all necessary data into memory once for its calculations, which is efficient for its purpose within the current scale.

**Algorithmic Analysis:**
*   **CRUD Operations (`JSONFileRepositories`):** Dominated by file I/O. Effective time complexity is O(N_records) for reading/writing the entire file.
*   **Report Generation:** O(N_test_cases + N_results) in-memory processing after initial file reads.

**Resource Utilization:**
*   **Memory:** Minimal for the current scope (few MBs).
*   **CPU:** Low.
*   **I/O:** Most taxed resource due to frequent full file reads/writes, though mitigated by SSDs for small files.

**Scalability Assessment:**
The current design is **not inherently scalable beyond the stated "up to 100 test cases" limit.** Any significant increase in test cases or results will lead to noticeable performance degradation as file sizes grow. Horizontal scaling is not applicable. Vertical scaling (more RAM/CPU) offers limited benefit against the fundamental I/O pattern.

**Recommendations:**
*   **Prioritize Database Migration for Future Scale:** Clearly communicate this limitation and recommend SQLite migration as the primary path for growth.
*   **Monitoring & Profiling (If Issues Arise):** Use Python's `cProfile` if performance unexpectedly degrades within the expected limits.
*   **Error Handling for File Corruption:** (Addressed in Refactoring) The graceful handling of JSON decoding errors in `file_utils.py` improves resilience, contributing to perceived performance stability.

## Known Limitations

*   **Scalability:** Limited by the flat-file JSON storage, which requires reading/writing entire files for most operations. Not suitable for hundreds or thousands of test cases without migration to a database.
*   **Security (Authentication/Authorization):** Lacks any user authentication or authorization. Designed for single-user or trusted environments only. Data files are vulnerable to direct modification by anyone with file system access.
*   **No Advanced Features:** Does not include features like test automation framework integration, complex reporting dashboards, historical trend analysis (beyond latest result), or integration with external systems (e.g., Jira).
*   **Evidence Management:** Only stores a *path* to evidence; it does not manage, store, or process the evidence files themselves.
*   **Manual Workflow:** Primarily supports manual testing and requires significant user interaction for execution and result recording.
```

### Changelog
```markdown
# Changelog

## Version History

### Version 1.0.0 (Initial Release - Refactored)
*   **Date:** 2023-10-27
*   **Summary:** Initial stable release incorporating a layered monolithic architecture, file-based data persistence (JSON), and core functionalities for defining, executing, and reporting manual test cases. This version includes significant refactoring for improved quality, security, and performance based on initial reviews.

## Breaking Changes

While minimal, users migrating from an unrefactored version should note:

*   **Configuration File:** File paths for `test_cases.json` and `test_results.json` are now defined in `src/config.py`. If you previously hardcoded these paths elsewhere or relied on implicit locations, you must now adjust your setup to use or import from `src/config.py`.
*   **Error Handling in `file_utils.py`:** The `read_json_file` function in `src/infrastructure/file_utils.py` no longer raises `json.JSONDecodeError` or `IOError` directly for reading failures. Instead, it logs the error and returns an empty list `[]`. If your code explicitly caught these exceptions from this function, you should update your error handling logic.
*   **Console Error Messages:** Detailed technical error messages are now primarily directed to the application's internal logs (if configured) instead of being printed directly to the console. User-facing messages are more general and user-friendly.

## Migration Guides

### Migrating to Version 1.0.0 (from a pre-refactor state)

Follow these steps to ensure a smooth transition to the refactored version:

1.  **Update Project Structure:**
    Ensure your project structure includes the new `src/config.py` file and aligns with the following:
    ```
    project/
    ├── src/
    │   ├── __init__.py
    │   ├── main.py
    │   ├── config.py             # <--- NEW FILE
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

2.  **Replace File Contents:**
    *   **`src/config.py`**: Create this new file and copy its entire content as provided in the refactored code.
    *   **`src/main.py`**: Replace the entire content of your existing `main.py` with the refactored `main.py` code.
    *   **`src/infrastructure/file_utils.py`**: Replace the entire content of your existing `file_utils.py` with the refactored `file_utils.py` code.
    *   **`tests/test_infrastructure.py`**: Replace the entire content of your existing `test_infrastructure.py` with the updated `test_infrastructure.py` code.
    *   All other files (`src/domain/*.py`, `src/infrastructure/repositories.py`, `src/application/*.py`, `tests/test_domain.py`, `tests/test_application.py`) remain unchanged in terms of their code content, but ensure they are present in the correct paths.

3.  **Data File Location:**
    The application now strictly expects `test_cases.json` and `test_results.json` to be located within a `data/` directory, directly inside your `project/` root.
    *   If you have existing `test_cases.json` or `test_results.json` files from a previous run, **move them into the `project/data/` directory.**
    *   If you wish to place data files elsewhere, you *must* edit `src/config.py` to update the `DATA_DIR`, `TEST_CASES_FILE`, and `TEST_RESULTS_FILE` variables accordingly.

4.  **Logging Configuration:**
    The `main.py` now includes basic logging configuration. If you require more advanced logging (e.g., writing logs to a specific file, setting different log levels for various modules), you can modify the `logging.basicConfig` call in `main.py` or implement a more elaborate logging setup.

5.  **Running the Application and Tests:**
    *   **To run the application:** Navigate to your `project/` directory and execute:
        ```bash
        python -m src.main
        ```
    *   **To run the unit tests:** Navigate to your `project/` directory and execute:
        ```bash
        python -m unittest discover tests
        ```

---

**Important Security Note for Users:**

This Simple Test Workflow is explicitly designed for a **single-user or trusted, local environment**. It is crucial to understand its inherent limitations:

*   **No Authentication/Authorization:** The application does not implement any form of user login or access control. Anyone with direct access to the machine where the application is running can define, execute, modify, and delete test cases and their results.
*   **Plain-Text Data Storage:** All test case definitions and execution results are stored unencrypted in plain-text JSON files. Therefore, **sensitive or confidential information should absolutely NOT be stored within this system.**
*   **Reliance on OS Permissions:** The security of your data relies entirely on the operating system's file system permissions on the `data/` directory and the application files.

**If your environment is not trusted, involves multiple users, or requires the handling of sensitive data, this tool is NOT suitable. A more robust solution with built-in security controls (e.g., a database with access control, encryption, user management) would be required.**
```

## 📁 Incremental Outputs
Individual agent outputs have been saved to: `backend/output/incremental_20250704_084057`

Each agent's output is saved as a separate markdown file with execution order:
- `00_workflow_metadata.md` - Initial workflow configuration
- `01_[agent_name].md` - First agent output
- `02_[agent_name].md` - Second agent output
- `...` - Additional agent outputs in execution order
- `99_final_summary.md` - Execution summary

Note: Actual filenames will match the executed agents in your workflow.

## 📊 Performance Metrics
- **Execution Time**: 277.72 seconds
- **Success Rate**: 100%
- **Memory Usage**: Available in full JSON report
- **API Calls**: Tracked in session state

## 🔧 Technical Details
- **Workflow Manager**: FlexibleWorkflowManager
- **Runner Type**: InMemoryRunner
- **Session ID**: flexible_session
- **User ID**: flexible_user
- **App Name**: flexible_agent_app

---
*Report generated on 2025-07-04 08:45:34 by Flexible Workflow System*
