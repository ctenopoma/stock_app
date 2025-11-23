# Stock App - Portfolio Analysis & Projection Platform

A full-stack application for managing investment holdings, tracking recurring investment plans, and projecting future portfolio growth using compound interest calculations.

**Tech Stack**:
- **Backend**: Django 4.2+ with Django REST Framework 3.12+
- **Frontend**: Next.js 14 (React 18, TypeScript 5)
- **Database**: SQLite (development), PostgreSQL (production-ready)
- **Testing**: pytest (backend), Jest/Vitest (frontend)

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18.17.0+ (enforced via `.nvmrc`)
- Git

### Setup Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
python src/manage.py migrate
python src/manage.py runserver
```

### Setup Frontend

```bash
cd frontend
nvm use  # Load Node version from .nvmrc
npm install
npm run dev  # Start dev server on http://localhost:3000
```

### Run Tests

**Backend**:
```bash
cd backend
python -m pytest -v
```

**Frontend**:
```bash
cd frontend
npm run test
npm run lint
```

---

## Development Workflow

### Install Pre-commit Hooks (Recommended)

Before making commits, install pre-commit hooks to automatically check code quality:

```bash
# Install pre-commit framework
pip install pre-commit

# Install the git hook scripts
pre-commit install
```

Once installed, pre-commit will automatically run on every `git commit` to:
- **Format code**: Black (Python), Prettier (JS/TS/JSON/MD)
- **Lint code**: Ruff (Python), ESLint (TypeScript/JavaScript)
- **Fix whitespace**: trailing-whitespace, end-of-file-fixer

To manually run all checks:
```bash
pre-commit run --all-files
```

### Linting & Type Checking

**Backend**:
```bash
cd backend
black src/
ruff check src/ --fix
mypy src/  # Type checking
```

**Frontend**:
```bash
cd frontend
npm run lint  # ESLint
npm run format  # Prettier (if available)
```

---

## Project Structure

```
.
├── backend/                       # Django REST API
│   ├── src/
│   │   ├── config/               # Settings, URLs, WSGI
│   │   ├── portfolio/            # Core app (models, views, serializers)
│   │   ├── accounts/             # Auth (login, logout)
│   │   └── api/                  # API routing & OpenAPI schema
│   ├── tests/                    # Pytest tests (contract, integration, unit)
│   ├── requirements.txt           # Production dependencies
│   └── requirements-dev.txt       # Development dependencies
│
├── frontend/                      # Next.js application
│   ├── src/
│   │   ├── pages/                # Route pages (input, plans, portfolio, projections)
│   │   ├── components/           # Reusable React components
│   │   ├── services/             # API client (typed)
│   │   └── styles/               # CSS modules
│   ├── package.json              # Dependencies & scripts
│   └── tsconfig.json             # TypeScript configuration
│
├── specs/
│   └── 1-portfolio-analysis/     # Feature specification documents
│       ├── plan.md               # Technical architecture
│       ├── data-model.md         # Entity definitions
│       ├── spec.md               # User requirements
│       └── tasks.md              # Implementation tasks
│
├── .pre-commit-config.yaml        # Pre-commit hook configuration
├── .github/workflows/ci.yml       # GitHub Actions CI/CD pipeline
└── README.md                      # This file
```

---

## CI/CD Pipeline

GitHub Actions automatically:
1. **Runs on push** to `main`, `1-portfolio-analysis`, and feature branches
2. **Runs on pull requests** to `main`
3. **Executes tests** (backend pytest, frontend lint/build)
4. **Applies pre-commit checks** to all files
5. **Reports results** with detailed logs

View pipeline status in `.github/workflows/ci.yml`.

---

## API Documentation

Once backend is running, OpenAPI/Swagger documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI JSON**: http://localhost:8000/api/schema/

---

## Troubleshooting

### Node version mismatch
```bash
nvm install  # Install version from .nvmrc
nvm use
```

### Pre-commit hook fails
```bash
# View failing file
pre-commit run --all-files --show-diff-on-failure

# Fix Python code automatically
black src/
ruff check src/ --fix

# Fix JavaScript/TypeScript automatically
npx prettier --write "src/**/*.{ts,tsx,js,json,md}"
```

### Database issues
```bash
cd backend
rm src/db.sqlite3  # Delete old database
python src/manage.py migrate  # Re-apply migrations
```

---

## Contributing

1. Create a branch from the task ID (e.g., `T028-projection-service`)
2. Make changes and ensure pre-commit hooks pass
3. Write tests for new features
4. Run full test suite locally before pushing
5. Create pull request with clear description
6. CI pipeline validates automatically

---

## Feature Overview

### User Story 1: Input Holdings (MVP)
Create, read, update, and delete investment holdings across multiple account types and asset regions.

### User Story 2: Visualize Portfolio
View current portfolio composition by asset region with interactive pie charts and totals.

### User Story 3: Recurring Plans
Define recurring investment plans (daily/monthly/bonus months) for automatic contribution tracking.

### User Story 4: Project Growth
Calculate future portfolio value using compound interest formula with configurable return rates and projection periods.

---

## License

MIT
