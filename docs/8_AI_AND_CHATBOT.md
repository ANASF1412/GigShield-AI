# Explainable AI (XAI) & Chatbot Identity

Insurance regulation dreads "Black Box AI." We solved it entirely.

## 🤖 The Read-Only Gemini Protocol

Instead of allowing an LLM to generate premium logic, we constrained the AI entirely.
*   **The Actuary (Python):** Generates ML scores, applies Zone constraints, limits payouts, logs actions.
*   **The Chatbot (Gemini):** Takes the final JSON output of those mathematical actions, places them into a System Prompt, and is instructed simply to *Explain* it.

### UI Implementation
The Assistant lives at the bottom of the Dashboards.
*   **Worker Context:** The bot knows your name, your zone, and why your last claim got blocked, answering seamlessly.
*   **Admin Context:** The bot strips identity and answers macro-pool questions regarding structural limits.

### Safe Fallback
If the internet dies or the API key vanishes, a pure Regex-fallback mode continues operating locally. Demo safety is 100% secured.
