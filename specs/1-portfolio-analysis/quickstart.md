# Quickstart: Portfolio Analysis & Asset Projection

**Date**: 2025-11-14
**Feature**: Portfolio Analysis & Asset Projection (1-portfolio-analysis)
**Purpose**: Setup, running, and basic usage guide

## Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- SQLite 3 (built-in on macOS/Linux; Windows installer included with Python)
- Git

## Project Structure

```
stock_app/
├── backend/          # Django REST API
├── frontend/         # Next.js TypeScript application
└── specs/            # Documentation (this feature is 1-portfolio-analysis)
```

## Setup

### Backend (Django)

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

**Windows (Git Bash / WSL / bash.exe) notes**:

- Create and activate virtualenv (recommended name: `.venv`):
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate   # bash.exe / Git Bash on Windows
   # or for WSL / Linux: source .venv/bin/activate
   ```

- Install dependencies using the dev requirements (includes linters/tests):
   ```bash
   pip install -r backend/requirements-dev.txt
   ```

4. **Create environment file** (`.env`):
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   DATABASE_URL=sqlite:///db.sqlite3
   ALLOWED_HOSTS=localhost,127.0.0.1
   ```

5. **Run database migrations**:
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional, for admin access):
   ```bash
   python manage.py createsuperuser
   ```

7. **Run development server**:
   ```bash
   python manage.py runserver 8000
   ```

   Server available at: `http://localhost:8000/api/v1/`

### Frontend (Next.js)

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Create environment file** (`.env.local`):
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
   ```

4. **Run development server**:
   ```bash
   npm run dev
   ```

   Application available at: `http://localhost:3000`

## Basic Usage Flow

### 1. Login / Register

- Visit `http://localhost:3000` → Navigate to Login page
- Create account or login with test credentials
- Session maintained via Django session cookie

#### Quick verification using curl (API-level)

After running the backend server, verify login via `curl` from a bash shell:

1) Create a test user (if you didn't run `createsuperuser`, use admin or create via Django shell):

```bash
# Create a superuser interactively (recommended for testing)
cd backend/src
python manage.py createsuperuser

# OR create a test user via django shell (example):
python manage.py shell -c "from django.contrib.auth.models import User; User.objects.create_user('testuser','test@example.com','testpass')"
```

2) Login with curl and capture session cookie:

```bash
curl -i -c cookies.txt -H "Content-Type: application/json" \
   -d '{"username":"testuser","password":"testpass"}' \
   http://127.0.0.1:8000/api/v1/auth/login/

# The response will include a Set-Cookie header stored in cookies.txt
```

3) Access a protected endpoint using the stored cookie (example: health endpoint is open, but use holdings once implemented):

```bash
curl -b cookies.txt http://127.0.0.1:8000/api/v1/holdings
```

If the cookie is valid, the API will return your holdings (or an empty list). If you receive `401` or `403`, verify the login step and cookie handling.

### 2. Input Investment Holdings (P1)

- Navigate to "Input Holdings" page
- Click "Add Holding"
- Fill form:
  - Account Type: NISA or General Account
  - Asset Class: Stock, Mutual Fund, Cryptocurrency, etc.
  - Asset Region: Domestic Stocks, International Stocks, etc.
  - Asset Identifier: Symbol or code (e.g., "1234" for Toyota, "VANGUARD_VTI")
  - Asset Name: Human-readable name
  - Current Amount: JPY amount (can be 0)
  - Purchase Date: Optional
- Click "Save" → Holding appears in list

**Test Data**:
- Domestic Stock: 1000000 JPY (Toyota, 1234)
- International Stock: 500000 JPY (VANGUARD VTI, VANGUARD_VTI)
- Cryptocurrency: 250000 JPY (Bitcoin, BTC)
- Domestic Bond: 300000 JPY (JGB, JGB10Y)

### 3. View Current Portfolio (P2)

- Navigate to "Portfolio" tab
- Pie chart displays holdings grouped by asset region
- Hover over slices to see tooltips:
  - Asset region name
  - JPY amount
  - Percentage of portfolio
  - Number of holdings
- Visual distinction between NISA and General Account holdings

**Expected Pie Chart** (with test data above):
- Domestic Stocks: 45%
- International Stocks: 22.5%
- Cryptocurrency: 11.3%
- Domestic Bonds: 13.5%
- (Percentages depend on precise amounts)

### 4. Define Recurring Investment Plans (P2)

- Navigate to "Investment Plans" tab
- Click "Add Plan"
- Fill form:
  - Target Account Type: NISA or General
  - Target Asset Class & Region: Choose destination
  - Frequency:
    - **Monthly**: Amount invested every month (start/end dates)
    - **Daily**: Amount invested every business day (if enabled)
    - **Bonus Month**: Amount only in specified months (e.g., June, December)
  - Amount: JPY per period
  - Start Date: Begin investing on this date
  - End Date: Optional; null means ongoing
  - Bonus Months: If frequency is BONUS_MONTH, select months (1-12)
- Click "Save" → Plan appears in list

**Test Plan**:
- Monthly ¥50,000 to Domestic Stocks (NISA)
- Monthly ¥30,000 to International Stocks (General Account)
- Bonus Month ¥200,000 in June and December to Cryptocurrency (General Account)

### 5. Project Future Portfolio (P3)

- Navigate to "Projections" tab
- Enter parameters:
  - **Projection Years**: 5, 10, 15, 20, or custom (1-50)
  - **Annual Return Rate**: 4.0 for 4%, or -2.0 for market downturn
  - (Optional) Toggle "Include Year-by-Year Breakdown"
