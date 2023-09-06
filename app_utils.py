import replicate
import time
import openai
import os
import pinecone
import streamlit as st
from Database import PineConeWrap

# Initialize debounce variables
last_call_time = 0
debounce_interval = 2  # Set the debounce interval (in seconds) to your desired value


def debounce_replicate_run(llm, prompt, max_len, temperature, top_p, API_TOKEN):
    global last_call_time
    print("last call time: ", last_call_time)

    # Get the current time
    current_time = time.time()

    # Calculate the time elapsed since the last call
    elapsed_time = current_time - last_call_time

    # Check if the elapsed time is less than the debounce interval
    if elapsed_time < debounce_interval:
        print("Debouncing")
        return "Hello! You are sending requests too fast. Please wait a few seconds before sending another request."

    # Update the last call time to the current time
    last_call_time = time.time()

    output = replicate.run(
        llm,
        input={
            "prompt": prompt + "Assistant: ",
            "max_length": max_len,
            "temperature": temperature,
            "top_p": top_p,
            "repetition_penalty": 1,
        },
        api_token=API_TOKEN,
    )
    return output


def embed_query(query):
    openai_key = st.session_state["OPENAI_API_KEY"]
    openai_model = st.session_state["OPENAI_MODEL"] 

    openai.api_key = openai_key

    embedded_query = openai.Embedding.create(
        input=[query], model=openai_model
    )["data"][0]["embedding"]
    
    return embedded_query


def find_top_k_houses(
    user_description, city, top_k
):
    
    pc_index = st.session_state["PINECONE_INDEX_NAME"] 
    pc_env = st.session_state["PINECONE_ENV"]
    pc_key = st.session_state["PINECONE_KEY"]
       
    index = PineConeWrap(pc_key, pc_env, pc_index)
    
    embedded_query = embed_query(user_description)
    
    if not embed_query:
        st.warning("Description could not be embedded. Please try again.")
        return None

    query_response = index.query(
        top_k=top_k,
        include_values=False,
        include_metadata=True,
        vector=embedded_query,
        filter={"city": {"$eq": city}},
    )

        
    return query_response
