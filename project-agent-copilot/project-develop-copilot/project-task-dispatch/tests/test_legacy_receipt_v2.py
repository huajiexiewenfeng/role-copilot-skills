from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import legacy_receipt


class LegacyReceiptV2Test(unittest.TestCase):
    def test_completed_receipt_maps_only_to_submitted_candidate(self) -> None:
        receipt = legacy_receipt.parse_receipt(
            {
                "schemaVersion": 1, "taskId": "T-a", "requestedState": "COMPLETED",
                "summary": "done", "evidenceRefs": ["thread:old"], "nextStep": "review",
                "blocked": False, "needsParentDecision": False, "blocker": None,
            }
        )
        candidate = legacy_receipt.completed_receipt_to_delivery_candidate(receipt, "2026-08-23T15:00:00+08:00")
        self.assertEqual(candidate["targetState"], "SUBMITTED")
        self.assertNotEqual(candidate["targetState"], "APPROVED")


if __name__ == "__main__":
    unittest.main()
