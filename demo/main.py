import os
from dotenv import load_dotenv
from langchain import hub
from langchain.agents import AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from tools import __all__
import streamlit as st
import matplotlib as plt
import io
import traceback

# Step 1: Environment Configuration
def load_api_key(env_file='key.env'):
    load_dotenv(env_file)
    return os.getenv('open_ai_API_Key')

# Step 2: Initialize Tools
def initialize_tools():
    tools = __all__
    return tools
    

# Step 3: Main Streamlit App
def main():

    def show_image(code):
        code = code.strip('```python')
        namespace = {"plt": plt, "io": io}
        try:
            # Safely execute the code
            exec(code, namespace)
            # Capture the graph and display it
            buffer = io.BytesIO()
            plt.savefig(buffer, format="png")
            buffer.seek(0)
            st.image(buffer, caption="Generated Graph")
            plt.close()
        except Exception as e:
            st.error("An error occurred while executing the graph code.")
            st.text(traceback.format_exc())

    # Load API key and tools
    api_key = load_api_key()
    tools = initialize_tools()
    
    # Initialize LLM and agent
    llm = ChatOpenAI(model="gpt-4o", openai_api_key=api_key, max_tokens=5000)
    prompt = hub.pull("hwchase17/structured-chat-agent")
    
    # Initialize memory in Streamlit
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory(
            memory_key="chat_history",  # Explicit key for memory storage
            return_messages=True
        )
        initial_message = "You are an AI assistant that can provide helpful answers using available tools. \nIf you are unable to answer, you can use the following tools:'Extract_Tool', 'Growth_Tool', 'GrossmmarginpercTool','ExpensespercTool','TaxrateTool','EBTTool','EPS_Tool','RNDGrowth_Tool','RNDTool','SNGTool','GenerateGraph_Tool'"

        # Add the system message to memory only once
        st.session_state.memory.chat_memory.add_message(
            SystemMessage(content=initial_message)
        )

    # Create the structured chat agent with memory
    agent = create_structured_chat_agent(llm=llm, tools=tools, prompt=prompt)
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True,
        memory=st.session_state.memory,  # Pass memory explicitly
        handle_parsing_errors=True,
    )

    # Streamlit UI
    st.title("AI Financial Assistant")

    # Display chat history excluding the system message
    for msg in st.session_state.memory.chat_memory.messages:
        if isinstance(msg, SystemMessage):
            continue  # Skip displaying the system message
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        st.chat_message(role).write(msg.content)

    # User input
    user_input = st.chat_input("Enter your query...")
    if user_input:
        # Add user input to memory
        # st.session_state.memory.chat_memory.add_message(HumanMessage(content=user_input))
        st.chat_message("user").write(user_input)
        
        # Get agent response
        # try:
        #     response = agent_executor.invoke({
        #         "input": user_input,
        #         "chat_history": st.session_state.memory.chat_memory.messages  # Pass memory explicitly
        #     })
        #     response_output = response.get("output", "Sorry, I couldn't generate a response.")
        # except Exception as e:
        #     response_output = f"Error: {str(e)}"
        try:
            response = agent_executor.invoke({
                "input": user_input,
                "chat_history": st.session_state.memory.chat_memory.messages  # Pass memory explicitly
            })
            
                # Check for executable code in the response
            if "code" in response:
                code = response["code"]
                show_image(code)
            elif "error" in response:
                # Handle error message
                st.chat_message("assistant").write(response["error"])
            else:
                # Handle normal text output
                response_output = response.get("output", "Sorry, I couldn't generate a response.")
                st.chat_message("assistant").write(response_output)
        except Exception as e:
            response_output = f"Error: {str(e)}"
            st.chat_message("assistant").write(response_output)  # Display error message
        # Add assistant response to memory
        # st.session_state.memory.chat_memory.add_message(AIMessage(content=response_output))

        # Display the latest assistant response
        st.chat_message("assistant").write(response_output)

if __name__ == "__main__":
    main()
