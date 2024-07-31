import streamlit as st
from dotenv import load_dotenv
import fitz  # PyMuPDF
from groq import Groq
import os
import time
import random

st.set_page_config(
    page_title="Chat with PDF",
    page_icon="🌹",
    menu_items={
        'About': "# Created by YXONE"
    }
)

st.title('Chat with PDF 💬')

# Sidebar contents
with st.sidebar:
    st.title("🤔 LLM Chat App")
    st.markdown(
        """
    ## About
    This app is an LLM-powered chatbot built using:
    - [Streamlit](https://streamlit.io/)
    - [Groq](https://groq.com/)
    """
    )
    # PDF file upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

load_dotenv()

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Initialize the Groq client
client = Groq(api_key=os.getenv('GROQ_API_KEY'))


def show_message(prompt, model_name, loading_str, existing_messages):
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown(loading_str)
        full_response = ""
        try:
            # Include the history in the messages
            messages = existing_messages + [{"role": "user", "content": prompt}]
            completion = client.chat.completions.create(
                model=model_name,
                messages=messages,
                temperature=1,
                max_tokens=1024,
                top_p=1,
                stream=True,
                stop=None
            )
            for chunk in completion:
                content = chunk.choices[0].delta.content
                if content:  # Check if content is not None
                    for word in content:
                        full_response += word
                        message_placeholder.markdown(full_response + "_")
                        time.sleep(0.005)
        except Exception as e:
            st.exception(e)
        message_placeholder.markdown(full_response)
        st.session_state.history.append({"role": "assistant", "content": full_response})

def clear_state():
    st.session_state.history = []

if "history" not in st.session_state:
    st.session_state.history = []

# Model selection
model_name = st.sidebar.selectbox(
    "Select Model",
    ["llama3-8b-8192", "gemma2-9b-it"]
)

# Display existing chat history except for the initial hidden conversation
for item in st.session_state.history[1:]:
    with st.chat_message(item["role"]):
        st.markdown(item["content"])

# PDF file path
if uploaded_file:
    st.success("File successfully uploaded!")
    initial_text = extract_text_from_pdf(uploaded_file)

    # Initialize the conversation with the initial PDF content if history is empty
    clear_state()
    st.session_state.history.append({"role": "user", "content": initial_text})

    if prompt := st.chat_input("Ask questions about your PDF file:"):
        prompt = prompt.replace('\n', '  \n')
        with st.chat_message("user"):
            st.markdown(prompt)
            st.session_state.history.append({"role": "user", "content": prompt})

        show_message(prompt, model_name, "Thinking...", st.session_state.history)
