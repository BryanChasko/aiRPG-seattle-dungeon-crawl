# Project Rename Plan: Seattle Strands Dungeon Crawl

Status: plan only. Nothing in this file renames the GitHub repository.
Run the rename-day steps in section 5, in order, in one sitting.

## 1. The new names

- Display name (page titles, repo About text, package description):
  Seattle Strands Dungeon Crawl: A Visual Lit aiRPG Workshop
- Coined format phrase: Visual Lit aiRPG. A Visual Lit aiRPG is a LitRPG
  you can see, run by one System AI, built one floor at a time with the
  Strands Agents SDK on Amazon Nova 2 Lite. Conflict is a dance-off.
  Nobody gets hurt. Use this exact phrase wherever the format is defined.
- Recommended repository slug: seattle-strands-dungeon-crawl
  (29 characters, all lowercase).
- Runner-up slug: seattle-strands-dungeon-crawl-workshop (39 characters).
- Rejected slug: seattle-strands-dungeon-crawl-visual-lit-airpg-workshop.
  It is about twice as long as the recommendation, and learners type the
  slug by hand on 50 `cd` lines in the workshop pages. The full display
  name belongs in titles and the About text, not in the typed path.
  The recommendation keeps `seattle` and `dungeon-crawl` from the old slug
  for recognition, names Strands (the SDK taught on every floor), and
  drops the mixed-case `aiRPG` spelling, which is an easy hand-typing
  error in clone folders and Pages paths.

New addresses after the rename:

- Repo: `https://github.com/BryanChasko/seattle-strands-dungeon-crawl`
- Play page: `https://bryanchasko.github.io/seattle-strands-dungeon-crawl/`

Exact proposed repo About text (set in section 5, step 4):

- Description: Seattle Strands Dungeon Crawl: A Visual Lit aiRPG Workshop. Learn the Strands Agents SDK by building the System AI of a LitRPG dungeon crawl under Seattle, one floor at a time.
- Homepage: `https://bryanchasko.github.io/seattle-strands-dungeon-crawl/`

Current About text, observed with `gh repo view` while writing this plan
(keep it here for rollback in section 7):

- Description: Powered by Strands SDK. Learn to build AI agents by running a LitRPG dungeon crawl under Seattle, one floor at a time.
- Homepage: `https://bryanchasko.github.io/aiRPG-seattle-dungeon-crawl/`

## 2. Evidence base

Measured on `origin/main` at e3c09614c0fbdc58f0cc3fe126ab877efcf94bb2
(the PR 18 art/readme-slots merge) after `git fetch origin`:

- `git grep -i 'aiRPG-seattle-dungeon-crawl' origin/main`:
  64 lines in 53 files. 58 lines are under `workshop/`, and 50 of the
  64 are `cd aiRPG-seattle-dungeon-crawl` lines.
- Only 4 lines carry this repo's own web addresses:
  `workshop/floor-0.md:95` (git clone), `workshop/floor-6.md:26`
  (the play page on bryanchasko.github.io), `study/build_pack.py:56`,
  and the generated `study/knowledge-pack.md:2`.
- Only 2 lines are functional web configuration:
  `web/vite.config.ts:6` and `web/public/404.html:9`, both the Pages
  base path. The router and components read `BASE_URL`, so they follow
  the vite base on their own.
- `origin/solution` carries 65 old-slug lines. `origin/gh-pages`
  carries 6, all in built output.
- No badges to break: `git grep -i 'raw.githubusercontent|shields.io'`
  on origin/main is empty. `.github/` holds only `dependabot.yml`
  (no hosted workflows). No CNAME on main or gh-pages.
- Live state, observed with the gh CLI: default branch `main`, public.
  Pages is `built`, build type `legacy`, source branch `gh-pages`
  path `/`, custom 404 on, HTTPS enforced.
- The recommended slug was free when checked:
  `gh api repos/BryanChasko/seattle-strands-dungeon-crawl`
  returned 404 Not Found. Re-check it in section 5, step 1.

## 3. Pre-rename code changes

