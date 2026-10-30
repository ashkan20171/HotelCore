# HotelCore
### Enterprise Hotel Management System

A modern desktop application designed to support hotel operations through structured workflows, security-focused functionality, and a maintainable software architecture.

**HotelCore** is a Python-based hotel management project built with PySide6 and SQLite. It demonstrates practical desktop software engineering, database integration, modular development, and attention to usability and operational reliability.

---

## Project Overview

HotelCore aims to provide a centralized environment for managing hotel-related operations through an intuitive desktop interface.

The project is developed with an emphasis on:

- Maintainable and modular code organization
- Database-driven application workflows
- Security-conscious access and administrative operations
- Consistent user experience
- Practical business software architecture
- Continuous testing and incremental improvements

## Technology Stack

| Area | Technology |
|---|---|
| Programming Language | Python |
| Desktop UI | PySide6 |
| Database | SQLite |
| Data Access | Python SQLite integration |
| Testing | Python unittest |
| Architecture | Modular desktop application |

## Key Engineering Areas

### Hotel Management Workflows
A desktop-oriented foundation for organizing hotel operations and related business processes.

### Security & Administration
Security-focused administrative functionality, including event reporting, filtering, event inspection, and CSV export.

### Database Integration
SQLite-based persistence with parameterized database queries and database integrity checks.

### User Experience
A desktop interface designed to make operational tasks accessible and straightforward.

### Testing & Reliability
Automated unit tests and incremental validation to help maintain application stability as the project evolves.

## Architecture & Development Approach

HotelCore is developed incrementally, with a focus on:

- Separation of application responsibilities
- Reusable business logic
- Clear database interactions
- Input validation and error handling
- Consistent development conventions
- Testable functionality

The project prioritizes practical engineering decisions over unnecessary architectural complexity.

## Project Structure

The codebase is organized into application modules, user interface components, database-related functionality, and automated tests.

```text
HotelCore/
├── main.py
├── tests/
├── README.md
└── application modules
```

The exact structure may evolve as the application grows.

## Quality Assurance

Automated tests are used to validate application functionality and reduce regressions.

The development workflow includes:

- Unit testing
- Python syntax validation
- Database integrity checks
- Regression testing
- Incremental feature validation

## Getting Started

### Prerequisites

- Python 3.10 or newer
- pip

### Installation

```bash
git clone https://github.com/ashkan20171/HotelCore.git
cd HotelCore
```

Create and activate a virtual environment:

**Windows**

```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
python main.py
```

> Note: The installation and execution instructions should be kept aligned with the current project configuration.

## Roadmap

- [x] Modular development and incremental improvements
- [x] Security event reporting enhancements
- [x] Event filtering and inspection
- [x] CSV reporting functionality
- [ ] Advanced reporting and pagination
- [ ] Expanded automated test coverage
- [ ] Further improvements to usability and maintainability
- [ ] Additional hotel operational workflows

## About the Developer

**Ashkan Motaei**  
Software Developer | Desktop Applications | Backend Development

I enjoy designing and developing practical software solutions, with an interest in maintainable architecture, database-driven applications, and business-oriented software engineering.

GitHub: [@ashkan20171](https://github.com/ashkan20171)

---

## License

Choose and add an appropriate open-source license before publishing this repository.

---

*Built with Python and PySide6, with a focus on practical software engineering and continuous improvement.*
