import os
import re
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
import argparse
from langchain.chains import SequentialChain
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain

# Load environment variables
load_dotenv('key.env')
key_string = os.getenv('open_ai_API_Key')

# Load document from PDF
def docloader(file):
    loader_1 = PyPDFLoader(file)
    document_1 = loader_1.load()
    return document_1

# Find pages containing relevant sections
def page_finder(document):
    start_page = None
    end_page = None
    for doc in document:
        if doc.page_content.startswith("Item 8"):
            start_page = doc.metadata['page']
            break
    for doc in document:
        if doc.page_content.startswith("Item 9"):
            end_page = doc.metadata['page']
            break
    if start_page is None or end_page is None:
        raise ValueError("Could not find 'Item 8' or 'Item 9' in the document")
    return start_page, end_page

# Extract document pages between "Item 8" and "Item 9"
def page_executor(document):
    start_page, end_page = page_finder(document)
    extracted_documents = [doc for doc in document if start_page <= doc.metadata['page'] < end_page]
    return extracted_documents

# Main processing function
def main(filename):
    doc = docloader(filename)
    extract = page_executor(doc)

    # Define prompt for extraction
    extract_prompt = PromptTemplate(
        input_variables=["document"],
        template="""
        Extract the balance sheet, statement of operations, cashflow and shareholder's equity as a structured table.
        Include column names and all rows. Provide the table as a JSON object.
        Structure the table as follows:
        Item, Category, Subcategory, <Date1>, <Date2>, <Date3>...
        Document: {document}
        """
    )

    # Initialize LLM
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5, openai_api_key=key_string)

    # Create the first chain (for extraction)
    extract_chain = LLMChain(
        llm=llm,
        prompt=extract_prompt,
        output_key="balance_sheet"
    )

    # Define prompt for conversion to TSV
    convert_prompt = PromptTemplate(
        input_variables=["balance_sheet"],
        template="""
        Convert the following balance sheet, statement of operations, cashflow and shareholder's equity JSON into a TSV format.
        Return only the TSV data. Separate the 4 tables with headers.
        JSON: {balance_sheet}
        """
    )

    # Create the second chain (for conversion)
    convert_chain = LLMChain(
        llm=llm,
        prompt=convert_prompt,
        output_key="csv_output"
    )

    # Combine the chains using SequentialChain
    sequential_chain = SequentialChain(
        chains=[extract_chain, convert_chain],
        input_variables=["document"],
        output_variables=["csv_output"]
    )

    # Run the sequential chain with extracted document
    result = sequential_chain.run({"document": extract})
    print(result)
    # Save the result to a file
    file_name = 'filing_data/' + str(filename) + '_balance_sheet.tsv'
    with open(file_name, 'w') as file:
        file.write(result)

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Process a PDF file.")
    parser.add_argument('file_name', type=str, help='Name of the file to process')
    args = parser.parse_args()
    main(args.file_name)
