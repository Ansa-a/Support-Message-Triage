import json
import os
import time
from enum import Enum
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, ValidationError
from openai import OpenAI

app = FastAPI()

class CategoryEnum(str, Enum):
    billing = "billing"
    technical = "technical"
    account = "account"
    feature_request = "feature_request"
    general = "general"

class UrgencyEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"

class TriageInput(BaseModel):
    message: str = Field(..., min_length=1, description="Customer message cannot be empty")

class TriageOutput(BaseModel):
    category: CategoryEnum
    urgency: UrgencyEnum
    confidence: float = Field(..., ge=0.0, le=1.0)
    reason: str

# Initialize OpenAI/OpenRouter client with explicit timeout (<= 60s)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY", "dummy-key"),
    timeout=30.0
)

@app.post("/triage", response_model=TriageOutput)
def triage_message(payload: TriageInput):
    stub_mode = os.getenv("LLM_STUB", "0") == "1"
    llm_enabled = os.getenv("LLM_ENABLED", "true").lower() == "true"

    if stub_mode or not llm_enabled:
        return TriageOutput(
            category=CategoryEnum.general,
            urgency=UrgencyEnum.medium,
            confidence=0.5,
            reason="Stub mode or LLM disabled fallback response."
        )

    # Load prompt template
    prompt_path = "prompts/triage-v1.md"
    system_prompt = "Classify the support message."
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            system_prompt = f.read()

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": payload.message}
    ]

    start_time = time.time()
    model_name = os.getenv("LLM_MODEL", "openrouter/free")
    repair_count = 0
    raw_response_text = ""

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            response_format={"type": "json_object"}
        )
        raw_response_text = response.choices[0].message.content
        duration = time.time() - start_time
        token_counts = response.usage.total_tokens if response.usage else 0

        # Attempt validation
        parsed_data = json.loads(raw_response_text)
        result = TriageOutput(**parsed_data)
        
        # Log metrics (prompt version, model, tokens, duration, repairs)
        print(f"[LOG] model={model_name} tokens={token_counts} duration={duration:.2f}s repairs={repair_count}")
        return result

    except (ValidationError, json.JSONDecodeError, Exception) as e:
        repair_count = 1
        # Exactly one repair retry loop
        try:
            repair_messages = messages + [
                {"role": "assistant", "content": raw_response_text},
                {"role": "user", "content": f"Your previous output failed validation error: {e}. Fix the JSON output to strictly match the required TriageOutput schema."}
            ]
            repair_response = client.chat.completions.create(
                model=model_name,
                messages=repair_messages,
                response_format={"type": "json_object"}
            )
            fixed_text = repair_response.choices[0].message.content
            parsed_data = json.loads(fixed_text)
            return TriageOutput(**parsed_data)
        
        except Exception as final_err:
            # Quarantine log line
            os.makedirs("logs", exist_ok=True)
            with open("logs/quarantine.jsonl", "a", encoding="utf-8") as qf:
                qf.write(json.dumps({
                    "timestamp": time.time(),
                    "input": payload.message,
                    "raw_output": raw_response_text,
                    "error": str(final_err)
                }) + "\n")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": "Model output failed schema validation after repair.", "error": str(final_err)}
            )