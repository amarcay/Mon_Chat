import streamlit as st
import warnings
from crewai import Agent, Task, Crew, LLM

# Désactiver les avertissements
warnings.filterwarnings('ignore')

st.title("Générateur de Rapport d'Article avec IA")

if "messages_Agent1" not in st.session_state:
    st.session_state["messages_Agent1"] = [{"role": "assistant", "content": "Entrez un sujet pour générer un article!"}]

for msg in st.session_state.messages_Agent1:
    st.chat_message(msg["role"]).write(msg["content"])

def create_agents():
    planner = Agent(
        role="Planificateur de contenu",
        goal="Planifier un contenu engageant et factuellement exact sur {sujet}",
        backstory="Vous travaillez sur la planification d'un article de blog sur {sujet}.",
        allow_delegation=False,
        verbose=True,
        llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    )
    
    writer = Agent(
        role="Rédacteur de contenu",
        goal="Rédiger un article d'opinion perspicace et factuellement exact sur {sujet}",
        backstory="Vous travaillez sur la rédaction d'un article basé sur le plan fourni.",
        allow_delegation=False,
        verbose=True,
        llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    )
    
    editor = Agent(
        role="Rédacteur en chef",
        goal="Éditer un article pour assurer son alignement avec le style rédactionnel.",
        backstory="Vous révisez l'article pour améliorer la clarté et la qualité du contenu.",
        allow_delegation=False,
        verbose=True,
        llm=LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    )
    
    return planner, writer, editor

def create_tasks(planner, writer, editor, sujet):
    plan = Task(
        description=f"Créer un plan détaillé pour un article sur {sujet}",
        expected_output="Un plan de contenu détaillé.",
        agent=planner
    )
    
    write = Task(
        description="Rédiger un article basé sur le plan fourni.",
        expected_output="Un article structuré avec introduction, développement et conclusion.",
        agent=writer
    )
    
    edit = Task(
        description="Revoir l'article pour améliorer son style et corriger les erreurs.",
        expected_output="Un article finalisé, prêt à être publié.",
        agent=editor
    )
    
    return [plan, write, edit]

if sujet := st.chat_input("Entrez le sujet de l'article :"):
    st.session_state.messages_Agent1.append({"role": "user", "content": sujet})
    st.chat_message("user").write(sujet)
    
    st.write("Génération en cours...")
    
    planner, writer, editor = create_agents()
    tasks = create_tasks(planner, writer, editor, sujet)
    
    crew = Crew(agents=[planner, writer, editor], tasks=tasks, verbose=True)
    result = crew.kickoff(inputs={"sujet": sujet})
    
    if hasattr(result, "raw"):
        result_text = result.raw
    else:
        result_text = str(result)
    
    full_response = ""
    response_placeholder = st.empty()
    
    for chunk in result_text.split("\n"):
        full_response += chunk + "\n"
        response_placeholder.chat_message("assistant").write(full_response)
    
    st.session_state.messages_Agent1.append({"role": "assistant", "content": full_response})
