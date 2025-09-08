from contextlib import contextmanager
from .db import SessionLocal
@contextmanager
def uow():
    s=SessionLocal()
    try:
        yield s; s.commit()
    except Exception:
        s.rollback(); raise
    finally:
        s.close()
