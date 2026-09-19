# Version 11 premortem

The eight-reviewer premortem is maintained in
`analysis/V11_PREMORTEM.md`. The review found and fixed the following
submission risks before build: unsupported outage/data-loss wording, embedded
Highlights, physical-scale-out and saturation overclaims, transaction-level
pseudoreplication, post-data equivalence overclaiming, CRT-bound misuse,
signature-validity overinterpretation, corrected-code performance conflation,
privacy-coordinate exposure, unsupported repository metadata, and incomplete
declarations.

The remaining evidence boundaries are explicit in the manuscript: the sensor
table cannot prove capture-time buffering through outages; the controlled peer
campaign varies logical peers on fixed hosts; the throughput benchmark reports
an observed peak rather than capacity; the denial corpus has no positive
requests; revocation records lack episode identifiers; and corrected-code
performance has not been re-benchmarked.

The full eight-reviewer response is in `analysis/V11_REVIEW_REPORT.md`.
