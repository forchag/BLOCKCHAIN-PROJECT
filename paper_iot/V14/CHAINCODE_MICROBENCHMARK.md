# Chaincode decision-cost microbenchmark

This file records the isolated Go mock-stub benchmark cited by the manuscript.
It is not a Fabric-network, field-deployment, endorsement, ordering, validation
or commit measurement.

New
`contract_bench_test.go` files in both `chaincode/hrbac` and
`chaincode/hrbac-corrected` benchmark `CheckAccess` (one grant path, one
deny path) against the same in-memory mock state both packages' unit
tests already use. This is Go execution time only, not a Fabric-network
measurement, and it is reported as such in Section "Authorization-policy
findings." Raw output (`go test -bench=CheckAccess -benchtime=2000x
-benchmem -count=5`), reproducible from either package directory:

```
chaincode/hrbac:
BenchmarkCheckAccessGrant-4   2000   288944 ns/op   136228 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279430 ns/op   136227 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279129 ns/op   136756 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   299273 ns/op   136713 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   267974 ns/op   136505 B/op   1108 allocs/op
BenchmarkCheckAccessDeny-4    2000   285897 ns/op   134521 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273741 ns/op   134410 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273090 ns/op   134811 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   273046 ns/op   134868 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   280904 ns/op   135197 B/op   1107 allocs/op

chaincode/hrbac-corrected:
BenchmarkCheckAccessGrant-4   2000   283609 ns/op   136305 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   279770 ns/op   136286 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   276094 ns/op   136521 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   271037 ns/op   137530 B/op   1108 allocs/op
BenchmarkCheckAccessGrant-4   2000   273955 ns/op   136868 B/op   1108 allocs/op
BenchmarkCheckAccessDeny-4    2000   285155 ns/op   134661 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   279265 ns/op   134634 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   277807 ns/op   135039 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   286514 ns/op   134830 B/op   1107 allocs/op
BenchmarkCheckAccessDeny-4    2000   280885 ns/op   135014 B/op   1107 allocs/op
```

Grant-path mean 282.9µs (SD 11.8) vs. 276.9µs (SD 4.9), Welch
t=1.06, df=5.36, p=0.33. Deny-path mean 277.3µs (SD 5.8) vs. 281.9µs
(SD 3.8), t=-1.48, df=6.85, p=0.18. Neither is distinguishable from
run-to-run noise at n=5 runs per package. This narrows one cell of scope
item S5 (the chaincode's own share of decision cost); it says nothing about
endorsement, ordering, commit, or network-level latency and throughput,
which remain unmeasured for the corrected chaincode.

## Interpretation

At five runs per package, neither Welch test detected a statistically
significant difference. Nonsignificance does not establish statistical
equivalence. The result is limited to Go execution inside the mock-stub
harness.
