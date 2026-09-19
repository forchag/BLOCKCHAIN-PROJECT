package main

import (
	"fmt"
	"testing"
)

// These benchmarks exercise CheckAccess's own chaincode-level decision cost
// in isolation, through the same in-memory mockStub the correctness tests in
// contract_test.go use, not against a real Fabric network. They do not
// reproduce the manuscript's field measurements, which time a complete
// endorse-order-validate-commit transaction: the manuscript's Discussion
// section is explicit that a re-run of those campaigns against the corrected
// chaincode has not been performed. What this benchmark adds is a narrower,
// actually-run comparison: whether the corrected role hierarchy in this
// package (roles.go) changes the pure Go execution cost of the same
// CheckAccess call, holding everything else (state backend, workload,
// hardware) fixed against the identical benchmark in
// chaincode/hrbac/contract_bench_test.go.
//
// Run with: go test -bench=CheckAccess -benchtime=2000x -run=^$ -benchmem -count=5

func setBenchCaller(b *testing.B, stub *mockStub, id string, role Role, zone string, serial int64) {
	b.Helper()
	cert, err := makeTestCertificatePEM(id, role, zone, serial)
	if err != nil {
		b.Fatalf("failed to build benchmark certificate: %v", err)
	}
	stub.attributes = map[string]string{"hf.EnrollmentID": id, "role": string(role), "zone": zone}
	stub.creator = cert
}

func BenchmarkCheckAccessGrant(b *testing.B) {
	ctx, stub := newMockContext("bench-setup", 1_700_000_000)
	s := &SmartContract{}
	if err := s.AssignRole(ctx, "farmer-bench", string(Farmer), "North", "2030-01-01T00:00:00Z", "n-bench-assign"); err != nil {
		b.Fatalf("setup AssignRole failed: %v", err)
	}
	setBenchCaller(b, stub, "farmer-bench", Farmer, "North", 101)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		stub.setTx(fmt.Sprintf("bench-grant-%d", i), 1_700_000_001)
		ok, err := s.CheckAccess(ctx, "farmer-bench", string(WriteSensor), "North", "")
		if err != nil || !ok {
			b.Fatalf("unexpected result ok=%v err=%v", ok, err)
		}
	}
}

func BenchmarkCheckAccessDeny(b *testing.B) {
	ctx, stub := newMockContext("bench-setup-deny", 1_700_000_000)
	s := &SmartContract{}
	if err := s.AssignRole(ctx, "farmer-bench-2", string(Farmer), "North", "2030-01-01T00:00:00Z", "n-bench-assign2"); err != nil {
		b.Fatalf("setup AssignRole failed: %v", err)
	}
	setBenchCaller(b, stub, "farmer-bench-2", Farmer, "North", 102)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		stub.setTx(fmt.Sprintf("bench-deny-%d", i), 1_700_000_001)
		ok, err := s.CheckAccess(ctx, "farmer-bench-2", string(AdminAll), "North", "")
		if err != nil || ok {
			b.Fatalf("unexpected result ok=%v err=%v", ok, err)
		}
	}
}
