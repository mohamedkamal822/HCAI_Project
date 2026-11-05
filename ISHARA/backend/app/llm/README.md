# LLM response module

`gemini.py` contains the Google AI Studio request client and the response checks. `prompts.py` contains the generation prompt.

The API calls this module only after the sign catalog finds a verified entry. It passes the canonical Arabic and English labels plus the match type. Generated replies must mention the exact Arabic label, stay in Arabic, fit the short learning context, and pass format checks before the frontend receives them. Invalid, repeated, unavailable, or unconfigured model responses are omitted; the deterministic sign result remains available.

Configure `GEMINI_API_KEY`, `GEMINI_MODEL`, and `GEMINI_KEY_ROTATED_AT` in the project `.env` file. Keep that file out of version control.
