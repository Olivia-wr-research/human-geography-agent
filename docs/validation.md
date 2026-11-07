# Validation

## Local checks

- Python standard-library test suite: 10 tests passed on 2026-11-07.
- Covered: stage ordering, missing evidence, revision/rejection, approved-file modification detection, deterministic synthetic data, duplicate IDs, invalid coordinates, unmatched endpoints, antimeridian handling and overwrite prevention.
- Synthetic fixture generated and hashed. No research dataset or model was executed.
- Skill frontmatter and source compilation are checked during packaging.

## QGIS

The local environment did not provide QGIS. GitHub Actions ran the integration test on Ubuntu 24.04 / QGIS 3.34.4-Prizren. It exported PNG/PDF, saved the QGZ project and reopened two valid vector layers with one layout. The corrected version also checks A4 portrait dimensions and a readable portrait PNG.

[Test run for the corrected code](https://github.com/Olivia-wr-research/human-geography-agent/actions/runs/42383417050), code commit `37322e6090f62793fbb0a4fe8b9dfb1b6de1a4ba`.

The first export passed file checks but visual inspection found a landscape default that cropped the footer. The script now explicitly selects A4 portrait. This illustrates why successful export alone is not visual QA. The corrected PNG was inspected for complete points/links, title, legend, scale bar and source notes. PDF export was tested, but a separate PDF-render comparison was not performed.

The QGIS runtime may emit a GDAL message about PNG update access; export status, PNG decoding and project reopening are checked separately. This does not establish compatibility with every runtime or scientific validity on real data.

## Limits

The stage ledger checks existence and content hashes; it does not authenticate the decision maker, enforce filesystem access or evaluate scientific quality. Arbitrary nonempty evidence cannot be treated as substantive approval. The skill requires the researcher to review evidence and explicitly decide.

No original-paper numerical replication, human user study, real-data QGIS validation or journal-readiness assessment was performed. Public release includes only newly authored code, workflow documentation and fictional fixtures.
