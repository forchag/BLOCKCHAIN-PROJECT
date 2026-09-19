package main

import (
	"crypto/rand"
	"crypto/rsa"
	"crypto/x509"
	"crypto/x509/pkix"
	"encoding/base64"
	"encoding/json"
	"encoding/pem"
	"math/big"
	"os"
	"testing"
	"time"

	"github.com/hyperledger/fabric-chaincode-go/shim"
	"github.com/stretchr/testify/require"
)

type mockContext struct {
	stub shim.ChaincodeStubInterface
}

func (m *mockContext) GetStub() shim.ChaincodeStubInterface {
	return m.stub
}

type mockStub struct {
	state      map[string][]byte
	txID       string
	timestamp  *shim.Timestamp
	creator    []byte
	attributes map[string]string
}

func newMockContext(txID string, seconds int64) (*mockContext, *mockStub) {
	stub := &mockStub{
		state:      make(map[string][]byte),
		txID:       txID,
		timestamp:  &shim.Timestamp{Seconds: seconds},
		attributes: map[string]string{"hf.EnrollmentID": "admin", "role": string(Admin), "zone": "North"},
	}
	var err error
	stub.creator, err = makeTestCertificatePEM("admin", Admin, "North", 1)
	if err != nil {
		panic(err)
	}
	return &mockContext{stub: stub}, stub
}

func (m *mockStub) GetState(key string) ([]byte, error) {
	return m.state[key], nil
}

func (m *mockStub) PutState(key string, value []byte) error {
	if value == nil {
		m.state[key] = nil
		return nil
	}
	copyValue := append([]byte(nil), value...)
	m.state[key] = copyValue
	return nil
}

func (m *mockStub) DelState(key string) error {
	delete(m.state, key)
	return nil
}

func (m *mockStub) GetTxTimestamp() (*shim.Timestamp, error) {
	return m.timestamp, nil
}

func (m *mockStub) GetTxID() string {
	return m.txID
}

func (m *mockStub) GetCreator() ([]byte, error) {
	return m.creator, nil
}

func (m *mockStub) GetAttributeValue(name string) (string, bool, error) {
	value, ok := m.attributes[name]
	return value, ok, nil
}

func (m *mockStub) setCaller(t *testing.T, id string, role Role, zone string, serial int64) {
	t.Helper()
	m.attributes = map[string]string{"hf.EnrollmentID": id, "role": string(role), "zone": zone}
	m.creator = testCertificatePEM(t, id, role, zone, serial)
}

func (m *mockStub) setTx(txID string, seconds int64) {
	m.txID = txID
	m.timestamp = &shim.Timestamp{Seconds: seconds}
}

func testCertificatePEM(t *testing.T, id string, role Role, zone string, serial int64) []byte {
	t.Helper()
	cert, err := makeTestCertificatePEM(id, role, zone, serial)
	require.NoError(t, err)
	return cert
}

func makeTestCertificatePEM(id string, role Role, zone string, serial int64) ([]byte, error) {
	key, err := rsa.GenerateKey(rand.Reader, 1024)
	if err != nil {
		return nil, err
	}
	attrs, err := json.Marshal(map[string]map[string]string{"attrs": {"role": string(role), "zone": zone}})
	if err != nil {
		return nil, err
	}
	tmpl := &x509.Certificate{
		SerialNumber: big.NewInt(serial),
		Subject: pkix.Name{
			CommonName:         id,
			OrganizationalUnit: []string{string(role)},
			Locality:           []string{zone},
		},
		NotBefore: time.Unix(1_600_000_000, 0),
		NotAfter:  time.Unix(2_000_000_000, 0),
		ExtraExtensions: []pkix.Extension{{
			Id:    []int{1, 2, 3, 4, 5, 6, 7, 8, 1},
			Value: attrs,
		}},
	}
	der, err := x509.CreateCertificate(rand.Reader, tmpl, tmpl, &key.PublicKey, key)
	if err != nil {
		return nil, err
	}
	return pem.EncodeToMemory(&pem.Block{Type: "CERTIFICATE", Bytes: der}), nil
}

func futureISO(seconds int64) string {
	return time.Unix(seconds, 0).UTC().Format(time.RFC3339)
}

