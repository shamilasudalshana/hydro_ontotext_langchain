import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.graphs import OntotextGraphDBGraph
from langchain.chains import OntotextGraphDBQAChain
import os
import io
from contextlib import redirect_stdout

# Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
os.environ["OPENAI_API_KEY"] = ".................................."

os.environ["GRAPHDB_USERNAME"] = "admin"
os.environ["GRAPHDB_PASSWORD"] = "abc123"

# Initialize the OntotextGraphDBGraph with the RDF dataset
graph = OntotextGraphDBGraph(
    query_endpoint="http://localhost:7200/repositories/langchain",
    local_file="nf4di_earth_onthology.ttl",  # Path to the ontology file
)

# Streamlit App Title
st.title("🦜🔗 Question answering from RDF datasets")

# Sidebar for OpenAI API Key input
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# st.write(graph)

# Initialize session state to store conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

def generate_response(input_text):
    # Initialize the chain with the Ontotext graph and OpenAI model
    chain = OntotextGraphDBQAChain.from_llm(
        ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
        graph=graph,
        verbose=True  # Set verbose to False to avoid excessive logging
    )

    # Get the response from the chain
    # Capture the verbose output
    f = io.StringIO()
    with redirect_stdout(f):
        response = chain.invoke({chain.input_key: input_text})

    
    # Get the verbose output (including the SPARQL query)
    verbose_output = f.getvalue()
    
    # For displaying the generated SPARQL query, capture it appropriately
    # Assuming there's an internal method to get the SPARQL query
    # sparql_query = chain.get_last_sparql_query()

    # For now, we won't be capturing the SPARQL query; you can implement this later if necessary
    sparql_query = verbose_output



    # Add the user query and the response to the session state conversation history
    st.session_state.conversation.append({"user": input_text, "response": response[chain.output_key], "sparql_query": sparql_query,
                                          'completed_response_object': response })

    return response

# Streamlit chat interface using session state
with st.form("chat_form"):
    # Text input area for user query
    text = st.text_area("Enter your question:")
    
    # Submit button
    submitted = st.form_submit_button("Submit")
    
    if submitted:
        # Check if OpenAI API key is valid
        if openai_api_key.startswith("sk-"):
            # Generate and store the response in session state
            generated_resposne = generate_response(text)

        else:
            st.warning("Please enter your OpenAI API key correctly!", icon="⚠")

# Display the conversation history in chat format
if st.session_state.conversation:
    for i, exchange in enumerate(st.session_state.conversation):
        # Display user message
        st.write(f"**User {i+1}:** {exchange['user']}")
        # Display generated response
        st.write(f":green[**Assistant {i+1}:** {exchange['response']}]")
        # Optionally display the generated SPARQL query
        st.write(f"**Generated SPARQL Query {i+1}:**")
        st.code(exchange['sparql_query'], language="sparql")
