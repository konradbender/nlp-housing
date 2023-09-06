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
from app_utils import find_top_k_houses

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

st.sidebar.header("Paki Housing Search Engine")#Left sidebar menu
st.sidebar.markdown('**made by Konrad B.**')


st.session_state["PINECONE_ENV"] = os.environ.get('PINECONE_ENV')
st.session_state["PINECONE_KEY"] = os.environ.get('PINECONE_KEY')
st.session_state["PINECONE_INDEX_NAME"] = os.environ.get("PINCEONE_INDEX")
st.session_state["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")
st.session_state["OPENAI_MODEL"] = os.environ.get("OPENAI_EMBEDDING_MODEL")


if not (
    st.session_state["PINECONE_ENV"] and
    st.session_state["PINECONE_KEY"] and
    st.session_state["PINECONE_INDEX_NAME"] and
    st.session_state["OPENAI_API_KEY"] and
    st.session_state["OPENAI_MODEL"] 
):
    st.warning("Add a `.env` file to your app directory with the keys specified in `.env_template` to continue.")
    st.stop()


#Set up/Initialize Session State variables:
if 'string_dialogue' not in st.session_state:
    st.session_state['string_dialogue'] = ''
if 'city' not in st.session_state:
    st.session_state['city'] = 'Lahore'
if 'n_results' not in st.session_state:
    st.session_state['n_results'] = 3
if 'max_price' not in st.session_state:
    st.session_state['max_price'] = 1e7
    

st.sidebar.selectbox('Choose a City:', ['Lahore', 'Karachi', 'Islamabad'], key='city')

# Search filter
st.sidebar.slider('N Results:', min_value=1, max_value=5, step=1, key='n_results')
st.sidebar.slider('Max Price', min_value=1, max_value=int(1e7), step=int(1e3), key='max_price')



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

# Accept user input
text_search = st.text_input(f"Type the description of your dream house in {st.session_state['city']}")

if text_search:
    # do not display user input in main window, because it will be still visible in the text input
    output = find_top_k_houses(
        text_search,
        city=st.session_state['city'],
        top_k=st.session_state['n_results'],
    )
    if not output:
        st.markdown(f"Sorry, I couldn't find any houses in {st.session_state['city']} that match your description.")
            
        st.markdown(f"Here are the top {st.session_state['n_results']} houses in {st.session_state['city']} that match your description:\n\n")
    
    for i, result in enumerate(output["matches"]):
        st.subheader(f'House {i+1}')
        col1, col2, col3, col4 = st.columns(4, gap="small")
        col1.metric("Beds", int(result["metadata"]["bedrooms"]), delta=None, delta_color="normal", help=None, label_visibility="visible")
    
        col2.metric("Baths", int(result["metadata"]["baths"]), delta=None, delta_color="normal", help=None, label_visibility="visible")
    
        col3.metric("Price", f'{int(result["metadata"]["price"]/1e3)} K', delta=None, delta_color="normal", help=None, label_visibility="visible")
    
        col4.metric("Area", result["metadata"]["area"], delta=None, delta_color="normal", help=None, label_visibility="visible")
            
        st.markdown(f'**Description**: {result["metadata"]["GPT-Description"]} \n')
else:
    pass



