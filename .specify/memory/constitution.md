<!--
  SYNC IMPACT REPORT

  Version Change: 1.0.0 (New Constitution)
  Created: 2025-11-14

  Project: stock_app - A lightweight web application using Next.js (frontend) and Django (backend)

  Modified Principles:
  - I. Type-Safe Development (Explicit type definitions in all code)
  - II. API-First Architecture (Backend via Django REST, Frontend via Next.js)
  - III. Test-First Development (Unit and integration tests required)
  - IV. Code Standards Enforcement (Type hints, linting, formatting as mandatory)
  - V. Separation of Concerns (Frontend and backend separation)

  Added Sections:
  - Technology Stack (Next.js/Django specification)
  - Development Workflow (Type-checking and linting gates)

  Templates Updated:
  - ✅ spec-template.md (aligned with API-First architecture)
  - ✅ plan-template.md (technical context for Next.js/Django)
  - ✅ tasks-template.md (frontend/backend task organization)
-->

# stock_app Constitution

A lightweight web application built with Next.js (frontend) and Django (backend), emphasizing type safety, code standards, and clean architecture.

## Core Principles

### I. Type-Safe Development
All code MUST explicitly specify variable types. This is NON-NEGOTIABLE.

**Frontend (TypeScript/Next.js)**:
- All files MUST be `.ts` or `.tsx` (no `.js` files)
- All function parameters, return types, and variables MUST have explicit type annotations
- No `any` types allowed—use `unknown` only when absolutely necessary, with explicit narrowing
- Strict mode MUST be enabled in `tsconfig.json`

**Backend (Python/Django)**:
- All functions MUST have type hints for parameters and return values using `def func(x: Type) -> ReturnType:`
- All class attributes MUST have type annotations
- Use `typing` module for complex types (Optional, List, Dict, Callable, etc.)
- mypy MUST pass with `strict` mode enabled

**Rationale**: Explicit typing enables early error detection, improves code readability, supports IDE refactoring, and reduces runtime bugs in a lightweight application where every line matters.

### II. API-First Architecture
Frontend and backend communicate exclusively through well-defined REST APIs.

**Backend (Django)**:
- All business logic exposed via Django REST Framework endpoints
- Endpoints MUST include OpenAPI/Swagger documentation
- API versions MUST be managed (e.g., `/api/v1/`)
- All responses MUST follow consistent JSON schema

**Frontend (Next.js)**:
- All backend communication via typed API client (generated from OpenAPI or manual typed wrappers)
- No direct database access from frontend
- API calls MUST be abstracted into dedicated service layer in `src/services/`

**Rationale**: Clear API contracts reduce coupling, enable parallel development, and make the application easier to test, scale, and maintain.

### III. Test-First Development
Tests MUST be written before implementation. Red-Green-Refactor cycle is MANDATORY.

**Frontend**:
- Unit tests in `tests/unit/` using Jest + React Testing Library
- Integration tests in `tests/integration/` for API interactions
- Snapshot tests MUST NOT replace behavioral tests

**Backend**:
- Unit tests in `tests/unit/` using pytest
- Integration tests in `tests/integration/` for Django models and endpoints
- Contract tests in `tests/contract/` for API contracts

**Acceptance Criteria**: Minimum 80% line coverage; coverage reports MUST be reviewed in PRs.

**Rationale**: Test-first development ensures correctness from the start, prevents regressions, and serves as executable documentation.

### IV. Code Standards Enforcement
Type checking and code quality MUST be enforced at commit/PR stage, not runtime.

**Frontend**:
- TypeScript strict mode (required)
- ESLint with `@typescript-eslint` (required)
- Prettier formatting (required)
- Pre-commit hooks MUST run: `tsc`, `eslint`, `prettier`

**Backend**:
- mypy with `strict` mode (required)
- flake8 or ruff for linting (required)
- black for formatting (required)
- Pre-commit hooks MUST run: `mypy`, `black`, `ruff`

**Gate**: All PRs MUST pass type checking and linting before review.

**Rationale**: Automated enforcement prevents style discussions in reviews and catches type errors before code review, saving time.

### V. Separation of Concerns
Frontend and backend MUST be independently deployable and testable.

**Repository Structure**:
```
stock_app/
├── backend/
│   ├── src/
│   │   ├── models/       # Django models
│   │   ├── views/        # Django REST views
│   │   ├── serializers/  # REST serializers
│   │   ├── services/     # Business logic
│   │   └── middleware/   # Custom middleware
│   ├── tests/            # All tests
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/        # Next.js pages and routes
│   │   ├── components/   # React components
│   │   ├── services/     # API client and business logic
│   │   ├── types/        # TypeScript type definitions
│   │   └── hooks/        # Custom React hooks
│   ├── tests/            # All tests
│   └── package.json
└── docs/                 # Shared documentation
```

**Rationale**: Separation enables independent scaling, testing, and deployment of each layer.

## Technology Stack

**Frontend**: Next.js (with TypeScript) for server-side rendering and static optimization
**Backend**: Django with Django REST Framework for RESTful API
**Database**: (NEEDS CLARIFICATION: PostgreSQL, SQLite, or other?)
**Package Managers**: npm/yarn (frontend), pip (backend)
**Testing**: Jest + React Testing Library (frontend), pytest (backend)
**Type Checking**: TypeScript (frontend), mypy (backend)
**Linting/Formatting**: ESLint + Prettier (frontend), black + ruff (backend)

## Development Workflow

### Code Review Gates

All PRs MUST satisfy:

1. **Type Checking**: `tsc --noEmit` (frontend) and `mypy --strict .` (backend) MUST pass
2. **Linting**: ESLint (frontend) and ruff (backend) MUST report zero errors
3. **Formatting**: Code MUST be formatted by Prettier (frontend) and black (backend)
4. **Tests**: MUST pass; minimum 80% coverage
5. **Documentation**: New endpoints MUST include OpenAPI docs; new types MUST be documented

### Pre-Commit Enforcement

Each developer MUST configure pre-commit hooks to run:

```bash
# Frontend
npm run typecheck
npm run lint
npm run format

# Backend
mypy --strict .
ruff check .
black .
```

Branches MUST NOT be pushed without passing hooks.

### Deployment

- Frontend and backend can be deployed independently
- Frontend MUST be deployable to Vercel or similar Next.js host
- Backend MUST be deployable to any Python WSGI host (Heroku, DigitalOcean, etc.)
- Environment variables MUST be externalized; no secrets in code

## Governance

### Amendment Procedure

Amendments to this constitution MUST:

1. Be proposed with rationale and impact analysis
2. Updated template files MUST be listed (spec-template.md, plan-template.md, tasks-template.md)
3. Version MUST increment per semantic versioning:
   - MAJOR: Principle removals or breaking changes to development process
   - MINOR: New principles or significant expansions
   - PATCH: Clarifications, wording, or non-semantic refinements
4. All developers MUST review and approve
5. Document date and approval in this constitution

### Compliance Review

- Type checking gates MUST be enforced in CI/CD
- Linting failures MUST block PR merges
- Test coverage reports MUST be reviewed in every PR
- Quarterly audits of compliance (random sample of 10% of PRs)

### Related Documentation

Runtime development guidance is maintained in:
- **Frontend**: `frontend/docs/` and JSDoc comments in code
- **Backend**: `backend/docs/` and docstrings in code
- **API**: OpenAPI/Swagger specification (auto-generated from Django REST Framework)

---

**Version**: 1.0.0 | **Ratified**: 2025-11-14 | **Last Amended**: 2025-11-14
