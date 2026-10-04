from conftest import CONTRACT


ASSUMPTIONS = [
    "The supplier can deliver replacement parts within fourteen days.",
    "The existing support team can absorb the migration workload.",
]
RISKS = ["A delivery delay could extend the maintenance window."]


def setup_case(vm, deploy, owner, auditor):
    vm.sender = owner
    contract = deploy(CONTRACT)
    contract.seal_decision(
        "migration-7", "0x" + auditor.hex(), "Support platform migration",
        "The team must choose whether to migrate the support platform before the annual renewal while preserving customer response coverage.",
        ASSUMPTIONS, "Choose the option that preserves service coverage and can be reversed within thirty days.",
        "Migrate in two stages with a rollback checkpoint.",
        "Renew the existing platform for one year.", RISKS,
    )
    return contract


def mock_audit(vm, process=True, favorable=False, unsupported="[]", invalidated="[1]"):
    vm.mock_llm(
        r".*Hindsight Firewall audit.*",
        '{"process_sound":' + str(process).lower() + ',"outcome_favorable":' + str(favorable).lower() + ',"unsupported_indexes":' + unsupported + ',"invalidated_later_indexes":' + invalidated + '}',
    )


def test_sound_process_is_separate_from_bad_outcome(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = setup_case(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    mock_audit(direct_vm)
    contract.audit_decision("migration-7", "The migration finished, but the support team became overloaded after an unexpected product recall.", ["Staffing was adequate at approval time.", "The later recall doubled ticket volume after approval."])
    result = contract.get_case("migration-7")
    assert result["verdict"] == "SOUND_BAD_OUTCOME"
    assert result["invalidated_later_indexes"] == [1]


def test_only_designated_auditor_can_score(direct_vm, direct_deploy, direct_alice, direct_bob, direct_charlie):
    contract = setup_case(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_charlie
    mock_audit(direct_vm)
    with direct_vm.expect_revert("designated auditor"):
        contract.audit_decision("migration-7", "A sufficiently detailed later outcome for the audit record.", ["A sufficiently detailed later evidence item."])


def test_validator_rejects_forged_assumption_classification(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = setup_case(direct_vm, direct_deploy, direct_alice, direct_bob)
    mock_audit(direct_vm)
    case = contract.cases["MIGRATION-7"]
    result = contract._judge(case, "The migration finished but a later recall overloaded support.", ["The recall occurred after approval and doubled volume."])
    assert direct_vm.run_validator(leader_result=result) is True
    forged = dict(result)
    forged["unsupported_indexes"] = [0]
    forged["process_sound"] = False
    assert direct_vm.run_validator(leader_result=forged) is False


def test_owner_gets_one_evidence_bound_challenge(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = setup_case(direct_vm, direct_deploy, direct_alice, direct_bob)
    direct_vm.sender = direct_bob
    mock_audit(direct_vm, process=False, favorable=True, unsupported="[0]", invalidated="[]")
    contract.audit_decision("migration-7", "The migration succeeded without interruption despite late parts.", ["The supplier had no written delivery commitment at approval time."])
    direct_vm.clear_mocks()
    direct_vm.sender = direct_alice
    mock_audit(direct_vm, process=True, favorable=True, unsupported="[]", invalidated="[]")
    contract.challenge_audit("migration-7", ["A signed delivery schedule existed in the sealed procurement packet."])
    result = contract.get_case("migration-7")
    assert result["state"] == "REVISED"
    assert result["verdict"] == "SOUND_GOOD_OUTCOME"
    with direct_vm.expect_revert("unchallenged audit"):
        contract.challenge_audit("migration-7", ["A second challenge must not be accepted."])


def test_duplicate_case_is_rejected(direct_vm, direct_deploy, direct_alice, direct_bob):
    contract = setup_case(direct_vm, direct_deploy, direct_alice, direct_bob)
    with direct_vm.expect_revert("unique case"):
        contract.seal_decision("migration-7", "0x" + direct_bob.hex(), "Duplicate case", "A context long enough to pass the deterministic content floor for this duplicate.", ASSUMPTIONS, "A detailed decision rule for duplicate testing.", "A sufficiently detailed chosen action.", "A sufficiently detailed alternative action.", RISKS)
