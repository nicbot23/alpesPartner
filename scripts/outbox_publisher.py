#!/usr/bin/env python
"""Simple outbox publisher.
- Lee eventos no publicados en orden de occurred_at
- Simula envio (imprime JSON line)
- Marca como publicados
Uso:
  python scripts/outbox_publisher.py --batch-size 50 --dry-run
Variables env:
  DATABASE_URL (si no usa la definida por seedwork)
"""
from __future__ import annotations
import argparse, json, sys, time
from contextlib import contextmanager
from dataclasses import asdict
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from alpespartner.seedwork.infraestructura.db import SessionLocal
from alpespartner.seedwork.infraestructura.outbox.modelos import OutboxEvent

@contextmanager
def session_scope():
    session:Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

def fetch_batch(session:Session, batch_size:int):
    stmt = select(OutboxEvent).where(OutboxEvent.published==False).order_by(OutboxEvent.occurred_at).limit(batch_size)
    return list(session.scalars(stmt))

def mark_published(session:Session, ids):
    if not ids: return 0
    stmt = update(OutboxEvent).where(OutboxEvent.id.in_(ids)).values(published=True)
    res = session.execute(stmt)
    return res.rowcount or 0

def serialize(evt:OutboxEvent):
    return {
        'id': evt.id,
        'aggregate_type': evt.aggregate_type,
        'aggregate_id': evt.aggregate_id,
        'event_type': evt.event_type,
        'payload': evt.payload,
        'occurred_at': evt.occurred_at.isoformat() if evt.occurred_at else None,
        'correlation_id': evt.correlation_id,
        'causation_id': evt.causation_id
    }

def run(batch_size:int, dry_run:bool, loop:bool, sleep_seconds:float):
    processed_total=0
    while True:
        with session_scope() as session:
            batch = fetch_batch(session, batch_size)
            if not batch:
                if not loop:
                    print(f"No pending events. Total processed={processed_total}")
                    return 0
                else:
                    time.sleep(sleep_seconds)
                    continue
            ids=[e.id for e in batch]
            for evt in batch:
                line=json.dumps(serialize(evt), ensure_ascii=False)
                print(line)
            if dry_run:
                print(f"[DRY-RUN] Would mark {len(ids)} events published")
            else:
                updated = mark_published(session, ids)
                print(f"[INFO] Marked {updated} events as published")
                processed_total += updated
        if not loop:
            return 0
        time.sleep(sleep_seconds)

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch-size', type=int, default=50)
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--loop', action='store_true', help='Mantener proceso corriendo (polling)')
    parser.add_argument('--sleep', type=float, default=5.0, help='Segundos entre polls en modo loop')
    args = parser.parse_args(argv)
    return run(args.batch_size, args.dry_run, args.loop, args.sleep)

if __name__ == '__main__':
    raise SystemExit(main())