Split the work in two. Display titles are safe at any time. Slug strings
are wrong before the rename and right after it, so they land only inside
the rename window. Landing the new vite base or the new clone URL early
breaks the live play page and the current Floor 0 instructions.

### 3.1 Safe at any time: display titles

Set the display name from section 1 at each of these surfaces:

- `README.md:1` and the wordmark alt text at `README.md:4` (cover lane).
- `workshop/README.md:1` plus the opening format line (done on the
  branch that adds this plan).
- `pyproject.toml` description only (done on the branch that adds this
  plan; the `[project]` name is a separate decision, see 3.3).
- `web/index.html:7` (browser title).
- `.devcontainer/devcontainer.json:2`.
- `docs/visual-design-system.md:1`.
- `study/build_pack.py:54`, then regenerate the pack with
  `python3 study/build_pack.py`. Never hand-edit
  `study/knowledge-pack.md`.

### 3.2 Rename window only: every hardcoded old-slug URL and path

Change `aiRPG-seattle-dungeon-crawl` to `seattle-strands-dungeon-crawl`
in all 53 files listed in the appendix, with these groupings:

- Functional (the play page 404s until these ship and Pages rebuilds):
  `web/vite.config.ts:6`, `web/public/404.html:9`.
- Own web addresses: `workshop/floor-0.md:95` (clone URL),
  `workshop/floor-6.md:26` (play-page URL), `study/build_pack.py:56`.
  Then regenerate `study/knowledge-pack.md` by running the builder.
- Typed paths: the 50 `cd` lines and their sibling path lines across
  `workshop/cleanup.md`, `workshop/floor-0.md` through
  `workshop/floor-8-4.md` (13 floor and cleanup pages), and the
  34 pages under `workshop/encounters/` named in the appendix.
- Branches: propagate the same change to `solution` (65 lines there).
  Do not hand-edit `gh-pages`; the rebuild in section 5, step 5
  replaces its 6 generated hits.

Before merging the prepared branch, verify it locally:

```bash
git grep -in 'aiRPG-seattle-dungeon-crawl'   # only section 3.3 keeps and this plan
python3 tools/check_docs.py --offline
uv sync
cd web && npm ci && npm test && npm run build
```

### 3.3 Deliberate keeps: do not blind-sed these

- `8_agentcore_production/ui_proxy/ui_proxy.py:18` SESSION_ID
  `campaign-airpg-seattle-dungeon-crawl-0001`, matched at
  `workshop/floor-8-4.md:414`. It names a taught AgentCore session, not
  the repo. Change both lines together or neither. Recommendation: keep.
- `pyproject.toml:2` distribution name `airpg-seattle-dungeon-crawl`.
  Nothing else in the repo references it, so renaming it is low-risk but
  optional. Owner call; this plan does not require it.
- `tools/airpg_render.py` and its importers (`tools/compose_readme_art.py:25`,
  `tools/motion.py:28`, `tools/sam_cutout.py:23`), plus the
  `AIRPG_ART_DIR` environment name. The art team owns `tools/` art code;
  renaming breaks imports for zero learner benefit.
- The `airpg-art` path segment in published art URLs (for example in
  `docs/art-placements.md`, served from bryanchasko.com). Those are
  external object keys, not repo paths.
- The NOAA `application=aiRPG_workshop` value in
  `encounters/floor-2-tide-table/tide_table.py:25` and
  `workshop/encounters/tide-table.md`. It is an API caller label.
- Lettering baked into `images/wordmark-1200x240.webp` and
  `images/banner-1680x720.webp` (see the art backlog, section 8).
  Never edit `images/` binaries outside the art lane.
- This plan file. It keeps the old slug on purpose so the steps stay
  readable after the rename. Exempt it from post-rename greps.

## 4. Redirect behavior and its limits

From GitHub's renaming-a-repository documentation
(docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository):

- Redirected automatically: the old github.com web address (repo,
  issues, pull requests, wikis, stars, followers), and git clone,
  fetch, and push against the old HTTPS or SSH remote. Every branch
  keeps working, including `main`, `solution`, and `gh-pages`.
  Existing learner clones never break, and the un-edited Floor 0 clone
  line keeps working through the redirect.
