# MATC EMS Scenario Viewer

A browsable viewer for the paramedic training scenarios in [`matc-ems/scenarios`](https://github.com/matc-ems/scenarios), made for reviewing them one by one. It shows each scenario's dispatch and scene, the patient and history, a map of the phases and how they connect, the monitor state and presentation in each phase, the expected actions with their protocol references, and a table comparing vitals across phases.

The viewer is one self-contained HTML page. A GitHub Action rebuilds it from the scenarios repo every night and publishes it to GitHub Pages. This repo holds only the viewer. The scenarios stay in their own repo, and this repo only reads them.

## Layout

```
src/template.html            the viewer page (markup, styles, script); data is filled in at build time
build.py                     reads every unified.json and writes dist/index.html (standard library only)
.github/workflows/build.yml  nightly build + deploy to GitHub Pages
```
<!--
 ## Setup (once)

1. Create a new repo (for example `matc-ems/scenario-viewer`) and push these files to `main`.
2. In the repo, open **Settings → Pages** and set **Source** to **GitHub Actions**.
3. Open the **Actions** tab, choose **Build and publish viewer**, and click **Run workflow**.
4. When it finishes, the viewer is live at `https://<owner>.github.io/<repo>/` (for example `https://matc-ems.github.io/scenario-viewer/`).

The scenarios repo must be public for the Action to read it without extra credentials. If it becomes private, add a token with read access as a secret and pass it to the second `actions/checkout` step as `token: ${{ secrets.SCENARIOS_TOKEN }}`.
-->

## When it updates

- **Nightly**, at 07:17 UTC.
- **On demand**: click **Run workflow** on the Actions tab after a round of scenario edits.
- **When the viewer changes**: any push to `main` in this repo.

The sidebar shows which scenarios commit the page was built from and when, so reviewers can tell how current it is.

### Optional: rebuild as soon as scenarios change

To update the viewer after every push to the scenarios repo, add this workflow **to the scenarios repo** as `.github/workflows/notify-viewer.yml`. It needs a secret named `VIEWER_DISPATCH_TOKEN` there: a fine-grained personal access token with **Contents: read and write** on the viewer repo.

```yaml
name: Notify viewer
on:
  push:
    branches: [main]
jobs:
  notify:
    runs-on: ubuntu-latest
    steps:
      - run: |
          curl -sS -X POST \
            -H "Authorization: Bearer ${{ secrets.VIEWER_DISPATCH_TOKEN }}" \
            -H "Accept: application/vnd.github+json" \
            https://api.github.com/repos/matc-ems/scenario-viewer/dispatches \
            -d '{"event_type":"scenarios-updated"}'
```
<!--
## Optional: links to the scenario players

If the scenarios repo is published on GitHub Pages, the viewer can link each scenario to its interactive player (`index.html`) and printable handout. In this repo, go to **Settings → Secrets and variables → Actions → Variables** and add a variable named `SCENARIOS_PAGES_URL` set to that site's address (for example `https://matc-ems.github.io/scenarios/`). Leave it unset to show only the GitHub links.

## Building locally

```sh
git clone https://github.com/matc-ems/scenarios.git ../scenarios
python3 build.py --scenarios ../scenarios
# open dist/index.html in a browser
```

Each scenario has its own link: add its ID after `#`, for example `…/scenario-viewer/#055-anterior-stemi` or `…/#R-T1-01`.

## Pointing at a different repo or branch

Change `SCENARIOS_REPO` and `SCENARIOS_BRANCH` at the top of `.github/workflows/build.yml`. For example, point it at a review branch to see edits before they are merged.
-->
