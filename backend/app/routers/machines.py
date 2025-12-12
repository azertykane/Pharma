# adminpharma/app/routers/machines.py
from fastapi import APIRouter, Depends, HTTPException, Request, Body, Header
from sqlmodel import select
from datetime import datetime
from typing import Optional
from ..database import get_session
from ..models import Machine, BlockLog
from sqlmodel import Session

router = APIRouter()

@router.post("/report", summary="Report machine (create/update)")
def report_machine(
    payload: dict = Body(...),
    x_admin: Optional[str] = Header(None),
    session: Session = Depends(get_session),
):
    """
    Payload example:
    {
      "device_name": "PC-1",
      "mac_address": "AA:BB:CC:DD:EE:FF",
      "owner": "Pharmacie X",
      "ip": "1.2.3.4",
      "version": "1.2.3"
    }
    """
    mac = payload.get("mac_address") or payload.get("mac")
    if not mac:
        raise HTTPException(400, "mac_address required")

    mac = mac.strip().lower()
    machine = session.exec(select(Machine).where(Machine.mac_address == mac)).first()
    now = datetime.utcnow()
    if not machine:
        machine = Machine(
            device_name=payload.get("device_name", "unknown"),
            mac_address=mac,
            owner=payload.get("owner"),
            status="active",
            last_seen=now,
        )
        session.add(machine)
        session.commit()
        session.refresh(machine)
        action = "created"
    else:
        machine.device_name = payload.get("device_name", machine.device_name)
        machine.owner = payload.get("owner", machine.owner)
        machine.last_seen = now
        # don't auto-unblock here; admin decides
        session.add(machine)
        session.commit()
        action = "updated"

    return {
        "ok": True,
        "action": action,
        "machine": {
            "id": machine.id,
            "device_name": machine.device_name,
            "mac_address": machine.mac_address,
            "owner": machine.owner,
            "status": machine.status,
            "last_seen": machine.last_seen.isoformat() if machine.last_seen else None,
        },
    }

@router.get("/check", summary="Check machine status by mac")
def check_machine(mac: str, session: Session = Depends(get_session)):
    mac = mac.strip().lower()
    machine = session.exec(select(Machine).where(Machine.mac_address == mac)).first()
    if not machine:
        return {"exists": False, "blocked": False, "status": "unknown"}
    return {
        "exists": True,
        "blocked": machine.status == "blocked",
        "status": machine.status,
        "last_seen": machine.last_seen.isoformat() if machine.last_seen else None,
        "id": machine.id,
    }

@router.get("/", summary="List machines")
def list_machines(session: Session = Depends(get_session)):
    machines = session.exec(select(Machine)).all()
    return machines

@router.post("/{machine_id}/block", summary="Block a machine")
def block_machine(
    machine_id: int,
    reason: Optional[str] = Body(None),
    x_admin: Optional[str] = Header(None),
    session: Session = Depends(get_session),
):
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(404, "Machine not found")
    prev = machine.status
    machine.status = "blocked"
    machine.last_seen = datetime.utcnow()
    session.add(machine)
    log = BlockLog(machine_id=machine_id, action="block", by_user=(x_admin or "admin"), timestamp=datetime.utcnow())
    session.add(log)
    session.commit()
    return {"ok": True, "previous": prev, "now": machine.status}

@router.post("/{machine_id}/unblock", summary="Unblock a machine")
def unblock_machine(
    machine_id: int,
    reason: Optional[str] = Body(None),
    x_admin: Optional[str] = Header(None),
    session: Session = Depends(get_session),
):
    machine = session.get(Machine, machine_id)
    if not machine:
        raise HTTPException(404, "Machine not found")
    prev = machine.status
    machine.status = "active"
    machine.last_seen = datetime.utcnow()
    session.add(machine)
    log = BlockLog(machine_id=machine_id, action="unblock", by_user=(x_admin or "admin"), timestamp=datetime.utcnow())
    session.add(log)
    session.commit()
    return {"ok": True, "previous": prev, "now": machine.status}

@router.get("/{machine_id}/logs", summary="Get block/unblock logs for a machine")
def get_machine_logs(machine_id: int, session: Session = Depends(get_session)):
    logs = session.exec(select(BlockLog).where(BlockLog.machine_id == machine_id).order_by(BlockLog.timestamp.desc())).all()
    return logs
