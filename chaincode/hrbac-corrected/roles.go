package main

// This file is the corrected role hierarchy released alongside the
// historical, unpatched chaincode/hrbac package. It fixes two defects
// documented in the manuscript's implementation postmortem.
//
// First, the auditor-separation defect: the deployed hierarchy placed
// Certifier on the human inheritance chain (SupplyChain -> Certifier ->
// Agronomist -> Farmer -> Admin) rather than beside it, so Agronomist and
// Farmer inherited ReadAudit, and Certifier itself held ReadZone, letting
// an auditor read raw zone sensor data rather than only compliance/audit
// records. The fix removes Certifier from Agronomist's and Farmer's
// ancestor sets and drops ReadZone from Certifier's direct grants,
// replacing it with a direct ReadZone grant on Agronomist and Farmer so
// neither loses the zone visibility the design intends them to have.
//
// Second, the Agronomist-actuation defect, found in review of an earlier
// draft of this correction: Agronomist retained a direct ControlZone
// grant, contradicting the introduction's "history but no actuation
// rights" description of the role. ControlZone is removed from
// Agronomist's direct grants here; Farmer, which no longer inherits it
// from Agronomist once Agronomist's own grant is removed, receives its
// own direct ControlZone grant so operational control stays where the
// design intends it. TestAgronomistCannotControlZone in contract_test.go
// is the regression test for this specific defect.
//
// Every other effective permission is unchanged: this is a minimal patch
// to the two defects above, not a redesign of the role hierarchy. See
// ROLES_DIFF.patch for the exact diff against chaincode/hrbac/roles.go
// and the manuscript's deployed-vs-corrected policy table.

// Role identifies an HRBAC actor role.
type Role string

const (
	Admin       Role = "Admin"
	Gateway     Role = "Gateway"
	Farmer      Role = "Farmer"
	Agronomist  Role = "Agronomist"
	Certifier   Role = "Certifier"
	SupplyChain Role = "SupplyChain"
	Sensor      Role = "Sensor"
)

// Permission identifies an action allowed by an effective role.
type Permission string

const (
	ReadOwn        Permission = "ReadOwn"
	ReadZone       Permission = "ReadZone"
	ReadAll        Permission = "ReadAll"
	WriteSensor    Permission = "WriteSensor"
	ControlZone    Permission = "ControlZone"
	ControlAll     Permission = "ControlAll"
	ReadAudit      Permission = "ReadAudit"
	ManageRoles    Permission = "ManageRoles"
	IssueCrossZone Permission = "IssueCrossZone"
	AdminAll       Permission = "AdminAll"
)

var rolePermissions = map[Role][]Permission{
	SupplyChain: {ReadOwn},
	Certifier:   {ReadAudit},
	Agronomist:  {ReadZone, IssueCrossZone},
	Farmer:      {WriteSensor, ReadZone, ControlZone},
	Sensor:      {WriteSensor},
	Gateway:     {ReadZone, ControlZone},
	Admin:       {ReadAll, ControlAll, ManageRoles, AdminAll},
}

var roleAncestors = map[Role][]Role{
	SupplyChain: {SupplyChain},
	Certifier:   {Certifier, SupplyChain},
	Agronomist:  {Agronomist, SupplyChain},
	Farmer:      {Farmer, Agronomist, SupplyChain},
	Sensor:      {Sensor},
	Gateway:     {Gateway, Sensor},
	Admin:       {Admin, Farmer, Agronomist, Certifier, SupplyChain, Gateway, Sensor},
}

var validRoles = map[Role]struct{}{
	Admin: {}, Gateway: {}, Farmer: {}, Agronomist: {}, Certifier: {}, SupplyChain: {}, Sensor: {},
}

// GetEffectivePermissions returns permissions inherited by r in deterministic order.
func GetEffectivePermissions(r Role) []Permission {
	ancestors, ok := roleAncestors[r]
	if !ok {
		return nil
	}

	seen := make(map[Permission]struct{})
	permissions := make([]Permission, 0)
	for _, role := range ancestors {
		for _, permission := range rolePermissions[role] {
			if _, exists := seen[permission]; exists {
				continue
			}
			seen[permission] = struct{}{}
			permissions = append(permissions, permission)
		}
	}
	return permissions
}

// IsRoleValid reports whether r is one of the supported HRBAC roles.
func IsRoleValid(r Role) bool {
	_, ok := validRoles[r]
	return ok
}
