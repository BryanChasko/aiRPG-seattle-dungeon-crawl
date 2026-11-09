# Rename-day execution note (prepared on the move branch, not sent)

This branch (`move/root-restructure`) is the prepared tree. The slug
change itself is NOT in this branch except the code-side rename-day
state (vite base, 404, links.ts, ServerHelp, NewGameView). Run the
steps below in order, in one sitting, after this branch merges.

## Freeze order

1. Art lane lands first (renders, sidecars, `art/images/plans/*`).
2. Merge this move branch to `main`. Propagate the same tree to the
   solution replica branch (`move/root-restructure-solution`).
3. Merge the prepared slug branch (the 50 `cd` lines, floor-page URLs,
   build_pack source-of-truth string, play-page URLs) to `main` and to
   `solution`. Do not publish `gh-pages` yet.
4. Rename, set About, rebuild, republish (below).
5. Run the full verification checklist before announcing.

Do not rename local worktree folders by hand while lanes are active;
use `git worktree move`. Never create a new repo under the old name;
that kills the redirects permanently.

## Rename

```bash
git fetch origin && git log -1 --format=%H origin/main
gh api repos/BryanChasko/seattle-strands-dungeon-crawl   # expect 404
gh repo rename seattle-strands-dungeon-crawl -R BryanChasko/aiRPG-seattle-dungeon-crawl -y
```

## About text and homepage (exact strings)

```bash
gh repo edit BryanChasko/seattle-strands-dungeon-crawl -d "Seattle Strands Dungeon Crawl: A Visual Lit aiRPG Workshop. Learn the Strands Agents SDK by building the System AI of a LitRPG dungeon crawl under Seattle, one floor at a time." -h "https://bryanchasko.github.io/seattle-strands-dungeon-crawl/"
```

## gh-pages rebuild and publish

The Pages source setting does not change: legacy, branch `gh-pages`,
path `/`. Only the built output changes (it embeds the base path).
Rebuild from the renamed `main` and publish through the existing
gh-pages worktree, preserving `.nojekyll`:

```bash
cd site/web && npm ci && npm test && npm run build
# copy site/web/dist/ into the gh-pages worktree checkout, review, commit, push
# keep .git/, .nojekyll and .prettierignore exactly as they are
gh api repos/BryanChasko/seattle-strands-dungeon-crawl/pages --jq .html_url
# expect: https://bryanchasko.github.io/seattle-strands-dungeon-crawl/
```

## Post-rename paths (new tree)

- Docs gate: `python3 dungeon/check_docs.py` (add `--offline` to skip
  the network check).
- Study pack: `python3 dungeon/study/build_pack.py --check`
  (regenerate with `python3 dungeon/study/build_pack.py`).
- Python deps: `uv sync`.
- Web: `cd site/web && npm test && npm run build`.
- Preflight: `uv run python dungeon/0_stairwell/preflight.py`.
- Solution tests: full `pytest` on the solution replica branch.

## Verification checklist (section 6, condensed)

- `gh repo view BryanChasko/seattle-strands-dungeon-crawl
  --json url,description,homepageUrl` shows the About text above.
- `curl -sI https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl`
  returns a 301 to the new address.
- `git ls-remote
  https://github.com/BryanChasko/aiRPG-seattle-dungeon-crawl.git HEAD`
  returns a commit (old remote still works).
- Fresh clones of both addresses complete; `git fetch origin` and
  checkout of `main` and `solution` work in each.
- `curl -sI https://bryanchasko.github.io/seattle-strands-dungeon-crawl/`
  returns 200 with CSS and JS loading and no asset 404s.
- `curl -sI https://bryanchasko.github.io/aiRPG-seattle-dungeon-crawl/`
  returns 404, and nothing in the repo links it.
- The Floor 6 link opens the new play page; `textures/` and dice
  assets under the new base return 200; an in-app route survives a
  refresh through the custom 404 redirect.
- `git grep -in 'aiRPG-seattle-dungeon-crawl'` on `main` and on
  `solution` shows only the section 3.3 keeps and the rename plan.
- Gates green on the renamed tree: docs gate (online), `uv sync`,
  `npm test` and `npm run build` in `site/web`, full `pytest` on
  solution, study pack current.
- Every local worktree fetches clean: `git fetch origin` succeeds.
