# Source Ranking Rubric

Score candidate sources before using them heavily. Stars help discovery but do not determine quality alone.

## Scoring Table

| Dimension | Score | Guidance |
|---|---:|---|
| Authority | 0-5 | Official docs/repos and maintainers score higher. |
| Relevance | 0-5 | Directly about the topic and requested angle. |
| Recency | 0-5 | Recently updated, compatible with current APIs/features. |
| Adoption | 0-5 | Stars, forks, dependents, community mentions. |
| Documentation | 0-5 | Clear README, examples, architecture, limitations. |
| Practicality | 0-5 | Can be applied by the user, not only conceptual. |
| Evidence quality | 0-5 | Includes examples, workflows, tests, CI, issues, or real cases. |
| Maintainability | 0-5 | Active issues/PRs/releases and clear ownership. |

## Penalties

- `-5`: likely outdated for current versions.
- `-5`: mostly marketing with little implementation detail.
- `-3`: no clear license or usage path.
- `-3`: copied/duplicated awesome list with no curation.
- `-2`: too narrow for the requested audience.

## Source Classes

- **Tier A**: official docs/repos, canonical specs, actively maintained high-quality projects.
- **Tier B**: high-signal community best-practice repos, workflow kits, example projects.
- **Tier C**: useful but narrow tools, smaller examples, articles with concrete implementation.
- **Exclude**: stale, low-evidence, SEO-only, duplicated, or unverifiable content.

## Minimum Evidence Rules

- Use at least one official/primary source for factual claims when available.
- Use multiple community sources before calling something a "best practice".
- Prefer source links that a user can inspect later.
- Clearly label inference and recommendations.