- Not redirected: project site (Pages) addresses. The old play-page
  address dies at rename time. Until steps 4 and 5 in section 5 finish,
  `workshop/floor-6.md:26` and the repo homepage point at a dead
  address, and `python3 tools/check_docs.py` without `--offline` fails
  that link (it requires status 200).
- Not redirected: hosted Actions addresses. Not applicable here; the
  repo has no workflows, only `dependabot.yml`.
- Local folder names never change on their own. A folder named
  `aiRPG-seattle-dungeon-crawl` keeps working forever; renaming it is
  optional cosmetics, and the `cd` lines only describe fresh clones.
- Reusing the old name for a new repository kills the redirects
  permanently. Never create a new `aiRPG-seattle-dungeon-crawl` repo.

## 5. Rename-day commands, in order

Do not run any of this until the section 3.2 branch is reviewed and the
gh-pages publisher has confirmed their copy and commit flow (that flow
is not codified on main: no workflow, no deploy script in
`web/package.json`).

1. Freeze merges to `main`, `solution`, and `gh-pages`. Re-verify the
   base and that the slug is still free:

   ```bash
   git fetch origin && git log -1 --format=%H origin/main
   gh api repos/BryanChasko/seattle-strands-dungeon-crawl   # expect 404
   ```

2. Merge the prepared rename PR to `main`. Propagate the same change to
   `solution`. Do not publish `gh-pages` yet.

3. Rename the repository:

   ```bash
   gh repo rename seattle-strands-dungeon-crawl -R BryanChasko/aiRPG-seattle-dungeon-crawl -y
   ```

4. Set the About text and homepage (exact strings from section 1):

   ```bash
   gh repo edit BryanChasko/seattle-strands-dungeon-crawl -d "Seattle Strands Dungeon Crawl: A Visual Lit aiRPG Workshop. Learn the Strands Agents SDK by building the System AI of a LitRPG dungeon crawl under Seattle, one floor at a time." -h "https://bryanchasko.github.io/seattle-strands-dungeon-crawl/"
   ```

5. Repoint and republish Pages. The Pages source setting itself does
   not change: it stays legacy, branch `gh-pages`, path `/`, and the
   project address follows the new repo name. What must change is the
   built output, which embeds the old base path. Rebuild from the
   renamed `main` and publish through the existing gh-pages worktree,
   preserving `.nojekyll`:

   ```bash
   cd web && npm ci && npm test && npm run build
   # copy web/dist/ into the gh-pages worktree checkout, review, commit, push
   gh api repos/BryanChasko/seattle-strands-dungeon-crawl/pages --jq .html_url
   # expect: https://bryanchasko.github.io/seattle-strands-dungeon-crawl/
   ```

6. Fix local remotes. All linked worktrees of this repo share one
   `.git`, so one `set-url` in any of them fixes every worktree on
   this machine. Run `git worktree list` first and work from its real
   output; when this plan was written it showed 15 worktrees,
   including the `aiRPG-seattle-dungeon-crawl-gh-pages` checkout
   (branch `gh-pages`), the `aiRPG-seattle-dungeon-crawl-solution`
   checkout (branch `solution`), and the `wt-airpg-*` lanes:

   ```bash
   git worktree list
   git remote set-url origin https://github.com/BryanChasko/seattle-strands-dungeon-crawl.git
   git fetch origin
   ```

   Any separate clone (its own `.git`, for example on another machine)
   needs the same two commands inside that clone. The `upstream`
   remote (aws-samples) is untouched. Renaming local folders, for
   example `mv aiRPG-seattle-dungeon-crawl seattle-strands-dungeon-crawl`,
   is optional and must be done per worktree only after that worktree
   is clean; never move a worktree folder by hand while lanes are
   active in it, use `git worktree move`.

7. Run the full verification checklist in section 6 before announcing
   the new address anywhere.

## 6. Post-rename verification checklist

Every line must pass with real output, not assumption:

- [ ] Repo metadata:
  `gh repo view BryanChasko/seattle-strands-dungeon-crawl --json url,description,homepageUrl`
  shows the section 1 About text and homepage.
