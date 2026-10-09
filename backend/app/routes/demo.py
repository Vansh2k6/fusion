# Purpose: Define endpoints for local chain demo execution, receipt/balance observation, and chain reset.
import json
from fastapi import APIRouter, HTTPException
from typing import List
from app.monitoring.observer import run_attack_defense_demo, reset_local_chain
from app.schemas import DemoRunResponse, TxReceipt, BalanceDelta, IncidentAlert
from app.database import get_connection

router = APIRouter(prefix="/api/demo", tags=["demo"])

@router.post("/runs", response_model=DemoRunResponse)
def execute_demo_run():
    """Trigger the live Anvil attack/defense simulation."""
    res, error = run_attack_defense_demo()
    if error:
        raise HTTPException(status_code=400, detail=error)
    return res

@router.get("/runs/{run_id}", response_model=DemoRunResponse)
def get_demo_run(run_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM demo_runs WHERE id = ?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Demo run not found.")

    txs = [TxReceipt(**t) for t in json.loads(row["transactions_json"])]
    bals = [BalanceDelta(**b) for b in json.loads(row["balances_json"])]
    alert = IncidentAlert(**json.loads(row["alert_json"])) if row["alert_json"] else None

    return DemoRunResponse(
        id=row["id"],
        status=row["status"],
        rpc_url=row["rpc_url"],
        chain_id=row["chain_id"],
        original_vault=row["original_vault"],
        protected_vault=row["protected_vault"],
        attacker=row["attacker"],
        normal_user=row["normal_user"],
        transactions=txs,
        balances=bals,
        alert=alert,
        is_historical=bool(row["is_historical"]),
        created_at=row["created_at"],
        logs=row["logs"]
    )

@router.get("/runs", response_model=List[DemoRunResponse])
def list_demo_runs():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM demo_runs ORDER BY created_at DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()

    res = []
    for row in rows:
        txs = [TxReceipt(**t) for t in json.loads(row["transactions_json"])]
        bals = [BalanceDelta(**b) for b in json.loads(row["balances_json"])]
        alert = IncidentAlert(**json.loads(row["alert_json"])) if row["alert_json"] else None
        res.append(DemoRunResponse(
            id=row["id"],
            status=row["status"],
            rpc_url=row["rpc_url"],
            chain_id=row["chain_id"],
            original_vault=row["original_vault"],
            protected_vault=row["protected_vault"],
            attacker=row["attacker"],
            normal_user=row["normal_user"],
            transactions=txs,
            balances=bals,
            alert=alert,
            is_historical=bool(row["is_historical"]),
            created_at=row["created_at"],
            logs=row["logs"]
        ))
    return res

@router.post("/reset")
def reset_demo():
    """Reset local chain and mark earlier evidence as historical."""
    try:
        return reset_local_chain()
    except RuntimeError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
