# Job Card: Support Message Triage

## Input
- `message` (string, required): The raw customer support message text.
- `customer_tier` (string, optional): Account tier (e.g., "free", "pro", "enterprise").

## Output Fields
- `category`: Closed list [`billing`, `technical`, `account`, `feature_request`, `general`]
- `urgency`: Closed list [`low`, `medium`, `high`, `critical`]
- `confidence`: Float between 0.0 and 1.0
- `reason`: Concise string explaining the decision (max 2 sentences)

## Must Never Rules
- Never return raw model text or markdown blocks outside the JSON schema.
- Never concatenate user-supplied message text directly into the system prompt.
- Never retry on 400, 401, or 403 HTTP status codes.

## When-Unsure Behaviour
- If the category or urgency is ambiguous, default `category` to `general`, `urgency` to `medium`, set `confidence` to $\le 0.5$, and explain the ambiguity in `reason`.