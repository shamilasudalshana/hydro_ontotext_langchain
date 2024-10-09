import streamlit as st
from langchain_openai.chat_models import ChatOpenAI
from langchain_community.graphs import OntotextGraphDBGraph
from langchain.chains import OntotextGraphDBQAChain
import os
import io
from contextlib import redirect_stdout
from update_bash_docker_files_func import update_graphdb_docker_files

# Set the environment variable `OPENAI_API_KEY` to your OpenAI API key
os.environ["OPENAI_API_KEY"] = "..................................."
os.environ["GRAPHDB_USERNAME"] = "admin"
os.environ["GRAPHDB_PASSWORD"] = "abc123"

# Streamlit App Title
st.title("🦜🔗 Question Answering from RDF Datasets")

# Option to select data source type
data_source = st.radio("Choose data source type:", ("Local RDF files and ontologies", "Provide URLs for RDF data files and ontologies"))

if data_source == "Local RDF files and ontologies":
    # Upload the data files
    data_files = st.file_uploader("Upload RDF Data Files (.ttl)", type="ttl", accept_multiple_files=True)
    
    # Upload the ontology file (restricted to one file)
    ontology_file = st.file_uploader("Upload Ontology File (.ttl)", type="ttl", accept_multiple_files=False)

    
    if ontology_file is not None and 'ontology_uploaded' not in st.session_state:
        st.session_state['ontology_uploaded'] = True
        # Run the function immediately after upload
        update_graphdb_docker_files(data_files, ontology_file)
        st.success("Ontology and data files have been processed and Docker/GraphDB files updated.")
    
    
    # Check if an ontology file has been uploaded
    if ontology_file is not None:
        # Assign the uploaded file to `local_file` variable
        local_file = ontology_file.name  # Adjust this line as needed to handle the file stream

        # Initialize the OntotextGraphDBGraph with the uploaded ontology file
        graph = OntotextGraphDBGraph(
            query_endpoint="http://localhost:7200/repositories/langchain",
            local_file=local_file,  # Path to the uploaded ontology file
        )
else:
    st.write("URL-based RDF data loading option is not yet implemented. Please choose 'Local RDF files and ontologies'.")

# Sidebar for OpenAI API Key input
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

# Initialize session state to store conversation history
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

def generate_response(input_text):
    # Initialize the chain with the Ontotext graph and OpenAI model
    chain = OntotextGraphDBQAChain.from_llm(
        ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo"),
        graph=graph,
        verbose=True
    )

    # Capture the output of the response
    f = io.StringIO()
    with redirect_stdout(f):
        response = chain.invoke({chain.input_key: input_text})
    verbose_output = f.getvalue()

    # Store the conversation
    st.session_state.conversation.append({"user": input_text, "response": response[chain.output_key], "sparql_query": verbose_output})

    return response

# Streamlit chat interface
with st.form("chat_form"):
    text = st.text_area("Enter your question:")
    submitted = st.form_submit_button("Submit")

    if submitted:
        if openai_api_key.startswith("sk-"):
            generate_response(text)
        else:
            st.warning("Please enter your OpenAI API key correctly!", icon="⚠")

# Display conversation history
if st.session_state.conversation:
    for i, exchange in enumerate(st.session_state.conversation):
        st.write(f"**User {i+1}:** {exchange['user']}")
        st.write(f":green[**Assistant {i+1}:** {exchange['response']}]")
        st.write(f"**Generated SPARQL Query {i+1}:**")
        st.code(exchange['sparql_query'], language="sparql")
