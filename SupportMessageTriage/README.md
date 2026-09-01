## Evaluation & Run
- **Eval Score**: 100% on 8/8 test cases (`evals/cases.json`) as of September 2026.
- **Prompt Version**: `prompts/triage-v1.md`
- **Estimated Cost**: Free tier via OpenRouter.

### Run with Curl
```bash
curl -X 'POST' \
  '[http://127.0.0.1:8000/triage](http://127.0.0.1:8000/triage)' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"message": "My billing card was charged twice!"}'