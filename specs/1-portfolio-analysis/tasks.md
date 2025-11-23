# Tasks: Portfolio Analysis & Asset Projection

**Input**: Design docs in `specs/1-portfolio-analysis/` (plan.md, spec.md, data-model.md, contracts/)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directories `backend/` and `frontend/` per `plan.md` (repo root)
- [x] T002 Initialize backend Python project: create `backend/requirements.txt` and `backend/pyproject.toml` with Django, djangorestframework, drf-spectacular, pytest, mypy
- [x] T003 Initialize frontend Next.js TypeScript project: create `frontend/package.json`, `frontend/tsconfig.json` (Next.js + TypeScript + React)
- [x] T004 [P] Configure linting, formatting and pre-commit hooks: add `.pre-commit-config.yaml`, `frontend/.eslintrc.js`, `frontend/.prettierrc`, `backend/pyproject.toml` (black/ruff/mypy)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infra that MUST be complete before any user story implementation

- [x] T005 Setup Django project skeleton in `backend/src/` (manage.py, settings, wsgi)
- [x] T006 [P] Implement authentication using Django auth & session middleware in `backend/src/accounts/` (`models.py`, `views.py`, `serializers.py`)
- [x] T007 [P] Configure Django REST Framework and drf-spectacular in `backend/src/api/` (`urls.py`, `schema.py`, settings)`
- [x] T008 [P] Create base models for portfolio in `backend/src/portfolio/models.py`: `InvestmentHolding`, `RecurringInvestmentPlan`, `Projection`
- [x] T009 Create initial migrations and migrate DB (SQLite) using `backend/src/manage.py makemigrations` and `backend/src/manage.py migrate` (repo root/backed)
- [x] T010 [P] Add typed API client scaffolding in `frontend/src/services/api.ts` and generate/update OpenAPI usage config in `backend/src` for contract-driven development

**Checkpoint**: Foundational phase complete — user stories may start after these tasks finish

---

## Phase 3: User Story 1 - Input Current Investment Holdings (Priority: P1) 🎯 MVP

**Goal**: Allow users to create, read, update, delete investment holdings and persist them

**Independent Test**: Save and retrieve 5+ holdings across different account types and asset regions; data persists across sessions

### Tests (Test-First per constitution)

- [x] T011 [P] [US1] Add contract test for `POST /holdings` and `GET /holdings` in `backend/tests/contract/test_holdings_contract.py`
- [x] T012 [P] [US1] Add integration tests for holdings CRUD in `backend/tests/integration/test_holdings.py`

### Implementation

- [x] T013 [P] [US1] Create `InvestmentHolding` model in `backend/src/portfolio/models.py` (fields per `data-model.md`)
- [x] T014 [P] [US1] Create `InvestmentHoldingSerializer` in `backend/src/portfolio/serializers.py`
- [x] T015 [US1] Implement holdings views/endpoints in `backend/src/portfolio/views.py` and register routes in `backend/src/api/urls.py` (`/holdings`, `/holdings/{id}`)
- [x] T016 [US1] Implement frontend holdings input page `frontend/src/pages/input.tsx` and component `frontend/src/components/HoldingsForm.tsx`
- [x] T017 [US1] Implement typed API client methods for holdings in `frontend/src/services/api.ts` (create/get/update/delete)
- [x] T018 [US1] Add backend validation helpers in `backend/src/portfolio/validators.py` and wire into serializers
- [x] T019 [US1] Add frontend tests for holdings form in `frontend/tests/integration/test_holdings_form.test.tsx`

**Checkpoint**: US1 should be independently deployable and testable (holdings persisted + UI CRUD)

---

## Phase 4: User Story 2 - Visualize Current Portfolio (Priority: P2)

**Goal**: Provide pie-chart visualization of current portfolio by asset region and totals

**Independent Test**: Given 3+ holdings, portfolio summary endpoint returns composition and UI displays pie chart with percentages

- [x] T020 [P] [US2] Implement backend `GET /portfolio/summary` endpoint in `backend/src/portfolio/views.py` and serializer in `backend/src/portfolio/serializers.py`
- [x] T021 [US2] Implement `PortfolioChart` component in `frontend/src/components/PortfolioChart.tsx` (use Recharts or Chart.js) and wire into `frontend/src/pages/portfolio.tsx`
- [x] T022 [P] [US2] Add integration test for `GET /portfolio/summary` in `backend/tests/integration/test_portfolio_summary.py`
- [x] T023 [US2] Ensure UI shows totals in `frontend/src/pages/portfolio.tsx` and tooltips on hover (implement `frontend/src/components/Tooltip.tsx` if needed)

**Checkpoint**: US2 displays correct composition and totals with tooltips

---

## Phase 5: User Story 3 - Input Recurring Investment Plans (Priority: P2)

**Goal**: Allow users to create recurring investment plans (daily/monthly/bonus months) and persist them

**Independent Test**: Create 2+ plans, retrieve and edit them via API and UI

- [x] T024 [P] [US3] Create `RecurringInvestmentPlan` model in `backend/src/portfolio/models.py` (fields per `data-model.md`)
- [x] T025 [US3] Create serializer and views for `/recurring-plans` in `backend/src/portfolio/serializers.py` and `backend/src/portfolio/views.py`
- [x] T026 [P] [US3] Implement frontend plans page `frontend/src/pages/plans.tsx` and `frontend/src/components/PlansForm.tsx`
- [x] T027 [P] [US3] Add contract tests for `/recurring-plans` in `backend/tests/contract/test_recurring_plans_contract.py`

**Checkpoint**: US3 allows plan creation/edit/delete and persistence

---

## Phase 6: User Story 4 - Project Future Portfolio & Asset Growth (Priority: P3)

**Goal**: Calculate and present future portfolio values (compound interest) and projected composition

**Independent Test**: Given holdings + recurring plans + return rate, calculate projection and return a projection payload consistent with formula

 [x] T030 [US4] Implement frontend projection page `frontend/src/pages/projections.tsx` and components `frontend/src/components/ProjectionForm.tsx` and `frontend/src/components/ProjectionChart.tsx`
 [x] T031 [US4] Add integration test for projection calculations in `backend/tests/integration/test_projections.py` (year-by-year breakdown verification)

**Checkpoint**: US4 returns correct projected totals and charts

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Documentation, CI, performance and security improvements

- [x] T032 [P] Update `specs/1-portfolio-analysis/quickstart.md` and add developer README at `specs/1-portfolio-analysis/README.md`
- [x] T033 [P] Add CI pipeline and pre-commit hooks: `.github/workflows/ci.yml`, `.pre-commit-config.yaml` (run linters, type checks, tests)
- [x] T034 [P] Performance tuning and profiling tasks for portfolio aggregation in `backend/src/portfolio/services.py`
- [x] T035 [P] Run accessibility and responsive checks on frontend pages `frontend/src/pages/*.tsx`

---

## Dependencies & Execution Order

- Phase 1 (Setup) → Phase 2 (Foundational) → Phase 3+ (User Stories in priority order). User stories depend on Foundational tasks.
- Suggested execution: complete Setup + Foundational (T001–T010), then deliver US1 (T011–T019) as MVP. After US1 validated, implement US2 and US3 in parallel, then US4.

## Parallel Opportunities

- Tasks marked with `[P]` can be executed in parallel (different files/no hard dependency): T004, T006, T007, T008, T010, T011, T012, T013, T014, T020, T022, T024, T026, T027, T032, T033, T034, T035

## Counts & Summary

- Total tasks: 35
- Tasks per story:
  - Setup/Foundation: 10
  - US1: 9
  - US2: 4
  - US3: 4
  - US4: 4
  - Polish: 4

**MVP Recommendation**: Implement Phase 1 + Phase 2, then complete User Story 1 (holdings input + persistence + basic UI). Stop and validate before proceeding.

**Format Validation**: All tasks follow checklist format with Task IDs and file paths where applicable.
