# social-poster

An automated YouTube posting pipeline — a small cross-posting bot that runs
entirely in the cloud, no laptop or server required. Drop a video into a
folder, and it gets uploaded to YouTube on its own schedule.

## What it does

This project takes the manual work out of posting video content: instead of
remembering to log in and upload a file every day, you just drop videos into
a queue folder. A scheduled job checks in once a day, uploads the next video
in line, and files it away as done.

## How it works

The pipeline is built around two folders that act as a simple queue:

- **`to-postMH/`** — videos waiting to be posted
- **`postedMH/`** — videos that have already been posted

Every day, a [GitHub Actions](https://github.com/features/actions) workflow
wakes up on a schedule and:

1. Picks the **oldest** video sitting in `to-postMH/`
2. Generates a title, description, and tags automatically from the
   filename
3. Uploads it to YouTube via the **YouTube Data API v3**, authenticated
   with **Google OAuth2** (uploads are set to English and marked "not made
   for kids")
4. Moves the file into `postedMH/` once the upload succeeds, and commits
   that change back to the repo

Because it runs on GitHub's own infrastructure on a schedule, there's
nothing to keep running locally — the "cloud" part of the pipeline is the
GitHub Actions runner itself.

## Tech stack

- **Python** — posting logic and queue management
- **YouTube Data API v3** — video uploads
- **Google OAuth2** — authentication with YouTube
- **GitHub Actions** — scheduling and cloud execution

## Credentials & security

No credentials are ever committed to this repository. OAuth client
details and the authorization token are kept out of version control
(`.gitignore`) and are instead stored as encrypted
[GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets),
which the workflow reads at run time and discards once the job finishes.

## Verifying it's working

The easiest way to check on the pipeline is the **Actions** tab, which shows
the full run history — when each run happened, whether it succeeded, and
its logs:

https://github.com/amosndukwe-pht/social-poster/actions

A successful run will show a video moved from `to-postMH/` into
`postedMH/`, along with a link to the uploaded YouTube video in the run
logs. Runs can also be triggered manually from that same tab
(`Run workflow`) without waiting for the daily schedule.
