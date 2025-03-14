import streamlit as st
import warnings
from crewai import Agent, Task, Crew, LLM
from crewai_tools import ScrapeWebsiteTool

# Désactiver les avertissements
warnings.filterwarnings('ignore')

st.title("Scraper et Analyse de Site Web avec IA")

if "messages_Agent2" not in st.session_state:
    st.session_state["messages_Agent2"] = [{"role": "assistant", "content": "Entrez une URL pour extraire et analyser le contenu !"}]

for msg in st.session_state.messages_Agent2:
    st.chat_message(msg["role"]).write(msg["content"])

def create_agents():
    scraper_tool = ScrapeWebsiteTool()
    
    scraper = Agent(
        role="Scraper Web",
        goal="Extraire le contenu textuel du site spécifié {url}",
        backstory="Un expert en extraction de données web.",
        allow_delegation=False,
        verbose=True,
        tools=[scraper_tool],
        llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    )
    
    analyzer = Agent(
        role="Analyste de Contenu",
        goal="Analyser le contenu extrait du site {url}",
        backstory="Un expert en résumé et analyse de texte.",
        allow_delegation=False,
        verbose=True,
        llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    )
    
    return scraper, analyzer

def create_tasks(scraper, analyzer, url):
    scrape_task = Task(
        description=f"Extraire le texte du site web {url}",
        expected_output="Contenu textuel brut du site.",
        agent=scraper
    )
    
    analyze_task = Task(
        description="Résumer le contenu extrait.",
        expected_output="Résumé les informations principales contenu extrait.",
        agent=analyzer
    )
    
    return [scrape_task, analyze_task]

if url := st.chat_input("Entrez l'URL du site à scraper :"):
    st.session_state.messages_Agent2.append({"role": "user", "content": url})
    st.chat_message("user").write(url)
    
    st.write("Extraction et analyse en cours...")
    
    scraper, analyzer = create_agents()
    tasks = create_tasks(scraper, analyzer, url)
    
    crew = Crew(agents=[scraper, analyzer], tasks=tasks, verbose=True)
    result = crew.kickoff(inputs={"url": url})
    
    if hasattr(result, "raw"):
        result_text = result.raw
    else:
        result_text = str(result)
    
    full_response = ""
    response_placeholder = st.empty()
    
    for chunk in result_text.split("\n"):
        full_response += chunk + "\n"
        response_placeholder.chat_message("assistant").write(full_response)
    
    st.session_state.messages_Agent2.append({"role": "assistant", "content": full_response})
