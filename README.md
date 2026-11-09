# CodeSearch

A codebase search tool that stays accurate as the code changes and as permissions change.

> **Status:** early design. Nothing here is implemented yet. This README records the problem, the goals, and the intended design so the first code has something to answer to.

## The problem

Most code search tools build an index once and refresh it on a schedule. Between refreshes, two kinds of drift creep in:

1. **Content drift.** Files get edited, renamed, or deleted, and branches move. Search results point at lines that no longer exist, miss code that was just added, or return stale snippets.
2. **Permission drift.** Someone loses access to a repo, a repo goes private, or a team is removed from a group. The index still holds that code, and search keeps returning it to people who should no longer see it.

Content drift makes search wrong. Permission drift makes it a data leak.

## Goals

- **Fresh results.** A change to the code shows up in search within a bounded, measurable delay.
- **Permission-correct results.** A user never sees a result they could not open in the source system at the moment they search.
- **Honest about staleness.** Every result says which commit it was indexed from, so a user can tell whether it might be out of date.
- **Incremental by default.** Re-index what changed, not the whole corpus.

### Non-goals (for now)

- Replacing a full IDE or language server.
- Hosting or mirroring repositories as a source of truth.

## Design principles

**Permissions are checked when you search, not only when you index.**
Recording ACLs at index time is useful for filtering quickly, but it is a cache. The authoritative check runs against current permissions before results are returned. If the two disagree, the query-time answer wins and the index is corrected.

**Fail closed.**
If the permission source can't be reached or returns something ambiguous, the result is withheld.

**Every indexed document is tied to a specific version.**
Each chunk records `(repo, commit SHA, path, byte range)`. Results are traceable to an exact version and can be checked against the current HEAD.

**Change events drive indexing, and a periodic sweep backs them up.**
Webhooks and push events trigger incremental updates. A slower periodic reconciliation catches anything the events missed, such as dropped webhooks or force-pushes.

## Architecture sketch

```
   Source systems (GitHub / GitLab / local git)
        │                     │
   code change events    permission change events
        │                     │
        ▼                     ▼
  ┌───────────┐         ┌──────────────┐
  │ Ingestor  │         │ ACL syncer   │
  │ (diff →   │         │ (users,      │
  │  chunks)  │         │  groups,     │
  └─────┬─────┘         │  repo access)│
        │               └──────┬───────┘
        ▼                      ▼
  ┌──────────────────────────────────┐
  │ Index                            │
  │  - lexical (exact / regex)       │
  │  - semantic (embeddings)         │
  │  - per-chunk version + ACL tags  │
  └────────────────┬─────────────────┘
                   │
                   ▼
  ┌──────────────────────────────────┐
  │ Query service                    │
  │  1. retrieve candidates          │
  │  2. pre-filter by ACL tags       │
  │  3. re-check live permissions    │  ◄── authoritative
  │  4. annotate freshness           │
  └──────────────────────────────────┘
```

### Components

| Component | Responsibility |
|---|---|
| **Ingestor** | Turns commits and diffs into chunk additions, updates, and deletions. Handles renames, deletes, and branch moves. |
| **ACL syncer** | Mirrors who can see which repos and paths. Reacts to permission events and reconciles periodically. |
| **Index** | Stores chunks with version metadata and ACL tags. Supports both lexical and semantic retrieval. |
| **Query service** | Retrieves candidates, enforces permissions, ranks results, and reports how fresh each result is. |
| **Reconciler** | A periodic job that diffs the index against the source of truth for both content and permissions, and repairs any drift. |

## Measuring accuracy

"Stays accurate" should be measured, not just asserted. Metrics to track:

- **Index lag:** time from a push to the change being searchable (p50 / p95).
- **Stale-hit rate:** share of returned results whose indexed commit is behind HEAD for that path.
- **Permission revocation lag:** time from losing access to results disappearing.
- **Permission leak count:** results returned that fail the live permission check. The target is zero; any nonzero value is a bug.

## Roadmap

- [ ] Pick the language and storage stack
- [ ] Local-git ingestor with incremental, commit-aware chunking
- [ ] Lexical index with per-chunk version metadata
- [ ] Query service with freshness annotations
- [ ] Permission model and ACL syncer (start with a single provider, e.g. GitHub)
- [ ] Query-time permission re-check, failing closed
- [ ] Reconciler for content and ACL drift
- [ ] Semantic retrieval layer
- [ ] Accuracy metrics and a test harness that simulates edits and permission changes

## Open questions

- How fine-grained do permissions need to be: per repo, per path (e.g. CODEOWNERS or monorepo rules), or per branch?
- Which branches get indexed: only the default branch, or all of them?
- How should a live permission check be cached so it stays fast without serving decisions that are out of date?
- How should embeddings for semantic search be handled when a chunk changes slightly? Re-embed it, or tolerate a small mismatch?

## Getting started

Setup instructions will go here once the stack is chosen.

## License

TBD
