import streamlit as st
import ollama
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import Document
from langchain_core.runnables import RunnableMap
import warnings

warnings.filterwarnings("ignore")


# Fonction de chargement du vecteur store
def load_vector_store(chunks):
    '''
    Permet de stocker un fichier PDF dans un vector store, en utilisant le modèle d'embedding d'HuggingFace.

    Args :
        chunks : Morceau de ficher PDF
    '''
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma.from_documents(chunks, embedding, persist_directory="./chroma_db/PDF")
    return vector_store

# Fonction pour configurer le retriever
def setup_retriever(vector_store):
    '''
    Configure un retriever pour effectuer des recherches de similarité dans le vector store. Recherche les 2 documents les plus similaires

    Args:
        vector_store: Un vector store
    '''
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

# Fonction pour formater les documents récupérés
def format_docs(docs):
    '''
    Formate une liste de documents en une chaîne de caractères.

    Args:
        docs (list): Liste de documents
    '''
    return "\n\n".join(doc.page_content for doc in docs)

st.title("Le Chat du PDF")

if "messages_PDF" not in st.session_state:
    st.session_state["messages_PDF"] = [{"role": "assistant", "content": "Téléchargez un PDF et posez vos questions!"}]

uploaded_file = st.file_uploader("Déposez un PDF", type=("pdf"))

for msg in st.session_state.messages_PDF:
    st.chat_message(msg["role"]).write(msg["content"])

documents_pdf = []

if uploaded_file is not None:
    os.makedirs("./data/PDF", exist_ok=True)
    temp_pdf_path = f"./data/PDF/{uploaded_file.name}"
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    with st.spinner("Chargement du PDF..."):
        loader = PyMuPDFLoader(temp_pdf_path)
        documents_pdf += loader.load_and_split()
        
    # Découpe le fichier PDF en plusieurs morceaux d'une longueur de 600 caractères, et pour chaque morceaux un retour en arriere de 60 caractères pour conserver le contexte.
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=60,
        length_function=len,
        separators=["\n\n", "\n"]
    )
    chunks = text_splitter.split_documents(documents=documents_pdf)
    
    vector_store = load_vector_store(chunks)
    retriever = setup_retriever(vector_store)

if uploaded_file and (prompt := st.chat_input("Posez une question sur votre PDF")):
    st.session_state.messages_PDF.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    prompt_template = ChatPromptTemplate.from_template("""
        Tu es un assistant intelligent qui répond aux questions en utilisant les informations disponibles.

        Contexte :
        {context}

        Question de l'utilisateur :
        {question}
    """) 
    llm = ChatOllama(model='llama3.2')
    chain = (
        RunnableMap({
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        })
        | prompt_template
        | llm
        | StrOutputParser()
    )
    
    full_response = ""
    response_placeholder = st.empty()
    
    stream = chain.invoke(prompt) 
    
    for chunk in stream:
        full_response += chunk
        response_placeholder.chat_message("assistant").write(full_response)
    
    st.session_state.messages_PDF.append({"role": "assistant", "content": full_response})
