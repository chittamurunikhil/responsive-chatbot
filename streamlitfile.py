import streamlit as st
import ollama
import json
from pydantic import ValidationError, BaseModel, Field
from typing import Literal
# Import your existing prompts
from prompts import EXTRACTION_PROMPT_BASE, CLARIFICATION_PROMPT, DEPT_RESPONSE_PROMPT

class ExtractionPayload(BaseModel):
    department: Literal['Revenue', 'Police', 'Health', 'Education', 'Transport', 'Agriculture', None] = Field(
        description="Exact department match or None if unclear"
    )
    prompt: str = Field(description="Cleaned user query")

class GovernmentChatbot:
    def __init__(self, model="gemma3:4b"):
        self.model = model

    def extract_payload(self, user_input: str) -> ExtractionPayload:
        prompt = EXTRACTION_PROMPT_BASE.replace("USER_INPUT_PLACEHOLDER", user_input)
        with st.spinner("Extracting department..."):
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                format="json"  # Use Ollama's json mode for structured output
            )
        try:
            content = response['message']['content']
            payload = ExtractionPayload.model_validate_json(content)
            st.session_state.debug_info = f"✅ Extracted: {payload.model_dump()}"
            return payload
        except (ValidationError, KeyError, json.JSONDecodeError) as e:
            st.session_state.debug_info = f"⚠️ Extraction failed: {str(e)[:100]}... Fallback used."
            return ExtractionPayload(department=None, prompt=user_input)

    def needs_clarification(self, payload: ExtractionPayload) -> str:
        if payload.department is None:
            return CLARIFICATION_PROMPT.format(prompt=payload.prompt)
        return None

    def generate_response(self, payload: ExtractionPayload) -> str:
        dept_prompt = DEPT_RESPONSE_PROMPT.format(
            department=payload.department,
            prompt=payload.prompt
        )
        with st.spinner(f"Generating {payload.department} response..."):
            response = ollama.chat(
                model=self.model,
                messages=[{"role": "user", "content": dept_prompt}]
            )
        return response['message']['content']

# Streamlit UI
st.set_page_config(page_title="GovChatBot", page_icon="🏛️", layout="wide")
st.title("🏛️ Government Chatbot")
st.markdown("**Ask about services from Revenue, Police, Health, Education, Transport, or Agriculture**")

# Sidebar for model selection and debug
with st.sidebar:
    selected_model = st.selectbox("Ollama Model", ["gemma3:4b", "llama3.2:3b", "qwen2.5:3b"])
    show_debug = st.checkbox("Show Debug Info")
    bot = GovernmentChatbot(model=selected_model)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "debug_info" not in st.session_state:
    st.session_state.debug_info = ""

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Debug info
if show_debug and st.session_state.debug_info:
    with st.expander("Debug (Latest Extraction)"):
        st.info(st.session_state.debug_info)

# Chat input
if prompt := st.chat_input("Describe your query (e.g., 'Tax refund status' or 'FIR filing')"):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Process with bot
    with st.chat_message("assistant"):
        payload = bot.extract_payload(prompt)
        clarification = bot.needs_clarification(payload)
        
        if clarification:
            response = clarification
        else:
            response = bot.generate_response(payload)
        
        st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

# Instructions
with st.expander("How to Use"):
    st.markdown("""
    - Type your query naturally: "Check my tax refund" → Routed to **Revenue**
    - No department match? Bot asks for clarification
    - **Debug mode** shows extracted department and validation status
    - Supports your exact Pydantic schema and prompts
    - History persists during session
    """)
