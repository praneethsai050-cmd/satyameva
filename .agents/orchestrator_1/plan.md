# Plan: Satyameva Bulk Issuance Feature

## Phase 0: Survey & Exploration (Current)
- Spawn 3 parallel Explorers:
  1. `explorer_survey_backend`: Investigate existing routes, document issuance mechanisms, email notifications, blockchain anchoring, and models.
  2. `explorer_survey_frontend`: Investigate issuer portal UI, templates, student dashboard, public verify page, static assets, and template downloading.
  3. `explorer_survey_testing`: Investigate existing test harness, database setup, dependencies, running test commands, and edge cases.
- Synthesize findings into `PROJECT.md` with Feature Inventory, Milestones, and Interface Contracts.

## Phase 1: Dual Track Execution
### Track A: E2E Testing Track
- Spawn E2E Testing Orchestrator / Test Writers to build comprehensive opaque-box test suite:
  - Tier 1: Feature Coverage (CSV validation, UI endpoints, template download, text-only doc creation)
  - Tier 2: Boundary & Corner Cases (empty CSV, malformed CSV, partial missing fields, invalid roll numbers, huge CSV, unicode)
  - Tier 3: Cross-Feature (Multiple batches, mixed doc types, blockchain validation, dashboard + verify page rendering)
  - Tier 4: Real-World Scenarios (Batch issuance of degrees/transcripts, verification flow, error recovery)
- Publish `TEST_READY.md`.

### Track B: Implementation Track
- Milestone 1: CSV Template & Schema Validation (Backend validation logic, sample CSV endpoint)
- Milestone 2: Text-Only Credential Issuance Engine (DB record creation, blockchain block mining, notification triggers without physical file requirement)
- Milestone 3: Issuer UI & Student/Public Display Support (Issuer Bulk Upload UI, handling text-only credentials on student dashboard & public verify page)

## Phase 2: Final Milestone & Hardening
- Pass 100% of E2E tests (Tiers 1-4).
- Tier 5 Adversarial Coverage Hardening with Challengers.
- Forensic Integrity Audit.
- Final human reporting.