func decodeRole(t *testing.T, stub *mockStub, subject string) RoleAssignment {
	t.Helper()
	var assignment RoleAssignment
	require.NoError(t, json.Unmarshal(stub.state[roleKey(subject)], &assignment))
	return assignment
}

func TestAdminInheritsAllPermissions(t *testing.T) {
	permissions := GetEffectivePermissions(Admin)

	for _, permission := range []Permission{ReadOwn, ReadZone, ReadAll, WriteSensor, ControlZone, ControlAll, ReadAudit, ManageRoles, IssueCrossZone, AdminAll} {
		require.Contains(t, permissions, permission)
	}
}

func TestFarmerInheritsFromAgronomistSupplyChain(t *testing.T) {
	// Corrected hierarchy: Farmer no longer inherits from Certifier, so
	// ReadAudit is not among its permissions. Every other capability the
	// deployed hierarchy gave Farmer is preserved.
	permissions := GetEffectivePermissions(Farmer)

	require.Contains(t, permissions, WriteSensor)
	require.Contains(t, permissions, ControlZone)
	require.Contains(t, permissions, IssueCrossZone)
	require.Contains(t, permissions, ReadZone)
	require.Contains(t, permissions, ReadOwn)
	require.NotContains(t, permissions, ReadAudit)
}

// TestAuditorSeparationHolds is the regression test the postmortem's
// implementation audit motivates: it fails against the deployed hierarchy
// in chaincode/hrbac (Certifier on the human inheritance chain) and passes
// against this corrected one. A mutation reintroducing Certifier into
// Agronomist's or Farmer's ancestor set, or restoring ReadZone to
// Certifier's direct grants, should make it fail again.
func TestAuditorSeparationHolds(t *testing.T) {
	require.NotContains(t, GetEffectivePermissions(Agronomist), ReadAudit,
		"Agronomist must not inherit audit-log access")
	require.NotContains(t, GetEffectivePermissions(Farmer), ReadAudit,
		"Farmer must not inherit audit-log access")
	require.Contains(t, GetEffectivePermissions(Certifier), ReadAudit,
		"Certifier must retain audit-log access")
	require.NotContains(t, GetEffectivePermissions(Certifier), ReadZone,
		"Certifier must not read raw zone sensor data directly")
	require.Contains(t, GetEffectivePermissions(Agronomist), ReadZone,
		"Agronomist must keep zone sensor visibility despite the fix")
}

// policyRequirements mirrors the schema of ../policy-requirements.json, an
// independent, requirements-derived policy oracle authored without
// reference to this package's or chaincode/hrbac's roles.go.
type policyRequirements struct {
	Roles       []string                   `json:"roles"`
	Permissions []string                   `json:"permissions"`
	Matrix      map[string]map[string]bool `json:"matrix"`
}

// TestMatchesRequirementsOracle is the independent-oracle test a reviewer
// premortem asked for: it scores GetEffectivePermissions() against
// ../policy-requirements.json, a file authored from the manuscript's
// stakeholder requirements rather than generated from this or any other
// roles.go, so a defect shared between an implementation and a
// code-derived permission table cannot hide from it. It fails against
// chaincode/hrbac's deployed hierarchy (confirmed the same way
// TestAuditorSeparationHolds and TestAgronomistCannotControlZone were: a
// throwaway copy of this test run against that package during
// development) and passes here.
func TestMatchesRequirementsOracle(t *testing.T) {
	data, err := os.ReadFile("../policy-requirements.json")
	require.NoError(t, err, "independent policy oracle must be readable")

	var req policyRequirements
	require.NoError(t, json.Unmarshal(data, &req))
	require.True(t, len(req.Roles) > 0, "oracle must list roles")
	require.True(t, len(req.Permissions) > 0, "oracle must list permissions")

	for _, role := range req.Roles {
		effective := make(map[Permission]struct{})
		for _, p := range GetEffectivePermissions(Role(role)) {
			effective[p] = struct{}{}
		}
		expected, ok := req.Matrix[role]
		require.True(t, ok, "oracle missing expected row for role %s", role)
		for _, perm := range req.Permissions {
			want, ok := expected[perm]
			require.True(t, ok,
				"oracle missing expected cell for %s/%s", role, perm)
			_, have := effective[Permission(perm)]
			require.Equal(t, want, have,
				"role %s, permission %s: oracle expects %v, "+
					"chaincode grants %v", role, perm, want, have)
		}
	}
}

