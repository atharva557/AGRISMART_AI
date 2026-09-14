# Submission readiness

## Implemented locally

- Saved-weight classifier with one-label CLI; detailed output is opt-in.
- Optional crop check, unusable-photo retake flow and uncertainty preserved through assistant guidance.
- Optional same-scan weather context retaining source/window and simulation status.
- Checkpoint-label audit and user-run independent evaluation export.
- Concise model report, historical evidence, originality draft and four-minute demo script.

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
| Clean installation | Test clone, install, build and inference on intended judging hardware. Existing-environment tests do not establish the ten-minute setup target. |
| Public repository state | Review local changes; no commit, push, publication or deployment is implied. |

Verify live weather and regional-language output before demonstrating them as operational. Offline tests verify mocked contracts, not provider availability or translation quality.
