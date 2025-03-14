import streamlit as st
import glob
import chardet
import os
import pandas as pd
from langchain_community.utilities import SQLDatabase
from sqlalchemy import create_engine
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_ollama import ChatOllama
from langchain.agents import AgentType
from langchain_experimental.sql import SQLDatabaseChain
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import RunnableMap, RunnablePassthrough, RunnableLambda
import warnings

warnings.filterwarnings("ignore")

engine = create_engine("sqlite:///SQLRAG.db")

st.title("Le Chat du CSV et L'Agent SQL")

if "messages_Agent_SQL" not in st.session_state:
    st.session_state["messages_Agent_SQL"] = [{"role": "assistant", "content": "Téléchargez un fichier CSV et posez vos questions!"}]

uploaded_file = st.file_uploader("Déposez un CSV", type=("csv"))

for msg in st.session_state.messages_Agent_SQL:
    st.chat_message(msg["role"]).write(msg["content"])

# Demander le nom de la table à l'utilisateur
if uploaded_file is not None:
    table_name = st.text_input("Avant de poser votre question, entrez le nom de la table dans laquelle vous souhaitez stocker les données CSV:")
    
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
            df.to_sql(table_name, con = engine, index=False, if_exists="replace")
            
            # Afficher le chat seulement si le nom de la table est spécifié
            if table_name and table_name != "":
                # Figer l'aperçu du fichier en haut
                if "csv_preview" not in st.session_state:
                    st.session_state["csv_preview"] = df.head(5)
                
                # Afficher le prompt pour les questions
                if prompt := st.chat_input("Posez une question sur votre CSV"):
                    st.session_state.messages_Agent_SQL.append({"role": "user", "content": prompt})
                    st.chat_message("user").write(prompt)
                    
                    # Stockés les données du csv dans un DB
                    prompt_template = ChatPromptTemplate.from_template("""
                    Tu es un assistant intelligent et perspicace qui répond aux questions en utilisant les informations disponibles.
                    Utilise principalement les informations du contexte pour fournir une réponse précise et concise à la question de l'utilisateur.

                    Contexte :
                    {context}

                    Question de l'utilisateur :
                    {question}
                    """)
                    llm = ChatOllama(model='llama3.2')
                    db = SQLDatabase.from_uri("sqlite:///SQLRAG.db")
                    db_chain = SQLDatabaseChain.from_llm(llm, db, verbose = True, return_direct = True)
                    query_SQL = db_chain.invoke(prompt)
                    chain = (
                        RunnableMap({
                            "context": RunnableLambda(lambda _: query_SQL['result']),
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
                    
                    st.session_state.messages_Agent_SQL.append({"role": "assistant", "content": full_response})
        except pd.errors.EmptyDataError:
            st.error("Erreur: Le fichier CSV ne contient aucune donnée lisible.")
        except Exception as e:
            st.error(f"Une erreur est survenue: {e}")
