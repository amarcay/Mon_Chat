import streamlit as st
import pandas as pd
import chardet
import os
from langchain_community.document_loaders import CSVLoader
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
def load_vector_store(documents_csv):
    '''
    Permet de stocker un fichier CSV dans un vector store, en utilisant le modèle d'embedding d'HuggingFace.

    Args :
        documents_csv : Un document CSV
    '''
    embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
    vector_store = Chroma.from_documents(documents_csv, embedding, persist_directory="./chroma_db/CSV")
    return vector_store

# Fonction pour configurer le retriever
def setup_retriever(vector_store):
    '''
    Configure un retriever pour effectuer des recherches de similarité dans le vector store. Recherche les 10 documents les plus similaires

    Args:
        vector_store: Un vector store
    '''
    return vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 10})

# Fonction pour formater les documents récupérés
def format_docs(docs):
    '''
    Formate une liste de documents en une chaîne de caractères.

    Args:
        docs (list): Liste de documents
    '''
    return "\n\n".join(doc.page_content for doc in docs)

# Interface utilisateur
st.title("Le Chat du CSV")

if "messages_CSV" not in st.session_state:
    st.session_state["messages_CSV"] = [{"role": "assistant", "content": "Téléchargez un fichier CSV et posez vos questions!"}]

uploaded_file = st.file_uploader("Déposez un CSV", type=("csv"))

for msg in st.session_state.messages_CSV:
    st.chat_message(msg["role"]).write(msg["content"])

documents_csv = []

if uploaded_file is not None:
    # Détecter l'encodage du ficher afin de pouvoir ouvrir le csv peu importe son encodage
    rawdata = uploaded_file.getvalue()
    result = chardet.detect(rawdata)
    detected_encoding = result["encoding"]

    os.makedirs("./data/CSV", exist_ok=True)
    temp_csv_path = f"./data/CSV/{uploaded_file.name}"
    with open(temp_csv_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    if os.stat(temp_csv_path).st_size == 0:
        st.error("Le fichier CSV est vide. Veuillez en télécharger un valide.")
    else:
        try:
            # Pour afficher les données sur l'interface
            df = pd.read_csv(temp_csv_path, encoding=detected_encoding)
            loader = CSVLoader(temp_csv_path, encoding=detected_encoding)
            documents_csv += loader.load_and_split()
        except pd.errors.EmptyDataError:
            st.error("Erreur: Le fichier CSV ne contient aucune donnée lisible.")
        except Exception as e:
            st.error(f"Une erreur est survenue: {e}")

# Figer l'aperçu du fichier en haut
if "csv_preview" not in st.session_state and uploaded_file is not None:
    st.session_state["csv_preview"] = df.head(5)

#Afficher le df dans l'interface
if "csv_preview" in st.session_state:
    st.write("Aperçu du fichier CSV :")
    st.dataframe(st.session_state["csv_preview"])

# S'il a un ficher csv alors afficher le prompt
if uploaded_file and (prompt := st.chat_input("Posez une question sur votre CSV")):
    st.session_state.messages_CSV.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    # Stockés les données du csv dans un DB
    vector_store = load_vector_store(documents_csv)
    retriever = setup_retriever(vector_store)
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
    
    st.session_state.messages_CSV.append({"role": "assistant", "content": full_response})
