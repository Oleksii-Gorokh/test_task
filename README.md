# Data Processing Platform

A simple Django-based web application for uploading, validating, and analyzing advertising data from Excel (.xls, .xlsx) and CSV files.

## Features
- **User Roles:** Regular users (upload data, view stats) and Admins (access admin panel, manage users/logs).
- **File Processing:** Upload `.xls`, `.xlsx`, or `.csv` files. The system automatically maps columns even if the order is changed.
- **Validation:** Handles incorrect files and throws validation errors when data does not match the expected template.
- **Analytics:** View aggregated impression (Impr) statistics grouped by year.

## Requirements
- Python 3.10+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Oleksii-Gorokh/test_task.git
   cd test_task
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database migrations:
   ```bash
   python manage.py migrate
   ```

## Running the Application

1. Start the Django development server:
   ```bash
   python manage.py runserver
   ```

2. Open your web browser and go to:
   ```
   http://127.0.0.1:8000/
   ```

*Note: You can register a new account directly from the login page. To test admin features, you can create a superuser or manually change a user's role to 'admin' in the database/Django admin.*

## Running Tests

The project uses `pytest` for testing. To run the test suite, simply execute:

```bash
pytest
```

To run tests with a verbose output, use:

```bash
pytest -v
```