- Click "Calculate"
- View results:
  - **Projected Total Value**: Starting balance + contributions + compound interest
  - **Pie Chart**: Projected composition by asset region
  - **Breakdown Table**:
    - Starting Balance: Current portfolio total
    - Accumulated Contributions: Sum of all recurring investments
    - Interest Gains: Compound interest earned
    - Total Projected Value: Sum of above
  - **Comparison View**: Current vs. Projected side-by-side

**Example Calculation** (with test data + test plan + 10 years @ 4% return):
```
Starting Balance: 2,050,000 JPY
Monthly Contributions: 80,000 JPY → 10 years = 9,600,000 JPY
Bonus Contributions (June + Dec): 400,000 JPY/year × 10 = 4,000,000 JPY
Total Contributions: 13,600,000 JPY

Projected Total: ~24,500,000 JPY (starting + contributions + compound interest @ 4%)
Interest Gains: ~8,850,000 JPY

Composition (same region proportions as today):
- Domestic Stocks: 45%
- International Stocks: 22.5%
- Cryptocurrency: 11.3%
- Domestic Bonds: 13.5%
```

### 6. Edit / Delete Holdings or Plans

- Click "Edit" on any holding or plan to modify
- Click "Delete" to remove (confirmation required)
- Changes reflect immediately in portfolio and future projections

## API Endpoints Reference

Base URL: `http://localhost:8000/api/v1`

### Authentication
- `POST /auth/login` - Login with username/password
- `POST /auth/logout` - Logout current session

### Holdings
- `GET /holdings` - List all holdings (paginated, 50 per page)
- `POST /holdings` - Create new holding
- `PUT /holdings/{id}` - Update holding
- `DELETE /holdings/{id}` - Delete holding

### Portfolio
- `GET /portfolio/summary` - Get portfolio composition and totals

### Recurring Plans
- `GET /recurring-plans` - List all recurring investment plans
- `POST /recurring-plans` - Create new plan
- `PUT /recurring-plans/{id}` - Update plan
- `DELETE /recurring-plans/{id}` - Delete plan

### Projections
- `POST /projections` - Calculate future portfolio projection

**Full OpenAPI spec**: See `contracts/api.openapi.json`

## Development Workflow

### Running Tests

**Backend**:
```bash
cd backend
pytest tests/unit/              # Unit tests
pytest tests/integration/       # Integration tests
pytest tests/contract/          # API contract tests
pytest --cov=src tests/         # With coverage report
```

**Frontend**:
```bash
cd frontend
npm run test                    # Jest unit tests
npm run test:integration       # Integration tests
npm run test:coverage          # With coverage
```

### Type Checking

**Backend**:
```bash
cd backend
mypy --strict src/
```

**Frontend**:
```bash
cd frontend
npm run typecheck              # tsc --noEmit
```

### Linting & Formatting

**Backend**:
```bash
cd backend
ruff check src/               # Linting
black src/                    # Format
```

**Frontend**:
```bash
cd frontend
npm run lint                  # ESLint
npm run format               # Prettier
```

### Pre-Commit Hooks

Enable automatic checking before commits:

**Backend**:
```bash
cd backend
pip install pre-commit
pre-commit install
```

**Frontend**:
```bash
cd frontend
npm install husky
npx husky install
```

## Deployment

### Backend

For production, replace SQLite with PostgreSQL:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost/stock_app_db

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic

# Deploy to WSGI server (Heroku, DigitalOcean, etc.)
# See Django deployment docs
```

### Frontend

Deploy to Vercel (recommended for Next.js):

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

Or build for self-hosted:

```bash
npm run build
npm run start
```

## Troubleshooting

### Backend Issues

**Database locked error**:
- SQLite has limitations with concurrent access; use PostgreSQL for production
- For development, restart Django server: `python manage.py runserver`

**Import errors**:
- Ensure virtual environment is activated: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

**Type checking fails**:
- Update mypy: `pip install --upgrade mypy`
- Check function signatures match type hints

### Frontend Issues

**API connection errors**:
- Verify backend is running on `http://localhost:8000`
- Check `NEXT_PUBLIC_API_URL` in `.env.local`
- Check browser console for CORS errors

**TypeScript errors**:
- Clear Next.js cache: `rm -rf .next`
- Rebuild: `npm run dev`

**Chart not rendering**:
- Verify portfolio has holdings before accessing Portfolio tab
- Check browser console for Recharts errors

## Next Steps

1. **Run tests** to ensure setup is working:
   ```bash
   cd backend && pytest
   cd ../frontend && npm run test
   ```

2. **Add test data** using the API or UI

3. **Explore projections** with different return rates and time horizons

4. **Check code quality**:
   ```bash
   cd backend && mypy --strict src/
   cd ../frontend && npm run typecheck
   ```

5. **Proceed to implementation** following task breakdown in `/speckit.tasks`

## Additional Resources

- Django Documentation: https://docs.djangoproject.com/
- Next.js Documentation: https://nextjs.org/docs
- Django REST Framework: https://www.django-rest-framework.org/
- Recharts Documentation: https://recharts.org/
- Project Constitution: `.specify/memory/constitution.md`
- Feature Specification: `specs/1-portfolio-analysis/spec.md`
- Data Model: `specs/1-portfolio-analysis/data-model.md`
- API Schema: `specs/1-portfolio-analysis/contracts/api.openapi.json`
