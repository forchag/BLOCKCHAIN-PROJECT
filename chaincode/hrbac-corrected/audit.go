package main

import (
	"encoding/json"
	"fmt"
	"time"

	"github.com/hyperledger/fabric-contract-api-go/contractapi"
)

// AuditEntry records a deterministic authorization or administration event.
//
// EpisodeID is new in this corrected package. It closes part of the
// revocation-observability gap the manuscript's postmortem describes: the
// historical trace has no key linking CRL publication, gossip and cache
// invalidation into one revocation episode. RevokeRole and UpdateCRL both
// stamp EpisodeID with the caller-supplied correlation token (in practice,
// the same value scripts/revoke-cert.sh and scripts/generate-crl.sh now
// share for one revocation request), so an operator or a future trace
// collector can join the chaincode-side audit trail across both calls, and
// a gateway that logs the same token when it invalidates its policy cache
// (gateway/policy_cache.py) extends that join across the full pipeline.
// This does not, and cannot, resolve episodes in the historical trace
// already collected; it gives the next deployment a real key to collect.
type AuditEntry struct {
	TxID      string `json:"txId"`
	ActorID   string `json:"actorId"`
	Action    string `json:"action"`
	Resource  string `json:"resource"`
	Decision  string `json:"decision"`
	Reason    string `json:"reason,omitempty"`
	EpisodeID string `json:"episodeId,omitempty"`
	Timestamp int64  `json:"timestamp"`
}

func auditKey(txID string) string {
	return auditKeyPrefix + txID
}

func auditKeyWithSequence(txID string, sequence int) string {
	if sequence == 0 {
		return auditKey(txID)
	}
	return fmt.Sprintf("%s%s:%d", auditKeyPrefix, txID, sequence)
}

func writeAuditEntry(ctx contractapi.TransactionContextInterface, entry AuditEntry) (string, error) {
	stub := ctx.GetStub()
	txTimestamp, err := stub.GetTxTimestamp()
	if err != nil {
		return "", fmt.Errorf("failed to read transaction timestamp: %w", err)
	}

	entry.TxID = stub.GetTxID()
	entry.Timestamp = time.Unix(txTimestamp.Seconds, int64(txTimestamp.Nanos)).UTC().Unix()

	payload, err := json.Marshal(entry)
	if err != nil {
		return "", fmt.Errorf("failed to marshal audit entry: %w", err)
	}

	keys, err := getStringIndex(ctx, auditIndexKey)
	if err != nil {
		return "", err
	}

	key := auditKeyWithSequence(entry.TxID, 0)
	for sequence := 0; ; sequence++ {
		key = auditKeyWithSequence(entry.TxID, sequence)
		existing, err := stub.GetState(key)
		if err != nil {
			return "", fmt.Errorf("failed to check audit entry key: %w", err)
		}
		if existing == nil {
			break
		}
	}
	if err := stub.PutState(key, payload); err != nil {
		return "", fmt.Errorf("failed to write audit entry: %w", err)
	}
	keys = append(keys, key)
	if err := putStringIndex(ctx, auditIndexKey, keys); err != nil {
		return "", err
	}
	return key, nil
}
