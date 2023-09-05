import replicate
import time
import openai
import os
import pinecone

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


def find_top_k_houses(
    openai_key, openai_model, pc_index, pc_env, pc_key, user_description, city, top_k
):
    # TODO assert user description not too long
    openai.api_key = openai_key

    pinecone.init(api_key=pc_key, environment=pc_env)
    index = pinecone.Index(index_name=pc_index)
    embedded_query = openai.Embedding.create(
        input=[user_description], model=openai_model
    )["data"][0]["embedding"]

    query_response = index.query(
        top_k=top_k,
        include_values=False,
        include_metadata=True,
        vector=embedded_query,
        filter={"city": {"$eq": city}},
    )

    result_string = ""

    for i, result in enumerate(query_response["matches"]):
        result_string += result["id"] + ":\n" + \
                result["metadata"]["description"]+  "\n\n"
        
    return result_string
