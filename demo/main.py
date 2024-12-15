import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from tools.extract_tool import Extract_Tool
from tools.growth_tool import Growth_Tool
from tools import GrossmmarginpercTool, ExpensespercTool, TaxrateTool

# Step 1: Environment Configuration
def load_api_key(env_file='key.env'):
    load_dotenv(env_file)
    return os.getenv('open_ai_API_Key')

# Step 2: Tool Initialization
def initialize_tools():
    return [
        Extract_Tool,
        Growth_Tool,
        GrossmmarginpercTool,
        ExpensespercTool,
        TaxrateTool
    ]

# Step 3: LLM and Agent Initialization
def create_agent(key_string, tools):
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=key_string)
    prompt = hub.pull("hwchase17/structured-chat-agent")
    memory = ConversationBufferMemory(
        memory_key="chat_history", return_messages=True
    )
    agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=memory,
        handle_parsing_errors=True,
    )
    return agent_executor, memory

# Step 4: Chat Functionality
def handle_user_input(agent_executor, memory, user_input):
    memory.chat_memory.add_message(HumanMessage(content=user_input))
    response = agent_executor.invoke({"input": user_input})
    memory.chat_memory.add_message(AIMessage(content=response["output"]))
    return response["output"]

# Step 5: Streamlit Integration
def streamlit_ui(agent_executor, memory):
    import streamlit as st

    st.title("AI Assistant with LangChain")
    st.write("You can interact with the AI using the tools provided.")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "system", "content": "You are an AI assistant that can provide helpful answers using available tools."}
        ]

    user_input = st.text_input("User Input", "")
    if st.button("Submit"):
        if user_input.lower() == "exit":
            st.write("Session ended.")
            return

        st.session_state["messages"].append({"role": "user", "content": user_input})
        response = handle_user_input(agent_executor, memory, user_input)
        st.session_state["messages"].append({"role": "assistant", "content": response})

    for msg in st.session_state["messages"]:
        role = "User" if msg["role"] == "user" else "Assistant"
        st.write(f"{role}: {msg['content']}")

# Main Function
def main():
    # Load API key and initialize tools
    key_string = load_api_key()
    tools = initialize_tools()

    # Create the agent and memory
    agent_executor, memory = create_agent(key_string, tools)

    # Set up initial system message
    initial_message = "You are an AI assistant that can provide helpful answers using available tools.\nIf you are unable to answer, you can use the following tools: Extract_Tool, Growth_Tool, GrossmmarginpercTool, ExpensespercTool, TaxrateTool"
    memory.chat_memory.add_message(SystemMessage(content=initial_message))

    # Launch Streamlit UI
    streamlit_ui(agent_executor, memory)

if __name__ == "__main__":
    main()