// TestAgronomistCannotControlZone is the regression test for the second
// defect found in this corrected package: an earlier draft of the fix
// above left Agronomist with a direct ControlZone grant, contradicting
// the introduction's "history but no actuation rights" description. It
// fails against that earlier draft and against chaincode/hrbac's deployed
// hierarchy (both grant Agronomist ControlZone) and passes here. A
// mutation restoring ControlZone to Agronomist's direct grants, or
// removing it from Farmer's, should make it fail again.
func TestAgronomistCannotControlZone(t *testing.T) {
	require.NotContains(t, GetEffectivePermissions(Agronomist), ControlZone,
		"Agronomist must not hold zone actuation rights")
	require.Contains(t, GetEffectivePermissions(Farmer), ControlZone,
		"Farmer must retain zone actuation rights")
}

func TestSensorDoesNotInheritFarmerPermissions(t *testing.T) {
	permissions := GetEffectivePermissions(Sensor)

	require.Contains(t, permissions, WriteSensor)
	require.NotContains(t, permissions, IssueCrossZone)
	require.NotContains(t, permissions, ReadAudit)
}

func TestGetEffectivePermissionsIsIdempotent(t *testing.T) {
	first := GetEffectivePermissions(Admin)
	second := GetEffectivePermissions(Admin)

	require.Equal(t, first, second)
}

func TestInvalidRoleIsRejected(t *testing.T) {
	require.False(t, IsRoleValid(Role("Unknown")))
}

func TestFirstNonceUseSucceeds(t *testing.T) {
	ctx, _ := newMockContext("tx-1", 1_700_000_000)

	require.NoError(t, validateNonce(ctx, "actor-1", "nonce-1"))
}

func TestReplayNonceReturnsReplayDetected(t *testing.T) {
	ctx, _ := newMockContext("tx-1", 1_700_000_000)

	require.NoError(t, validateNonce(ctx, "actor-1", "nonce-1"))
	err := validateNonce(ctx, "actor-1", "nonce-1")

	require.ErrorContains(t, err, "replay detected")
}

func TestAuditKeyFormatIsCorrect(t *testing.T) {
	ctx, stub := newMockContext("tx-audit-1", 1_700_000_000)

	key, err := writeAuditEntry(ctx, AuditEntry{ActorID: "actor-1", Action: "read", Resource: "zone-1", Decision: "allow"})

	require.NoError(t, err)
	require.Equal(t, "audit:tx-audit-1", key)
	require.Contains(t, string(stub.state[key]), "tx-audit-1")
}

func TestExpiredRoleIsDetected(t *testing.T) {
	ctx, _ := newMockContext("tx-expired-1", 1_700_000_000)

	err := checkRoleExpiration(ctx, RoleAssignment{SubjectID: "actor-1", Role: Farmer, ExpiresAt: 1_600_000_000})

	require.ErrorContains(t, err, "expired")
}

func TestAssignRole(t *testing.T) {
	ctx, stub := newMockContext("tx-assign", 1_700_000_000)
	s := &SmartContract{}

	err := s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign")

	require.NoError(t, err)
	assignment := decodeRole(t, stub, "farmer-1")
	require.Equal(t, Farmer, assignment.Role)
	require.Equal(t, []string{"North"}, assignment.Zones)
	require.Equal(t, int64(1_800_000_000), assignment.ExpiresAt)
}

func TestAssignRoleRejectsInvalidZoneAndPastExpiry(t *testing.T) {
	ctx, _ := newMockContext("tx-assign-bad-zone", 1_700_000_000)
	s := &SmartContract{}

	err := s.AssignRole(ctx, "sensor-1", string(Sensor), "Central", futureISO(1_800_000_000), "n-zone")
	require.ErrorContains(t, err, "invalid zone")

	ctx, _ = newMockContext("tx-assign-past", 1_700_000_000)
	err = s.AssignRole(ctx, "sensor-1", string(Sensor), "North", futureISO(1_600_000_000), "n-past")
	require.ErrorContains(t, err, "expiry in the past")
}

