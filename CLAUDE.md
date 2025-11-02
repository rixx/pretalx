# CLAUDE.md

## Project Overview

pretalx is a conference planning tool built with Django that handles call for participation (CfP), submission review, scheduling, and conference management. It's a production-ready application used by many events worldwide.

## Architecture

### Core Applications
- **event/**: Event management and organization models
- **submission/**: CfP, submissions, reviews, questions, and tracks
- **schedule/**: Room management, time slots, and scheduling
- **person/**: User profiles, speaker information, and authentication
- **agenda/**: Public-facing schedule and agenda views
- **orga/**: Organizer interface and management views
- **cfp/**: Call for participation flow and forms
- **api/**: REST API using Django REST Framework
- **mail/**: Email templates and queuing system
- **common/**: Shared utilities, forms, mixins, and base functionality

## Development Commands

### Setup

```bash
uv sync --all-extras
```

### Running the Application
```bash
uv run python src/manage.py runserver  # Development server
```

### Database Management
```bash
uv run python manage.py migrate                    # Apply migrations
uv run python manage.py makemigrations             # Create new migrations
uv run python manage.py shell --unsafe-disable-scopes                      # Django shell with pretalx context
```

### Testing
```bash
uv run python -m pytest                                      # Run all tests
```

### Code Quality
```bash
uv run black .                                    # Format Python code
uv run isort .                                    # Sort imports
uv run flake8                                     # Lint code
uv run djhtml .                                   # Format Django templates
```

## Model Relationships

### Core Models
- **Event**: Top-level container for all conference data
- **Submission**: Talk/workshop submissions with speakers
- **User**: Authentication and speaker profiles
- **Schedule**: Time-based arrangement of accepted submissions
- **Room**: Physical/virtual spaces for sessions
- **Review**: Evaluation of submissions by reviewers

### Key Relationships
- Events contain multiple submissions, rooms, and schedules
- Submissions can have multiple speakers (many-to-many)
- Reviews are linked to submissions and users
- Schedules contain slots that reference submissions and rooms

## Common Patterns

### Form Handling
- Custom form mixins in `common/forms/`
- Multi-step form wizards for complex workflows

### API Design
- RESTful endpoints with DRF
- Event-scoped permissions
- Pagination and filtering support
- OpenAPI/Swagger documentation

### Template Structure
- Base templates in `templates/`
- Event-specific overrides supported

## Security Considerations

- CSRF protection enabled
- Content Security Policy (CSP) headers
- Event-scoped data access control
- Input sanitization with bleach
- File upload restrictions and validation

# Code style

Apart from using linters, please take care to make the code fit in with the project. Be sparing with comments.
JavaScript code should be modern – fat arrows, const instead of function, etc.

When building a new feature or fixing a bug that involves the backend, add a test showing the bug is fixed. If there is
an existing test covering similar ground, feel free to add assertions to it instead of writing a new test. New tests
should be standard pytest functional tests, and if you need to set up reusable data, put it as a fixture into the
conftest.py.
