# Overview

This is a Web application built with Flask that manages student hours, staff oversight, and achievement recognition. The application tracks input hours for students, allows staff to log and confirm hours, and provides a leaderboard system with milestone-based accolades (10, 25, 50 hours). It follows the Model-View-Controller (MVC) architectural pattern and provides a REST API with JWT-based authentication.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Web Framework & Structure

**Problem**: Need a scalable, maintainable structure for a Flask web application
**Solution**: Model-View-Controller (MVC) pattern implementation
- **Models** (`App/models/`): Database entities using SQLAlchemy ORM with polymorphic inheritance (User → Student, Staff)
- **Views** (`App/views/`): Blueprint-based route handlers separated by domain (auth, student, staff, user)
- **Controllers** (`App/controllers/`): Business logic layer that mediates between models and views

**Rationale**: MVC separation ensures single responsibility principle, makes testing easier, and allows components to evolve independently.

## Authentication & Authorization

**Problem**: Secure user authentication with role-based access control
**Solution**: Flask-JWT-Extended with cookie and header-based tokens
- JWT tokens store user ID in the 'sub' claim
- Polymorphic user types (student vs staff) enable role-based authorization
- Token stored in both cookies and headers for flexibility
- Custom user loader retrieves User objects from JWT identity

**Design Choice**: Password hashing via Werkzeug's `generate_password_hash`/`check_password_hash` for security.

## Data Layer

**Problem**: Persistent storage of user data, hours tracking, and accolades
**Solution**: Flask-SQLAlchemy with polymorphic inheritance pattern
- **User** base model with polymorphic identity discriminator
- **Student** extends User with hours tracking and accolade relationships
- **Staff** extends User with administrative capabilities
- **Accolade** separate entity linked to students via foreign key

**Alternatives Considered**: 
- Single table with nullable fields → Rejected due to poor normalization
- Separate tables without inheritance → Rejected due to code duplication

**Trade-offs**: Polymorphic inheritance adds complexity but provides clean code reuse and type safety.

## Database Schema Design

- **Users/Students/Staff**: Single-table inheritance with discriminator column (`user_type`)
- **Accolades**: One-to-many relationship with cascade delete to maintain referential integrity
- **Hours Tracking**: Integer field on Student model with automatic accolade milestone detection

## API Design

**Problem**: Provide programmatic access to application features
**Solution**: RESTful API with JSON responses
- Consistent endpoint naming (`/api/students`, `/api/staff`)
- HTTP verb semantics (GET for retrieval, POST for actions)
- JWT required on protected endpoints via `@jwt_required()` decorator
- Error responses with appropriate HTTP status codes

**Endpoints Structure**:
- Authentication: `/api/login`
- Student operations: `/api/students/*`, `/api/students/me`
- Staff operations: `/api/staff/*`, `/api/staff/log-hours`
- Leaderboard: `/api/students/leaderboard`

## Testing Strategy

**Problem**: Ensure code quality and prevent regressions
**Solution**: Multi-layer testing approach
- **Unit Tests**: Test individual model methods and business logic in isolation
- **Integration Tests**: Test controller functions with database interactions
- **API Tests**: Test complete request/response cycles via pytest fixtures
- Test database isolation using SQLite in-memory or separate test.db

**Implementation**: pytest framework with fixtures for database setup/teardown per test module.

## CLI Commands

**Problem**: Database initialization and administrative tasks
**Solution**: Flask CLI with Click framework
- `flask init`: Database schema creation and sample data seeding
- Custom command groups for students and staff management
- Promotes infrastructure-as-code for deployment

## Frontend Architecture

**Problem**: Serve both traditional web pages and SPA-style interfaces
**Solution**: Hybrid approach
- Jinja2 templates for server-side rendering (`/users`)
- Static HTML + JavaScript for client-side rendering (`/static/users`)
- Materialize CSS framework for responsive UI

**Rationale**: Provides flexibility for different use cases while maintaining consistent styling.

## Production Deployment

**Problem**: Serve application in production environment
**Solution**: Gunicorn WSGI server with gevent workers
- Async worker type for handling concurrent requests
- Configurable worker count (currently 4)
- Bind to 0.0.0.0:8080 for container/cloud compatibility

# External Dependencies

## Core Framework
- **Flask 2.3.3**: Web application framework
- **Werkzeug ≥3.0.0**: WSGI utilities and password hashing

## Database & ORM
- **Flask-SQLAlchemy 3.1.1**: SQLAlchemy integration for database models
- **Flask-Migrate 3.1.0**: Alembic-based database migrations
- **psycopg2-binary 2.9.9**: PostgreSQL adapter (production database support)

## Authentication & Security
- **Flask-JWT-Extended 4.4.4**: JWT token management for API authentication
- Werkzeug password hashing (built-in to Flask)

## Additional Flask Extensions
- **Flask-Cors 3.0.10**: Cross-Origin Resource Sharing support
- **Flask-Admin 1.6.1**: Administrative interface generation
- **Flask-Reuploaded 1.2.0**: File upload handling

## Production Server
- **gunicorn 20.1.0**: Production WSGI HTTP server
- **gevent 22.10.2**: Asynchronous networking library for Gunicorn workers

## Testing
- **pytest 7.0.1**: Testing framework for unit and integration tests
- **Mocha 10.0.0**: JavaScript testing framework (for E2E tests)
- **Chai 4.3.6**: Assertion library for JavaScript tests
- **Puppeteer-core 17.1.3**: Headless browser automation for E2E testing

## Utilities
- **click 8.1.3**: CLI creation framework (used by Flask)
- **python-dotenv 1.0.1**: Environment variable management
- **rich 13.4.2**: Terminal output formatting

## Development Database
- **SQLite**: Default development database (via `sqlite:///temp-database.db`)
- Configuration allows switching to PostgreSQL in production via environment variables

## Third-Party Services
- **Postman**: API documentation and testing (collection included in repository)
- No external API integrations currently implemented