- [ ] Old web address redirects:
  `curl -sI https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl`
  returns a 301 to the new repo address.
- [ ] Old git remote still works:
  `git ls-remote https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl.git HEAD`
  returns a commit.
- [ ] Fresh clones work both ways, in a scratch folder outside the repo:
  `git clone https://github.com/BryanChasko/seattle-strands-dungeon-crawl.git`
  and the old-address clone both complete, and each clone can
  `git fetch origin` and check out `main` and `solution`.
- [ ] Site loads: `curl -sI https://bryanchasko.github.io/seattle-strands-dungeon-crawl/`
  returns 200, and the page opens in a browser with its CSS and JS
  assets loading (no asset 404s in the network panel).
- [ ] Old site address is dead on purpose:
  `curl -sI https://bryanchasko.github.io/aiRPG-seattle-dungeon-crawl/`
  returns 404, and a repo-wide grep confirms nothing still links it.
- [ ] Floor 6 page links resolve: the link at `workshop/floor-6.md:26`
  opens the new play page; from that page, `textures/obsidian-512x512.webp`
  and `dice/d20.svg` under the new base return 200; an in-app route
  (start page to game page) survives a browser refresh through the
  custom 404 redirect.
- [ ] No stray old slug: `git grep -in 'aiRPG-seattle-dungeon-crawl' HEAD`
  on `main` and on `solution` shows only the section 3.3 keeps and
  this plan file.
- [ ] Gates green on the renamed tree: `python3 tools/check_docs.py`
  (online, so the Floor 6 link must return 200), `uv sync`, and
  `cd web && npm test && npm run build`.
- [ ] Study pack current: `python3 study/build_pack.py --check` passes
  (regenerate with `python3 study/build_pack.py` if it does not).
- [ ] Every local worktree fetches clean: `git fetch origin` succeeds,
  and `git worktree list` lanes on `gh-pages` and `solution` show the
  published tips.

## 7. Rollback

Clean only while the old name has not been reused and the new address
has not been announced. In order:

1. Rename back:

   ```bash
   gh repo rename aiRPG-seattle-dungeon-crawl -R BryanChasko/seattle-strands-dungeon-crawl -y
   ```

2. Restore the old About text from section 1:

   ```bash
   gh repo edit BryanChasko/aiRPG-seattle-dungeon-crawl -d "Powered by Strands SDK. Learn to build AI agents by running a LitRPG dungeon crawl under Seattle, one floor at a time." -h "https://bryanchasko.github.io/aiRPG-seattle-dungeon-crawl/"
   ```

3. Revert the section 3.2 slug commits on `main` and `solution`
   (display titles from section 3.1 may stay; they are true under
   either slug).
4. Rebuild `web/` from the reverted tree and republish `gh-pages`
   exactly as in section 5, step 5, so the old play-page address
   serves again.
5. Point local remotes back:
   `git remote set-url origin https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl.git`
   once per `.git`, then `git fetch origin`.
6. Re-run section 6 with old and new swapped: old Pages address 200,
   new Pages address 404, gates green. Note the same warning in
   reverse: after a rollback, never reuse `seattle-strands-dungeon-crawl`
   for a different repo, or its redirects die too.

## 8. Art backlog (art lane owns renders; nothing here edits images)

1. Recompose the wordmark with the new display name and the format
   line "A Visual Lit aiRPG Workshop" (`tools/compose_readme_art.py`
   still sets the old title text; output replaces
   `images/wordmark-1200x240.webp`).
2. Spoiler-safe hero re-roll for the banner slot used at the top of
   `workshop/README.md` and the repo cover: the wreck, shadow, one arm,
   an eye. Full dance reveal is earned later, and companions who join
   on later floors never appear on cover, Floor 0, or Floor 1 surfaces.
   Until the re-roll lands, alt text on those surfaces stays tease-only.
3. Optional social preview crop (1200x630, plus 1280x640 for the repo
   social-preview upload) derived from item 2 once it exists.

## 9. Open owner calls

- SESSION_ID keep-or-change (section 3.3). Recommendation: keep.
- `pyproject.toml` distribution name keep-or-change (section 3.3).
- The exact gh-pages publish flow (section 5 preamble): the publisher
  confirms it before rename day; it is not codified on main.
