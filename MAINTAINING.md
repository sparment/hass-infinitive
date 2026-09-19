# Automatic compatibility checks

The **Home Assistant compatibility** workflow tests Infinitive with real Home
Assistant software and simulated thermostat responses. Tests cannot contact your
thermostat: network sockets are blocked. They never update your home installation.

## One-time activation

1. Merge the compatibility setup pull request into `master` after its checks pass.
2. Open the repository's **Actions** tab and select **Home Assistant compatibility**.
   If GitHub asks you to enable Actions, enable it for this repository.
3. Click **Run workflow**, choose `master`, and click the green **Run workflow**
   button. Wait for a green result.
4. In your personal [GitHub notification settings](https://github.com/settings/notifications),
   find **Actions**, enable email notifications, and choose failed workflows only
   if that option is available. Verify your GitHub email address is correct.

GitHub sends scheduled-run notifications to the user who last changed the cron
schedule, or re-enabled a disabled workflow. Repository ownership and watching
the repository alone do not guarantee delivery. If notifications go to the wrong
account, disable and re-enable this workflow while signed in as `sparment`, then
confirm your personal Actions notification settings.

## What runs automatically

| Check | Timing |
| --- | --- |
| Latest stable HA | Daily at 09:23 UTC, on pull requests, and on changes to `master` |
| Newer beta/prerelease HA | Same runs, only while a prerelease newer than stable exists |
| HA development branch | Sundays at 10:43 UTC |
| Hassfest metadata validation | Every workflow run |

The workflow resolves exact versions on every run, uses the Python version HA
requires, and saves test results and installed package versions for 14 days.
GitHub may delay scheduled runs. A missing beta job usually means no newer beta
is available; the version-selection log says so explicitly.

## When a check fails

Open the failed run linked in GitHub's notification. The red job identifies
whether it was stable, beta, development, or metadata validation. Copy its URL
into a Codex conversation and ask for diagnosis. A failure can indicate an HA
change, a dependency/download problem, or a test-harness change; it does not by
itself prove your thermostat is broken. Repeated failures can generate repeated
GitHub notifications; this initial setup does not deduplicate them.

## Avoid silent monitoring gaps

GitHub disables scheduled workflows in public repositories after 60 days without
repository activity. These checks do **not** prevent that. An independent monitor
should check the public Actions API weekly and alert when the last scheduled run
is more than 3 days old or the workflow is disabled. That monitor must run outside
this repository's scheduled Actions. Until it is configured, check the Actions
page periodically and re-enable the workflow if GitHub disables it.

## Scope and known follow-up work

The suite checks YAML setup, actual HA entity creation and service dispatch,
temperature readings, mode mapping, single/range setpoints, fans, hold presets,
on/off services, and recovery after a simulated transport exception. It is an
early-warning baseline, not a guarantee of every hardware scenario or compatibility
with every historical HA release.

The initial monitoring change leaves thermostat behavior unchanged. Follow-up
work should address numbered HVAC mode lookups, stale mode state when switching
modes and setting temperatures immediately, error visibility/availability, and
the old minimum HA version advertised in `hacs.json`. Older versions have not
been validated by this workflow; do not raise the minimum just to match the
latest successful test.

## Running locally (optional)

Use the Python version required by the HA version being tested, then:

```sh
python -m pip install homeassistant -r requirements-test.txt
python -c 'import json, subprocess, sys; deps=json.load(open("custom_components/infinitive/manifest.json"))["requirements"]; subprocess.check_call([sys.executable, "-m", "pip", "install", *deps])'
python -m pytest
```

Useful references:
- [GitHub Actions notifications](https://docs.github.com/en/actions/concepts/workflows-and-actions/notifications-for-workflow-runs)
- [Scheduled workflow limitations](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)
- [Home Assistant developer announcements](https://developers.home-assistant.io/blog/)
