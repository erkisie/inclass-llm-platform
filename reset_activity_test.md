## Reset Activity Verification Test

### Test Steps

1. Added score records for an activity.
2. Called /instructor/export-scores → scores returned.
3. Called /instructor/reset-activity.
4. Called /instructor/export-scores → empty result.
5. Called /student/get-activity → access blocked.

### Result

Passed.
