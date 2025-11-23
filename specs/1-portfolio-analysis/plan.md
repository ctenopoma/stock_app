# Implementation Plan: Portfolio Analysis & Asset Projection

**Branch**: `1-portfolio-analysis` | **Date**: 2025-11-14 | **Spec**: [./spec.md](./spec.md)
**Input**: Feature specification from `/specs/1-portfolio-analysis/spec.md`

## Summary

Portfolio Analysis & Asset Projection enables users to track investment holdings across multiple account types (NISA, general accounts) and asset classes, visualize current portfolio allocation via pie charts, define recurring investment plans, and calculate future asset values with compound interest. The application prioritizes data input (P1) → visualization (P2) → projections (P3).

## Technical Context

**Language/Version**:
- Frontend: Node.js 18+ with TypeScript 5.x
- Backend: Python 3.11+

**Primary Dependencies**:
- Frontend: Next.js 14.x, React 18.x, TypeScript, Chart.js or Recharts for pie charts
- Backend: Django 4.2+, Django REST Framework 3.14+, drf-spectacular for OpenAPI docs

**Storage**: SQLite for local persistence (development); PostgreSQL for production migration path. Schema includes User, InvestmentHolding, RecurringInvestmentPlan tables.

**Testing**:
- Frontend: Jest, React Testing Library (unit + integration tests)
- Backend: pytest with pytest-django (unit + integration + contract tests)

**Target Platform**: Web application (responsive SPA) accessible via browser; works on desktop and mobile browsers

**Project Type**: Web application with frontend (Next.js/TypeScript) + backend (Django/Python) separation

**Performance Goals**:
- Portfolio pie chart renders in <2 seconds (SC-002)
- Projection calculation completes in <1 second for 5-10 year horizons (SC-004)
- Page load time <3 seconds on standard broadband
- API response time <500ms for all endpoints

**Constraints**:
- Local database persistence required (SQLite minimum)
- Must comply with project constitution: Type-Safe Development, API-First Architecture, Test-First Development
- No external payment or financial APIs (calculations only; no real market data integration)

**Scale/Scope**:
- Single-user or session-authenticated MVP (no multi-user tenant management)
- 4 user stories, 20 functional requirements, 8 success criteria
- ~50-100 screens/components for MVP

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Principle I: Type-Safe Development
✅ **PASS**
- Frontend will use TypeScript with strict mode, type annotations for all functions, no `any` types
- Backend will use Python with type hints (def func(x: Type) -> ReturnType:) and mypy strict mode
- Pre-commit hooks will enforce: tsc, eslint, mypy, black, ruff

### Principle II: API-First Architecture
✅ **PASS**
- All portfolio operations (holdings, projections, calculations) exposed via Django REST Framework endpoints
- OpenAPI/Swagger documentation auto-generated via drf-spectacular
- Next.js frontend communicates exclusively via REST API, no direct DB access
- API versioning: `/api/v1/` endpoints for holdings, plans, projections

### Principle III: Test-First Development
✅ **PASS**
- Frontend: Jest + React Testing Library for holdings form, portfolio chart, projection UI
- Backend: pytest for portfolio calculations, projection engine, data validation
- 80% coverage minimum required for all modules

### Principle IV: Code Standards Enforcement
✅ **PASS**
- Frontend: TypeScript strict, ESLint + @typescript-eslint, Prettier, pre-commit hooks
- Backend: mypy strict, flake8/ruff, black, pre-commit hooks
- All PRs must pass type checking and linting before review

### Principle V: Separation of Concerns
✅ **PASS**
- Backend (Django): models, REST endpoints, business logic (portfolio aggregation, projection calculation)
- Frontend (Next.js): components, forms, pie chart visualization, API service layer
- Independent deployment and testing paths

**Conclusion**: No violations. All five core principles satisfied.

## Project Structure

### Documentation (this feature)

