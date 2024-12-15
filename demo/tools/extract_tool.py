import json
from pydantic import BaseModel, Field
from langchain.tools import tool
# from utils.data_loader import load_json_data

class Extract_toolArgs(BaseModel):
    a: str = Field(description="Company name")
    b: str = Field(description="item")
    c: str = Field(description="Year_1")
    d: str = Field(description="Year_2")

import json
@tool(args_schema=Extract_toolArgs)
def Extract_Tool(a: str, b: str, c:str, d:str) -> Extract_toolArgs:
    """extracts specific data for a company from Year_1 to Year_2."""
    with open("data_soo.json","r") as json_file:
        data = json.load(json_file)
    
    a = a.upper()
    b = b.lower()
    json_data = next(item for item in data[a] if item["Item"] == b)
    
    year_data =[]
    cash_data = []
    
    # Ensure c and d represent years in the correct order
    if int(c) > int(d):
        c, d = d, c
    
    for year in range(int(c), int(d) + 1):
        value = json_data.get(str(year))
        if value is not None:
            cash_data.append(value)
            year_data.append(year)

            
    
    if len(cash_data) == 0:
        raise ValueError(f"Data for the years {c} to {d} is not available.")
    
    return cash_data,year_data
