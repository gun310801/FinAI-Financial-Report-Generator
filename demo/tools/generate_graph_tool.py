from pydantic import BaseModel, Field
import traceback
import matplotlib

import matplotlib.pyplot as plt
from langchain.tools import tool
import io
import os
from dotenv import load_dotenv
import openai
load_dotenv('key.env')  
key_string = os.getenv('open_ai_API_Key')

# Set your OpenAI API key
openai.api_key = key_string

class GenerateGraphToolArgs(BaseModel):
    data: list = Field(description="List of numerical values or metrics to plot.")
    labels: list = Field(description="List of labels (e.g., years, categories) corresponding to the data.")
    graph_type: str = Field(description="Type of graph, such as 'bar chart', 'line graph', or 'scatter plot'.")
    title: str = Field(description="Title of the graph.")

@tool(args_schema=GenerateGraphToolArgs)
def GenerateGraph_Tool(data: list, labels: list, graph_type: str, title: str) -> dict:
    """
    Generates Python code to create a graph (e.g., bar, line, scatter) using matplotlib based on user input.
    """
    prompt = (
        f"Generate Python code to create a '{graph_type}' using matplotlib. The graph should have the title '{title}', "
        f"the X-axis labels as {labels}, and the Y-axis values as {data}. Return only the code."
    )
    
    try:
        # Use OpenAI to generate code
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are an assistant that generates Python graph code using matplotlib."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        code = response.choices[0].message.content
        return {'code': str(code.strip())}
    except Exception as e:
        return f"Error generating graph code: {str(e)}"

### Step 2: Tool Schema for Executing Graph Code ###
# class ExecuteGraphToolArgs(BaseModel):
#     code: str = Field(description="The Python code to execute and display the graph.")

# @tool(args_schema=ExecuteGraphToolArgs)
# def ExecuteGraph_Tool(code: str) -> dict:
#     """
#     Executes the Python code to  display the graph.
#     """
#     code = code.strip('```python')
#     namespace = {"plt": plt, "io": io}
#     try:
#         # Safely execute the code
#         exec(code, namespace)
#         # Capture the graph and display it
#         buffer = io.BytesIO()
#         plt.savefig(buffer, format="png")
#         buffer.seek(0)
#         print(f"Buffer type: {type(buffer)}")
#         plt.close() 
#         return {"image_buffer": buffer}
#         # st.image(buffer, caption="Generated Graph")
#         # plt.close()
#     except Exception as e:
#         return ("An error occurred while executing the graph code."+traceback.format_exc())
#         # st.error("An error occurred while executing the graph code.")
#         # st.text(traceback.format_exc())

