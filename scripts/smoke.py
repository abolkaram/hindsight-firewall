"""Run a two-wallet StudioNet lifecycle against an existing deployment."""
import json
import os
import time

from genlayer_py import create_account, create_client
from genlayer_py.chains import studionet


ADDRESS = "0x81f8f50Bc0Cf53F83979d67bE4692242d1E7EC25"


def client(variable):
    key = os.environ.get(variable, "").strip()
    if not key:
        raise SystemExit(variable + " is required")
    account = create_account(account_private_key=key)
    return account, create_client(chain=studionet, account=account)


def send(api, method, args):
    tx = api.write_contract(address=ADDRESS, function_name=method, args=args)
    receipt = api.wait_for_transaction_receipt(
        transaction_hash=tx, wait_until="finalized", retries=180,
        interval=5000, full_transaction=True,
    )
    leader = (receipt.get("consensus_data", {}).get("leader_receipt") or [{}])[0]
    if receipt.get("result_name") != "MAJORITY_AGREE" or leader.get("execution_result") != "SUCCESS":
        raise RuntimeError(json.dumps(receipt, default=str))
    return str(tx)


owner, owner_api = client("OWNER_KEY")
auditor, auditor_api = client("AUDITOR_KEY")
case_id = "HF-LIVE-" + str(int(time.time()))
transactions = {}
transactions["seal"] = send(owner_api, "seal_decision", [
    case_id, auditor.address, "Staged support migration",
    "A service team must choose a migration path before its annual platform renewal while keeping response coverage and a practical rollback route.",
    ["The supplier committed to deliver parts within fourteen days.", "The support team can absorb the planned two-stage migration workload."],
    "Prefer the reversible path that preserves customer coverage and has a documented rollback checkpoint.",
    "Migrate in two stages with a rollback review between stages.",
    "Renew the current platform for one year and defer migration.",
    ["A later demand spike could overload the support team."],
])
transactions["audit"] = send(auditor_api, "audit_decision", [
    case_id,
    "The migration completed, but an unrelated product recall doubled support demand after approval and caused a temporary response delay.",
    ["The signed supplier schedule existed before approval.", "The product recall was announced only after the migration decision."],
])
state = owner_api.read_contract(address=ADDRESS, function_name="get_case", args=[case_id])
if state["state"] != "AUDITED" or not state["verdict"]:
    raise RuntimeError(json.dumps(state, default=str))
print(json.dumps({
    "caseId": case_id, "transactions": transactions,
    "state": state, "walletDisclosure": "Both wallets and evidence are operator-controlled fixtures."
}, indent=2, default=str))

