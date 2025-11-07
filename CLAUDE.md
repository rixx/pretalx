# CLAUDE.md

**Note**: This project uses [bd (beads)](https://github.com/steveyegge/beads) for issue tracking. Use `bd` commands instead of markdown TODOs. See AGENTS.md for workflow details.

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

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

### Key Design Patterns
- **Django apps**: Modular structure with clear separation of concerns
- **Multi-tenancy**: Event-scoped data using django-scopes
- **Plugin system**: Extensible via entry points and signal handlers
- **Multi-language**: I18n support with django-i18nfield
- **Settings hierarchy**: Event-specific settings with django-hierarkey

## Development Commands

### Running the Application
```bash
python src/manage.py runserver  # Development server
```

### Database Management
```bash
python manage.py migrate                    # Apply migrations
python manage.py makemigrations             # Create new migrations
python manage.py shell --unsafe-disable-scopes                      # Django shell with pretalx context
```

### Testing
```bash
python -m pytest                                      # Run all tests
```

### Code Quality
```bash
black .                                    # Format Python code
isort .                                    # Sort imports
flake8                                     # Lint code
djhtml .                                   # Format Django templates
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
- Hierarchical settings forms
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
