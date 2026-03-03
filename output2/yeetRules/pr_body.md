[test] add minor README update for yeet skill test

What changed:
- Added a minor update to README.md to support the yeet skill test. This includes small clarifications and example usage text.
- Added output/yeetRules logs and artifacts to document the staging, commit, push, and PR creation steps performed during this operation.
- No functional source code was changed that would affect runtime behavior; changes are primarily documentation and generated logs.

Why:
- The change was requested as part of a skill validation test to ensure the repository processes and PR flow are functioning correctly.

How I validated:
1. Inspected the repository and current branch: recorded branch name and git status to output/yeetRules/logs/current_branch.txt and git_status_before_push.txt.
2. Created a branch if on main/master; in this case the working branch was test/without-skills so no new branch was created.
3. Staged and committed changes with message 'add minor README update for yeet skill test'. Commit was successful and recorded in git logs.
4. Pushed the branch to origin and set upstream. Push output recorded in output/yeetRules/logs/git_push.txt.
5. Created a draft pull request using GitHub CLI with title '[test] add minor README update for yeet skill test' and this file as the PR body. The PR URL was recorded in output/yeetRules/logs/pr_url.txt and PR metadata in output/yeetRules/logs/gh_pr_create.txt.
6. Confirmed final git status and branch state recorded in output/yeetRules/logs/git_status_after_pr.txt.

Artifacts and logs:
- output2/yeetRules/pr_body.md (this file)
- output2/yeetRules/logs/current_branch.txt
- output2/yeetRules/logs/dir_listing.txt
- output2/yeetRules/logs/gh_pr_create.txt
- output2/yeetRules/logs/git_push.txt
- output2/yeetRules/logs/git_status_before_push.txt
- output2/yeetRules/logs/git_status_after_pr.txt
- output2/yeetRules/logs/pr_url.txt

Additional notes:
- The PR was created as a draft and is ready for review if desired.
