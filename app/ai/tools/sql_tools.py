from sqlalchemy.orm import Session

def run_sql(db: Session, sql: str) -> list[dict]:
    try:
        res = db.execute(sql)
        cols = res.keys()
        return [dict(zip(cols, row)) for row in res.fetchall()]
    except Exception:
        return []
