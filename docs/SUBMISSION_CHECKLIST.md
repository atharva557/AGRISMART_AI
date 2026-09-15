# Submission readiness

## Implemented locally

- Saved-weight classifier with one-label CLI; detailed output is opt-in.
- Optional crop check, unusable-photo retake flow and uncertainty preserved through assistant guidance.
- Optional same-scan weather context retaining source/window and simulation status.
- Checkpoint-label audit and user-run independent evaluation export.
- Concise model report, historical evidence, originality draft and four-minute demo script.
- Clean archive installation verified with `npm ci`, frontend build, automated tests and one-label CLI inference.
- Report/notebook audit and judge-facing result card committed locally.

## Pending external/team inputs

| Item | Next action |
|---|---|
| Organizer labels/split | Obtain exact files; run `python -m model.submission_check --labels PATH`; resolve any mismatch explicitly. |
| Organizer baseline/bands | Record separately from the team's ResNet baseline. Not supplied yet. |
| Official held-out metrics | Let organizers evaluate the predict interface. Do not tune on their test or invent scores. |
| Current-checkpoint field evidence | Team to prepare a reviewed manifest and run `model.evaluate`; no new field accuracy is claimed. |
| Core source/license | Confirm exact distribution and kickoff split. Generic dataset names are insufficient. |
| Originality | Review `docs/ORIGINALITY.md`, add references and confirm authorship/timeframe. |
| Demo video | Record using `docs/JUDGE_DEMO.md`; add an accessible 3–5-minute video URL. |
| Intended judging hardware | Repeat the clean install and inference check on the actual presentation machine before the event. |
| Public repository state | Local changes are committed. Push or publish the submission branch only when the team is ready and repository visibility has been checked. |

Verify live weather and regional-language output before demonstrating them as operational. Offline tests verify mocked contracts, not provider availability or translation quality.
