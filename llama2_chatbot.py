"""
LLaMA 2 Chatbot app
======================

This is an Streamlit chatbot app with LLaMA2 that includes session chat history and option to select multiple LLM
API enpoints on Replicate. Each model (7B, 13B & 70B) runs on Replicate on one A100 (40Gb). The weights have been tensorized.

Author: Marco Mascorro (@mascobot.com)
Created: July 2023
Version: 0.9.0 (Experimental)
Status: Development
Python version: 3.9.15
a16z-infra
"""
#External libraries:
import streamlit as st
import replicate
from dotenv import load_dotenv
load_dotenv()
import os
from utils import find_top_k_houses

# feel free to replace with your own logo
logo1 = 'https://storage.googleapis.com/llama2_release/a16z_logo.png'
# TODO this resolution is way to high
logo2 = 'https://upload.wikimedia.org/wikipedia/commons/4/4d/OpenAI_Logo.svg'

###Initial UI configuration:###
st.set_page_config(page_title="LLaMA2 Chatbot by a16z-infra", page_icon=logo1, layout="wide")

# reduce font sizes for input text boxes
custom_css = """
    <style>
        .stTextArea textarea {font-size: 13px;}
        div[data-baseweb="select"] > div {font-size: 13px !important;}
    </style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

@st.cache_data
def load_data():
    # TODO load data from pinecone
    pass

st.sidebar.header("Paki Housing Chatbot")#Left sidebar menu
st.sidebar.markdown('**made by Konrad B.**')
st.sidebar.markdown('**(Chatbot UI not associated with Meta Platforms, Inc)**')

#Set config for a cleaner menu, footer & background:
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


PINECONE_ENV=os.environ.get('PINECONE_ENV')
PINECONE_API_KEY=os.environ.get('PINECONE_API_KEY')
PINECONE_INDEX_NAME=os.environ.get("PINECONE_INDEX_NAME")
OPENAPI_KEY=os.environ.get("OPENAPI_KEY")
OPENAI_MODEL=os.environ.get("OPENAI_MODEL")


if not (PINECONE_API_KEY and PINECONE_ENV and PINECONE_INDEX_NAME and OPENAPI_KEY):
    st.warning("Add a `.env` file to your app directory with the keys specified in `.env_template` to continue.")
    st.stop()

#container for the chat history
response_container = st.container()
#container for the user's text input
container = st.container()
#Set up/Initialize Session State variables:
if 'chat_dialogue' not in st.session_state:
    st.session_state['chat_dialogue'] = []
if 'string_dialogue' not in st.session_state:
    st.session_state['string_dialogue'] = ''

if 'city' not in st.session_state:
    st.session_state['city'] = 'Lahore'
if 'n_results' not in st.session_state:
    st.session_state['n_results'] = 3


selected_city = st.sidebar.selectbox('Choose a City:', ['Lahore', 'Karachi', 'Islamabad'], key='city_select')
st.session_state['city'] = selected_city

#Model hyper parameters:
st.session_state['n_results'] = st.sidebar.slider('N Results:', min_value=1, max_value=5, value=3, step=1)


# Add the "Clear Chat History" button to the sidebar
clear_chat_history_button = st.sidebar.button("Clear Chat History")

# Check if the button is clicked
if clear_chat_history_button:
    # Reset the chat history stored in the session state
    st.session_state['chat_dialogue'] = []
    
    
# add links to relevant resources for users to select
text1 = 'Chatbot Demo Code' 
text2 = 'Model from OpenaI' 
text3 = 'LLaMa2 Cog Template'

logo1_link = "https://github.com/a16z-infra/llama2-chatbot"
logo2_link = "https://platform.openai.com/overview"
text3_link = "https://github.com/a16z-infra/cog-llama-template"

st.sidebar.markdown(f"""
<div class='resources-section'>
    <h3>Resources:</h3>
    <div style="display: flex; justify-content: space-between;">
        <div style="display: flex; flex-direction: column; padding-left: 15px;">
            <div style="align-self: flex-start; padding-bottom: 5px;"> <!-- Change to flex-start here -->
                <a href="{logo1_link}">
                    <img src="{logo1}" alt="Logo 1" style="width: 30px;"/>
                </a>
            </div>
            <div style="align-self: flex-start;">
                <p style="font-size:11px; margin-bottom: -5px;"><a href="{logo1_link}">{text1}</a></p>
                <p style="font-size:11px;"><a href="{text3_link}">{text3}</a></p>  <!-- second line of text -->
            </div>
        </div>
        <div style="display: flex; flex-direction: column; padding-right: 25px;">
            <div style="align-self: flex-start; padding-bottom: 5px;">
                <a href="{logo2_link}">
                    <img src="{logo2}" alt="Logo 2" style="width: 120px;"/>
                </a>
            </div>
            <div style="align-self: flex-start;">
                <p style="font-size:11px;"><a href="{logo2_link}">{text2}</a></p>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


# Display chat messages from history on app rerun
for message in st.session_state.chat_dialogue:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input
if prompt := st.chat_input(f"Type the description of your dream house in {st.session_state['city']}"):
    # Add user message to chat history
    st.session_state.chat_dialogue.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        print (prompt)
        output = find_top_k_houses(
            OPENAPI_KEY,
            OPENAI_MODEL,
            PINECONE_INDEX_NAME,
            PINECONE_ENV,
            PINECONE_API_KEY,
            prompt,
            city=st.session_state['city'],
            top_k=st.session_state['n_results'],
        )
        full_response = f"Here are the top {st.session_state['n_results']} houses in {st.session_state['city']} that match your description:\n\n"
        full_response += "".join(output)
        message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
    # Add assistant response to chat history
    st.session_state.chat_dialogue.append({"role": "assistant", "content": full_response})



