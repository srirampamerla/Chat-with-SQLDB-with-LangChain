import streamlit as st
from pathlib import Path
from langchain.agents import create_sql_agent
from langchain.sql_database import SQLDatabase
from langchain.agents.agent_types import AgentType
from langchain.callbacks import StreamlitCallbackHandler
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from sqlalchemy import create_engine
import sqlite3
from langchain_groq import ChatGroq


st.set_page_config(page_title="Langchain : Chat with SQL DB",page_icon="🦜️")
st.title("🦜️ LangChain: Chat with SQL DB")

# Major problem with chat with SQL DB is that there may be some kind of vulnerable prompt injection(kinds of wrning we can give that) 

# INJECTION_WARNING="""
#                     SQL agent can be vulnerable to prompt injection. Use a DB role with limit permissions.
#                     Read more [here] (https://python.langchain.com/docd/security)."""

LOCALDB="USE_LOCALDB"
MYSQL="USE_MYSQL"

radio_opt=["Use SQL lite 3 Database- Student.db","Connect to you SQL Database"]

Selected_opt=st.sidebar.radio(label="Choose the DB which you want to chat",options=radio_opt)

if radio_opt.index(Selected_opt)==1:
    db_uri=MYSQL
    mysql_host=st.sidebar.text_input("provide MY SQL Host")
    mysql_user=st.sidebar.text_input("MY SQL USER")
    mysql_password=st.sidebar.text_input("MYSQL Password",type="password")
    mysql_db=st.sidebar.text_input("MYSQL Database")

else:
    db_uri=LOCALDB

api_key=st.sidebar.text_input(label="Groq API  key",type="password")

if not db_uri:
    st.info("Please Enter the database Information and uri")

if not api_key:
    st.info("Please Add Groq API key")

## LLM Model

llm=ChatGroq(groq_api_key=api_key,model_name="Llama3-8b-8192",streaming=True)

@st.cache_resource(ttl="2h")
def configure_db(db_uri,mysql_host=None,mysql_user=None,mysql_password=None,mysql_db=None):
    if db_uri==LOCALDB:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator=lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro",uri=True)
        return SQLDatabase(create_engine("sqlite:///",creator=creator))
    elif db_uri==MYSQL:
        if not(mysql_host and mysql_user and mysql_password and mysql_db):
            st.error("please Provide all MYSQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"mysql+mysqlconnector://{mysql_user}:{mysql_password}@{mysql_host}/{mysql_db}"))

if db_uri==MYSQL:
    db=configure_db(db_uri,mysql_host,mysql_user,mysql_password,mysql_db)
else:
    db=configure_db(db_uri)

## Toolkit 

toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION
)

if "messages" not in st.session_state or st.sidebar.button("clear Message History"):
    st.session_state["messages"]=[{"role":"assistant","content":"How Can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the databse")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)

# To run this streamlit run app.py
# In case any issues with requirements SQLAlchemy,mysql-connector-python 
