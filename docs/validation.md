# Validation

## Local checks

- Python standard-library test suite: 10 tests passed on 2026-11-07.
- Covered: stage ordering, missing evidence, revision/rejection, approved-file modification detection, deterministic synthetic data, duplicate IDs, invalid coordinates, unmatched endpoints, antimeridian handling and overwrite prevention.
- Synthetic fixture generated and hashed. No research dataset or model was executed.
- Skill frontmatter and source compilation are checked during packaging.

## QGIS

The local environment did not provide QGIS. The script is based on versioned official PyQGIS documentation. The repository includes a headless QGIS CI job that exports a synthetic project, PNG and PDF and checks reopening with valid layers. A green job establishes only that tested environment's export/reopen behavior; visual review and real-data cartographic validity remain separate.

## Limits

The stage ledger checks existence and content hashes; it does not authenticate the decision maker, enforce filesystem access or evaluate scientific quality. Arbitrary nonempty evidence cannot be treated as substantive approval. The skill requires the researcher to review evidence and explicitly decide.

No original-paper numerical replication, human user study, real-data QGIS validation or journal-readiness assessment was performed. Public release includes only newly authored code, workflow documentation and fictional fixtures.
