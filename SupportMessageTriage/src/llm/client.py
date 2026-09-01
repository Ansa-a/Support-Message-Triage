import os
import json
from pathlib import Path
from openai import OpenAI
from src.llm.schema import TriageOutput
from pydantic import ValidationError

def get_client() -> OpenAI:
    """Initializes the OpenAI client safely, stripping unwanted keyword arguments."""
    # Temporarily clear any environment proxy variables that might confuse httpx/openai
    os.environ.pop("http_proxy", None)
    os.environ.pop("https_proxy", None)
    os.environ.pop("HTTP_PROXY", None)
    os.environ.pop("HTTPS_PROXY", None)

    return OpenAI(
        base_url=os.getenv("LLM_BASE_URL"),
        api_key=os.getenv("LLM_API_KEY")
    )

def load_prompt() -> str:
    """Loads the versioned system prompt from the prompts directory[cite: 1]."""
    prompt_path = Path("prompts/triage-v1.md")
    return prompt_path.read_text(encoding="utf-8")

def log_to_quarantine(user_text: str, raw_output: str, error_msg: str, prompt_version: str):
    """Safely writes unparseable or invalid model outputs to a JSONL quarantine log[cite: 1]."""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_entry = {
        "prompt_version": prompt_version,
        "input": user_text,
        "raw_output": raw_output,
        "error": error_msg
    }
    with open(log_dir / "quarantine.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

def parse_and_validate(content: str) -> TriageOutput:
    """Strips markdown code fences, isolates JSON, and validates against the Pydantic schema[cite: 1]."""
    cleaned = content.replace("```json", "").replace("```", "").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1:
        cleaned = cleaned[start:end+1]
    
    data = json.loads(cleaned)
    return TriageOutput(**data)

def call_llm_with_repair(user_text: str) -> TriageOutput:
    """Calls the model, validates the output, and executes a single repair retry if validation fails[cite: 1]."""
    client = get_client()
    system_prompt = load_prompt()
    model_name = os.getenv("LLM_MODEL", "openrouter/free")
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_text} # Untrusted content isolated in user message
    ]

    # First model attempt
    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=0.0
    )
    raw_content = response.choices[0].message.content

    try:
        return parse_and_validate(raw_content)
    except (json.JSONDecodeError, ValidationError) as first_error:
        # Repair retry: Send back the error and the broken output to let the model fix it once
        repair_message = (
            f"Your previous answer was rejected because of this error: {str(first_error)}. "
            f"Previous broken output: {raw_content}. "
            "Return ONLY corrected JSON matching the schema."
        )
        
        messages.append({"role": "assistant", "content": raw_content})
        messages.append({"role": "user", "content": repair_message})

        retry_response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.0
        )
        retry_content = retry_response.choices[0].message.content

        try:
            return parse_and_validate(retry_content)
        except (json.JSONDecodeError, ValidationError) as second_error:
            # If repair fails too, give up cleanly and write to quarantine
            log_to_quarantine(user_text, retry_content, str(second_error), "triage-v1")
            raise ValueError(f"Model failed validation after repair: {str(second_error)}")


