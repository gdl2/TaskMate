from html_preprocessing import preprocess_html

import pickle
from flask import Flask, request, jsonify
from flask_cors import CORS

from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate, LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone
import pinecone

import re
import json

import os
os.environ["OPENAI_API_KEY"] = "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"

# initialize pinecone
pinecone.init(
    api_key="258a5561-3828-4a8e-9807-ad8df86ef5be",  # find at app.pinecone.io
    environment="eu-west1-gcp"  # next to api key in console
)
index = pinecone.Index("cosiw-project")
embeddings = OpenAIEmbeddings()
vectorstore = Pinecone(index, embeddings.embed_query, "text")

query_actions_mapping = {}
# check is mapping exists on disk
if os.path.isfile("query_actions_mapping.pickle"):
    # deserialize the dictionary from the file
    with open("query_actions_mapping.pickle", 'rb') as f:
        query_actions_mapping = pickle.load(f)

app = Flask(__name__)
CORS(app)

# Use OpenAI ChatGPT model
chat = ChatOpenAI(temperature=0)
init_message_history = [
    SystemMessage(content="You are controlling a Chrome Extension. \
    You are given the HTML of the webpage and the user command. \
    You can interact with any elements on the webpage. \
    You cannot use any APIs. \
    Only use Javascript code to interact with these elements. \
    Keep all the Javascript code together in one code block. Make it easy for a program to parse to find the code by searching for ```. \
    Use concise explanations. \
    If you are unsure of what to do, you can ask the user to help you.")
]
message_history = init_message_history.copy()
summary_in_chat = False

@app.route('/get_response', methods=['POST'])
def get_response():
    global message_history
    global summary_in_chat

    # Get the HTML from the request body
    raw_html = request.json['html']
    
    # Preprocess the HTML
    html = preprocess_html(raw_html)

    # Get the user's command from the request body
    message = request.json['message']

    # Create user prompt template
    user_template = "HTML: {}\nUser command: {}".format(html, message)

    # Ignore code in step-by-step summary that ChatGPT repeats (next step: bot decides when to execute code or not?)
    restate_summary = False
    # Used to show the step button
    found_summary = False
    # Track the list of steps in step-by-step summary
    lst_steps = None
    # Check if message history only has System Message (if empty otherwise)
    if len(message_history) == 1:
        print("RETRIEVING EMBEDDING")
        # If so, search for past summary of this task being completed
        docs = vectorstore.similarity_search(user_template)
        print(docs)
        if len(docs) != 0:
            # Use the most relevant embedding
            key = docs[0].page_content
            print("EMBEDDING FOUND:", key)
            past_summary = query_actions_mapping[key]
            print(past_summary)

            # Parse the list of steps from the step-by-step summary
            lst_steps = re.findall(r'\d+\.\s+(.*)', past_summary)

            # Create string representation of steps
            lst_steps = json.dumps(lst_steps)

            # Prepend summary to user_template
            user_template = "Step-by-step summary for performing a similar task with a different objective:\n" + past_summary + "\Let the user know you found the summary above."
            restate_summary = True
            found_summary = True
            summary_in_chat = True


    # Add message as HumanMessage to message history 
    message_history.append(HumanMessage(content=user_template))

    # Get a response from the chatbot
    response = chat(message_history[:2] + message_history[-1:]).content

    # Add bot response as AIMessage to message history 
    message_history.append(AIMessage(content=response))

    print("MESSAGE HISTORY:", message_history)

    javascript_code = None

    # Check if step-by-step summary is not being restated
    if not restate_summary:
        # Extract Javascript code from response
        # Find the starting and ending indices of the JavaScript code
        start_index = response.find("```") + 3
        end_index = response.find("```", start_index)

        # Make sure that code exists in response
        if start_index != 2 and end_index != -1:
            # Extract the JavaScript code from the response
            javascript_code = response[start_index:end_index]
            # Remove "javascript" prefix if necessary
            prefix = "javascript"
            if javascript_code.startswith(prefix):
                javascript_code = javascript_code[len(prefix):]
            
            print("JS code:", javascript_code)

    # Return the chatbot's response as a JSON object
    return jsonify({'response': response, 'javascript_code': javascript_code, 'found_summary': found_summary, 'lst_steps': lst_steps})

@app.route('/save_history', methods=['POST'])
def save_history():
    global message_history
    temp_message_history = message_history.copy()
    print(temp_message_history)

    global summary_in_chat

    # Make sure not to save restated summary (to avoid overlap or summary from different task)
    if summary_in_chat:
        temp_message_history = temp_message_history[:1] + temp_message_history[3:] # removes the restate summary User message and Assistant response

    # Add message as HumanMessage to message history
    #temp_message_history.append(HumanMessage(content="Concisely summarize our conversation above into steps and include code for each step. Start from the beginning of the conversation. Do not include steps that didn't work."))
    temp_message_history.append(HumanMessage(content="Concisely summarize our conversation above into steps and include code and HTML for each step. Start from the beginning of the conversation. Do not include steps that didn't work."))
    
    # Get a response from the chatbot
    response = chat(temp_message_history).content
    print(response)
    
    # Save the original task query response in vectorstore
    original_query = temp_message_history[1].content
    vectorstore.add_texts([original_query])

    # Save the key-value pair of query, step-by-step summary
    query_actions_mapping[original_query] = response
    
    # Disk the mapping to disk
    with open("query_actions_mapping.pickle", "wb") as f:
        pickle.dump(query_actions_mapping, f)

    print(query_actions_mapping)

    return jsonify({'response': "SUCCESS"})

@app.route('/clear_history', methods=['POST'])
def clear_history():
    global message_history
    global summary_in_chat
    print(1)
    # Clear previous chat history
    message_history = init_message_history.copy()
    summary_in_chat = False
    print(message_history)
    print(2)

    return jsonify({'response': "SUCCESS"})

if __name__ == '__main__':
    app.run(debug=True)
