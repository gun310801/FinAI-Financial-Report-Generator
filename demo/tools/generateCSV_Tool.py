import pandas as pd
import os
import io
from langchain.tools import tool
from pydantic import BaseModel, Field

# Tool schema for CSV generation
class GenerateCSVToolArgs(BaseModel):
    data: list = Field(description="List of data (list of dictionaries) to save as a CSV.")
    filename: str = Field(description="Desired filename for the CSV (without extension).")

@tool(args_schema=GenerateCSVToolArgs)
def GenerateCSV_Tool(data: list, filename: str) -> dict:
    """
    Generates a CSV file from the provided data and returns the path to download the file.
    """
    try:
        # Create a DataFrame from the data
        df = pd.DataFrame(data)
        
        # Define the path to save the CSV file
        file_path = f"/tmp/{filename}.csv"
        
        # Save the DataFrame as a CSV file
        df.to_csv(file_path, index=False)

        # Return the path to download the file
        return {'link': file_path}
    except Exception as e:
        return f"Error generating CSV: {str(e)}"