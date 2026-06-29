---
plan name: final-evaluation-prep
plan description: Prepare final project evaluation
plan status: active
---

## Idea
Prepare MelodyBox for the final software design evaluation (June 29 - July 3). This plan covers: (1) Implementing missing business rules from the SRS (password policy, playlist/song limits, unique playlist names), (2) Improving test coverage on low-coverage modules (redis_helper, youtube, fft_service), (3) Creating presentation slides, (4) Verifying all rubric criteria are met, (5) Final demo preparation and team defense rehearsal.

The plan addresses 10 evaluation criteria with specific actions for each. The current state is strong but has critical gaps: 6 business rules from the SRS are not implemented, several modules have coverage below 70%, and presentation materials need to be created.

## Implementation
- 1. Implement missing business rules (RN-003 password policy, RN-005 50 playlist limit, RN-006 500 songs/playlist, RN-008a 100MB file limit, RN-015 unique playlist names) in services layer with schemas validation
- 2. Add tests for all new business rules and improve coverage on low-coverage modules (redis_helper, youtube_service, youtube routes, fft_service, dependencies) to reach >70%
- 3. Verify CI pipeline passes all jobs (lint, format, tests, coverage >=70%, SonarQube) and fix any failures
- 4. Create evaluation presentation slides covering: architecture patterns, CI pipeline, auth system, testing strategy, SonarQube integration, demo walkthrough, and technical justifications
- 5. Prepare demo script covering all functional requirements: auth flow, upload/stream, playlist CRUD, favorites, search, admin panel, FFT analysis
- 6. Run full SonarQube analysis locally, resolve any critical/blocker issues, verify coverage.xml is generated correctly
- 7. Final review: verify all rubric criteria with check-list, rehearse defense justifications for each technical decision
- 8. Create AGENTS.md with verification commands for the team to run before submission

## Required Specs
<!-- SPECS_START -->
- clean-code-spec
- final-eval-spec
<!-- SPECS_END -->