```
specs/1-portfolio-analysis/
├── plan.md              # This file
├── research.md          # Phase 0 output (TBD)
├── data-model.md        # Phase 1 output (TBD)
├── quickstart.md        # Phase 1 output (TBD)
├── contracts/           # Phase 1 output (TBD)
│   ├── holdings.openapi.json
│   ├── recurring-plans.openapi.json
│   ├── projections.openapi.json
│   └── auth.openapi.json
└── checklists/
    └── requirements.md   # Quality checklist (completed)
```

### Source Code (repository root)

```
backend/
├── src/
│   ├── accounts/             # User authentication & account management
│   │   ├── models.py
│   │   ├── views.py
│   │   └── serializers.py
│   ├── portfolio/            # Core portfolio features
│   │   ├── models.py         # InvestmentHolding, RecurringInvestmentPlan
│   │   ├── views.py          # REST endpoints
│   │   ├── serializers.py    # API serialization
│   │   ├── services.py       # Portfolio aggregation, projection calculations
│   │   └── validators.py     # Data validation
│   ├── api/                  # API routing & middleware
│   │   └── urls.py           # /api/v1/ endpoints
│   ├── settings.py           # Django settings
│   └── wsgi.py
├── tests/
│   ├── unit/                 # Unit tests for models, serializers, validators
│   ├── integration/          # Integration tests for endpoints
│   └── contract/             # API contract tests
├── manage.py
└── requirements.txt

frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx         # Dashboard / Landing
│   │   ├── portfolio.tsx     # Current portfolio view
│   │   ├── input.tsx         # Holdings input form
│   │   ├── plans.tsx         # Recurring investment plans
│   │   └── projections.tsx   # Future projections
│   ├── components/
│   │   ├── HoldingsForm.tsx      # Input form for holdings
│   │   ├── PortfolioChart.tsx    # Pie chart visualization
│   │   ├── ProjectionForm.tsx    # Projection input
│   │   ├── ProjectionChart.tsx   # Projected portfolio pie chart
│   │   └── ComparisonView.tsx    # Current vs projected side-by-side
│   ├── services/
│   │   └── api.ts            # Typed API client (holdings, plans, projections)
│   ├── types/
│   │   ├── investment.ts     # InvestmentHolding, RecurringInvestmentPlan types
│   │   ├── portfolio.ts      # Portfolio, Projection types
│   │   └── common.ts         # Enums (AccountType, AssetClass, AssetRegion)
│   └── hooks/
│       ├── usePortfolio.ts   # Fetch and manage holdings
│       ├── usePlans.ts       # Fetch and manage recurring plans
│       └── useProjection.ts  # Calculate and fetch projections
├── tests/
│   ├── unit/                 # Jest tests for components, hooks, utilities
│   └── integration/          # Integration tests for API interactions
├── tsconfig.json             # TypeScript strict mode
├── next.config.js
└── package.json
```

**Structure Decision**: Web application with clear frontend/backend separation. Django provides REST API and business logic; Next.js provides responsive UI. Both layers use TypeScript/Python with strict type checking. Shared types defined in both backends and transmitted via OpenAPI schema.

## Complexity Tracking

No violations of constitution; no special complexity justifications needed. Standard web application architecture with straightforward data models (holdings, plans, projections).

## Phase 0: Outline & Research (TBD)

Research tasks to complete before Phase 1:
- Best practices for compound interest calculation in financial applications
- Portfolio visualization libraries comparison (Chart.js vs Recharts)
- Django authentication best practices for single-user MVP
- Performance optimization for large portfolio datasets (1000+ holdings)

## Phase 1: Design & Contracts (TBD)

Deliverables:
- `research.md` with findings from Phase 0
- `data-model.md` with entity definitions, relationships, validation rules
- `contracts/` with OpenAPI schemas for all endpoints
- `quickstart.md` with setup, running, and basic usage instructions

## Phase 2: Implementation (TBD)

Output by `/speckit.tasks` command:
- Task breakdown by user story (P1 → P2 → P3)
- Dependency graph (foundational tasks → story-specific tasks)
- Testing requirements (test-first approach)