- The rename window itself: pick a time when no learner cohort is
  mid-floor, since the play page is down between steps 3 and 5.

## 10. Root restructure (same window, after the art team lands)

The repo root is crowded and slow to scroll. On rename day, after the
art team finishes and before the section 5 commands, collapse the root
to the README plus three folders; everything else moves under them.
Do not start this early: floor pages, `study/build_pack.py`,
`tools/check_docs.py`, and the web build all reference current root
paths, so the move and every reference fix land in one prepared
branch, gated the same way as the slug change.

Target shape (names provisional, decided on the branch):

- `README.md` stays at root, alone.
- `dungeon/` (or `crawl/`): the workshop — `workshop/`, `study/`,
  `tools/` (docs tooling), `characters.json`, floor code folders
  (`0_stairwell/` through `8_agentcore_production/`,
  `encounters/`).
- `site/` (or `play/`): the web interface — `web/`, `assets/hud/`.
- `art/`: `images/`, `docs/` art plans, art tooling out of
  `tools/` (render, compose, publish scripts).

Rules for the move branch: every `cd`, relative link, image path,
`build_pack.py` ROOT, check-docs roots, and vite base move together;
`git grep` for the old top-level names must come back clean except
this plan; full gates (`check_docs.py`, pack `--check`, `uv sync`,
web tests, solution tests) before the rename-day merge. Local folder
renames (`mv aiRPG-seattle-dungeon-crawl seattle-strands-dungeon-crawl`)
happen in the same window, so learners clone once into the final
shape instead of twice.

## Appendix: the 53 files carrying the old slug on origin/main

From `git grep -il 'aiRPG-seattle-dungeon-crawl' origin/main` at
e3c09614c0fbdc58f0cc3fe126ab877efcf94bb2. Re-run the command on rename
day; this list is a snapshot, not the source of truth.

```text
8_agentcore_production/ui_proxy/ui_proxy.py
pyproject.toml
study/build_pack.py
study/knowledge-pack.md
web/public/404.html
web/vite.config.ts
workshop/cleanup.md
workshop/encounters/ask-the-player.md
workshop/encounters/barnaby-takes-the-call.md
workshop/encounters/broadcast-booth.md
workshop/encounters/commentary-booth.md
workshop/encounters/concurrent-shuffle.md
workshop/encounters/context-flood.md
workshop/encounters/delivery-drone-horde.md
workshop/encounters/developer-advocate-swarm.md
workshop/encounters/ferry-manifest.md
workshop/encounters/grudge-ledger.md
workshop/encounters/house-rules-guardrails.md
workshop/encounters/hype-meter.md
workshop/encounters/keyword-versus-vector.md
workshop/encounters/launch-commit-criteria.md
workshop/encounters/living-workbench.md
workshop/encounters/locks-turnstile.md
workshop/encounters/mid-song-save.md
workshop/encounters/pad-explosion-aftermath.md
workshop/encounters/paper-trail.md
workshop/encounters/policy-gatekeeper.md
workshop/encounters/quarterly-earnings-call.md
workshop/encounters/range-safety-officer.md
workshop/encounters/read-the-receipt.md
workshop/encounters/read-the-room-typed.md
workshop/encounters/reasoning-dial.md
workshop/encounters/sandbox-tide-pool.md
workshop/encounters/save-points.md
workshop/encounters/sponsor-interrupt.md
workshop/encounters/static-fire.md
workshop/encounters/subcontract-the-paperwork.md
workshop/encounters/system-holds-grudges.md
workshop/encounters/tide-table.md
workshop/encounters/trace-the-portal.md
workshop/encounters/warehouse-automation-grid.md
workshop/floor-0.md
workshop/floor-1.md
workshop/floor-2.md
workshop/floor-3.md
workshop/floor-4.md
workshop/floor-5.md
workshop/floor-6.md
workshop/floor-7.md
workshop/floor-8-2.md
workshop/floor-8-3.md
workshop/floor-8-4.md
workshop/floor-8.md
```
