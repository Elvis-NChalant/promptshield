# backend/app.py
import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from detection_engine import compute_risk, sanitize_text
from ppa import wrap_prompt
from storage import SessionLocal, init_db, AttackLog
from models import (
    AnalyzeRequest,
    AnalyzeResponse,
    LayerScores,
    AttackHistoryResponse,
    AttackLogItem,
)

app = FastAPI(title="PromptShield")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

init_db()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    start = time.perf_counter()

    raw_prompt = req.prompt

    # 1) Detection
    risk = compute_risk(raw_prompt)

    # 2) Sanitization (if needed)
    if risk["action"] in ("sanitize", "block"):
        sanitized = sanitize_text(raw_prompt)
    else:
        sanitized = raw_prompt

    # 3) PPA wrapping (only if not blocked)
    wrapped = None
    template_id = None
    if risk["action"] != "block":
        wrapped, template_id = wrap_prompt(sanitized)

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    # 4) Log to DB
    db: Session = next(get_db())
    log = AttackLog(
        raw_prompt=raw_prompt,
        sanitized_prompt=sanitized,
        wrapped_prompt=wrapped or "",
        action=risk["action"],
        regex_score=risk["regex_score"],
        entropy_score=risk["entropy_score"],
        anomaly_score=risk["anomaly_score"],
        total_score=risk["total_score"],
        ppa_template_id=template_id or "",
        processing_ms=elapsed_ms,
    )
    db.add(log)
    db.commit()
    db.refresh(log)

    return AnalyzeResponse(
        scores=LayerScores(**risk),
        raw_prompt=raw_prompt,
        sanitized_prompt=sanitized,
        wrapped_prompt=wrapped,
        ppa_template_id=template_id,
        processing_ms=elapsed_ms,
    )


@app.get("/history", response_model=AttackHistoryResponse)
def history(limit: int = 50):
    db: Session = next(get_db())
    rows = (
        db.query(AttackLog)
        .order_by(AttackLog.id.desc())
        .limit(limit)
        .all()
    )

    items = [
        AttackLogItem(
            id=row.id,
            timestamp=row.timestamp.isoformat(),
            action=row.action,
            total_score=row.total_score,
            processing_ms=row.processing_ms,
            regex_score=row.regex_score,
            entropy_score=row.entropy_score,
            anomaly_score=row.anomaly_score,
            ppa_template_id=row.ppa_template_id or None,
        )
        for row in rows
    ]

    return AttackHistoryResponse(items=items)