func TestRevokeRole(t *testing.T) {
	ctx, stub := newMockContext("tx-revoke-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setTx("tx-revoke", 1_700_000_001)

	err := s.RevokeRole(ctx, "farmer-1", "n-revoke")

	require.NoError(t, err)
	require.Equal(t, []byte(nil), stub.state[roleKey("farmer-1")])
}

func TestRenewRole(t *testing.T) {
	ctx, stub := newMockContext("tx-renew-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setTx("tx-renew", 1_700_000_001)

	err := s.RenewRole(ctx, "farmer-1", futureISO(1_900_000_000), "n-renew")

	require.NoError(t, err)
	require.Equal(t, int64(1_900_000_000), decodeRole(t, stub, "farmer-1").ExpiresAt)
}

func TestCheckAccessPermissionGrantAndDeny(t *testing.T) {
	ctx, stub := newMockContext("tx-perm-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setCaller(t, "farmer-1", Farmer, "North", 101)
	stub.setTx("tx-perm-grant", 1_700_000_001)

	ok, err := s.CheckAccess(ctx, "farmer-1", string(WriteSensor), "North", "")
	require.NoError(t, err)
	require.True(t, ok)

	stub.setTx("tx-perm-deny", 1_700_000_002)
	ok, err = s.CheckAccess(ctx, "farmer-1", string(AdminAll), "North", "")
	require.NoError(t, err)
	require.False(t, ok)
}

func TestZoneViolationDenied(t *testing.T) {
	ctx, stub := newMockContext("tx-zone-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setCaller(t, "farmer-1", Farmer, "North", 102)
	stub.setTx("tx-zone-deny", 1_700_000_001)

	ok, err := s.CheckAccess(ctx, "farmer-1", string(ControlZone), "South", "")

	require.NoError(t, err)
	require.False(t, ok)
}

func TestCrossZoneTokenValidExpiredRevoked(t *testing.T) {
	ctx, stub := newMockContext("tx-czt-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_900_000_000), "n-assign"))
	stub.setCaller(t, "agro-1", Agronomist, "North", 201)
	stub.setTx("tx-czt-issue", 1_700_000_001)
	tokenID, err := s.IssueCrossZoneToken(ctx, "farmer-1", "South", futureISO(1_700_000_010), "n-issue")
	require.NoError(t, err)
	require.True(t, tokenID != "")

	stub.setCaller(t, "farmer-1", Farmer, "North", 202)
	stub.setTx("tx-czt-valid", 1_700_000_002)
	ok, err := s.CheckAccess(ctx, "farmer-1", string(ControlZone), "South", tokenID)
	require.NoError(t, err)
	require.True(t, ok)

	stub.setTx("tx-czt-expired", 1_700_000_011)
	ok, err = s.CheckAccess(ctx, "farmer-1", string(ControlZone), "South", tokenID)
	require.NoError(t, err)
	require.False(t, ok)

	stub.setCaller(t, "agro-1", Agronomist, "North", 201)
	stub.setTx("tx-czt-issue-2", 1_700_000_012)
	tokenID, err = s.IssueCrossZoneToken(ctx, "farmer-1", "South", futureISO(1_800_000_000), "n-issue-2")
	require.NoError(t, err)
	stub.setTx("tx-czt-revoke", 1_700_000_013)
	require.NoError(t, s.RevokeCrossZoneToken(ctx, tokenID, "n-revoke-token"))
	stub.setCaller(t, "farmer-1", Farmer, "North", 202)
	stub.setTx("tx-czt-revoked-check", 1_700_000_014)
	ok, err = s.CheckAccess(ctx, "farmer-1", string(ControlZone), "South", tokenID)
	require.NoError(t, err)
	require.False(t, ok)
}

func TestCertificateRevocation(t *testing.T) {
	ctx, stub := newMockContext("tx-crl-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setCaller(t, "farmer-1", Farmer, "North", 255)
	stub.state["crl:ff"] = []byte("revoked")
	stub.setTx("tx-crl-check", 1_700_000_001)

	ok, err := s.CheckAccess(ctx, "farmer-1", string(WriteSensor), "North", "")

	require.NoError(t, err)
	require.False(t, ok)
}

// buildTestCRL creates a minimal, syntactically valid CRL (parseable by
// x509.ParseRevocationList) revoking exactly the given serials. Signature
// validity is irrelevant here: UpdateCRL parses the CRL to recover serial
// numbers, exactly as the deployed operational workflow's fabric-ca-client
// output would be parsed, and does not check who signed it (revocation
// authority is enforced separately, by requiring the Admin role).
func buildTestCRL(t *testing.T, serials ...int64) string {
	t.Helper()
	key, err := rsa.GenerateKey(rand.Reader, 1024)
	require.NoError(t, err)
	issuer := &x509.Certificate{
		SerialNumber: big.NewInt(1),
		Subject:      pkix.Name{CommonName: "test-ca"},
		NotBefore:    time.Unix(1_600_000_000, 0),
		NotAfter:     time.Unix(1_900_000_000, 0),
		KeyUsage:     x509.KeyUsageCRLSign | x509.KeyUsageCertSign,
		IsCA:         true,
	}
	issuerDER, err := x509.CreateCertificate(rand.Reader, issuer, issuer, &key.PublicKey, key)
	require.NoError(t, err)
	issuerCert, err := x509.ParseCertificate(issuerDER)
	require.NoError(t, err)

	entries := make([]x509.RevocationListEntry, 0, len(serials))
	for _, serial := range serials {
		entries = append(entries, x509.RevocationListEntry{
			SerialNumber:   big.NewInt(serial),
			RevocationTime: time.Unix(1_700_000_000, 0),
		})
	}
	template := &x509.RevocationList{
		Number:                    big.NewInt(1),
		ThisUpdate:                time.Unix(1_700_000_000, 0),
		NextUpdate:                time.Unix(1_700_100_000, 0),
		RevokedCertificateEntries: entries,
	}
	crlDER, err := x509.CreateRevocationList(rand.Reader, template, issuerCert, key)
	require.NoError(t, err)
	return base64.StdEncoding.EncodeToString(crlDER)
}

func TestUpdateCRLWritesRevocationEntriesAndDeniesCheckAccess(t *testing.T) {
	ctx, stub := newMockContext("tx-crl-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setCaller(t, "admin", Admin, "North", 1)
	stub.setTx("tx-update-crl", 1_700_000_001)

	crlB64 := buildTestCRL(t, 255)
	count, err := s.UpdateCRL(ctx, crlB64, "episode-2025-09-30-usr-0048", "n-crl")
	require.NoError(t, err)
	require.Equal(t, 1, count)
	require.True(t, stub.state["crl:ff"] != nil, "UpdateCRL must write a crl: entry for the revoked serial")

	stub.setCaller(t, "farmer-1", Farmer, "North", 255)
	stub.setTx("tx-crl-check", 1_700_000_002)
	ok, err := s.CheckAccess(ctx, "farmer-1", string(WriteSensor), "North", "")
	require.NoError(t, err)
	require.False(t, ok, "CheckAccess must deny a caller whose certificate serial UpdateCRL just revoked")
}

func TestUpdateCRLRequiresAdmin(t *testing.T) {
	ctx, stub := newMockContext("tx-crl-nonadmin", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-1", string(Farmer), "North", futureISO(1_800_000_000), "n-assign0"))
	stub.setCaller(t, "farmer-1", Farmer, "North", 101)
	stub.setTx("tx-crl-nonadmin-2", 1_700_000_001)

	_, err := s.UpdateCRL(ctx, buildTestCRL(t, 42), "episode-x", "n-crl-2")
	require.ErrorContains(t, err, "admin role required")
}

func TestUpdateCRLRecordsEpisodeIDOnAuditEntry(t *testing.T) {
	ctx, stub := newMockContext("tx-crl-assign2", 1_700_000_000)
	s := &SmartContract{}
	stub.setCaller(t, "admin", Admin, "North", 1)
	stub.setTx("tx-update-crl2", 1_700_000_001)

	_, err := s.UpdateCRL(ctx, buildTestCRL(t, 7), "episode-shared-token", "n-crl-3")
	require.NoError(t, err)

	raw, ok := stub.state[auditKey("tx-update-crl2")]
	require.True(t, ok)
	var entry AuditEntry
	require.NoError(t, json.Unmarshal(raw, &entry))
	require.Equal(t, "episode-shared-token", entry.EpisodeID)
	require.Equal(t, "UpdateCRL", entry.Action)
}

func TestRevokeRoleRecordsEpisodeIDOnAuditEntry(t *testing.T) {
	ctx, stub := newMockContext("tx-revoke-assign2", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "farmer-2", string(Farmer), "North", futureISO(1_800_000_000), "n-assign2"))
	stub.setTx("tx-revoke2", 1_700_000_001)

	require.NoError(t, s.RevokeRole(ctx, "farmer-2", "episode-shared-token-2"))

	raw, ok := stub.state[auditKey("tx-revoke2")]
	require.True(t, ok)
	var entry AuditEntry
	require.NoError(t, json.Unmarshal(raw, &entry))
	require.Equal(t, "episode-shared-token-2", entry.EpisodeID)
}

func TestPruneNonces(t *testing.T) {
	ctx, stub := newMockContext("tx-old", 1_600_000_000)
	require.NoError(t, validateNonce(ctx, "user-1", "old"))
	stub.setTx("tx-new", 1_700_000_000)
	require.NoError(t, validateNonce(ctx, "user-1", "new"))
	stub.setCaller(t, "admin", Admin, "North", 1)
	stub.setTx("tx-prune", 1_700_000_001)
	s := &SmartContract{}

	count, err := s.PruneNonces(ctx, 1_650_000_000, "prune")

	require.NoError(t, err)
	require.Equal(t, 1, count)
	require.Equal(t, []byte(nil), stub.state[nonceKey("user-1", "old")])
	require.True(t, stub.state[nonceKey("user-1", "new")] != nil)
}

func TestWriteSensorData(t *testing.T) {
	ctx, stub := newMockContext("tx-sensor-assign", 1_700_000_000)
	s := &SmartContract{}
	require.NoError(t, s.AssignRole(ctx, "sensor-1", string(Sensor), "North", futureISO(1_800_000_000), "n-assign"))
	stub.setCaller(t, "sensor-1", Sensor, "North", 301)
	stub.setTx("tx-sensor-write", 1_700_000_123)

	telemetry, err := s.WriteSensorData(ctx, "device-1", `{"moisture":42}`, "North", "n-write")

	require.NoError(t, err)
	require.Equal(t, `{"moisture":42}`, string(stub.state["sensor:device-1:1700000123000000000"]))
	require.True(t, telemetry != nil)
	require.True(t, telemetry.RbacOverheadMs >= 0.0)
}

func TestPrivilegeEscalationRejected(t *testing.T) {
	ctx, stub := newMockContext("tx-priv-assign", 1_700_000_000)
	stub.setCaller(t, "sensor-1", Sensor, "North", 401)
	s := &SmartContract{}

	err := s.AssignRole(ctx, "sensor-1", string(Admin), "North", futureISO(1_800_000_000), "n-escalate")
	require.ErrorContains(t, err, "unauthorized")

	stub.setTx("tx-priv-token", 1_700_000_001)
	_, err = s.IssueCrossZoneToken(ctx, "sensor-1", "South", futureISO(1_800_000_000), "n-token")
	require.ErrorContains(t, err, "unauthorized")
}

func TestGetAuditLogLimitedTo1000(t *testing.T) {
	ctx, stub := newMockContext("tx-audit-base", 1_700_000_000)
	for i := 0; i < 1005; i++ {
		stub.setTx("tx-audit-"+big.NewInt(int64(i)).String(), 1_700_000_000+int64(i))
		_, err := writeAuditEntry(ctx, AuditEntry{ActorID: "admin", Action: "test", Resource: "r", Decision: "GRANT"})
		require.NoError(t, err)
	}
	s := &SmartContract{}

	entries, err := s.GetAuditLog(ctx)

	require.NoError(t, err)
	require.Equal(t, 1000, len(entries))
}
