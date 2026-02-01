# responsive-chatbot
# Telangana Government Chatbot

## Setup
1. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh
2. ollama pull llama3.1:8b
3. pip install ollama pydantic
4. python chatbot.py

## Workflow Guarantees
- **Extraction**: Always JSON via schema - no parsing fails
- **Guardrails**: Blocks responses without clear dept
- **Reprompt**: Auto-asks for dept with examples
- **Responses**: Dept-specific, official-style
- **Error-proof**: Fallbacks for validation errors

## Test Examples
You: Tax status check → Revenue response
You: Weather → Reprompt for dept
You: FIR online → Police response

