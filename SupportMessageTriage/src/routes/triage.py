import os
from fastapi import APIRouter, HTTPException
from src.llm.schema import TriageInput, TriageOutput, CategoryEnum, UrgencyEnum
from src.llm.client import call_llm_with_repair

router = APIRouter()

@router.post("/triage", response_model=TriageOutput)
def triage_support_message(payload: TriageInput):
    # Stub mode check (Stage 1 requirement)
    # Use a robust boolean check
    if os.getenv("LLM_STUB", "0").strip() == "1":
        return TriageOutput(
        category=CategoryEnum.other,
        urgency=UrgencyEnum.normal,
        confidence=0.5,
        reason="Stub response active for testing."
    )
    
    try:
        return call_llm_with_repair(payload.text)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


