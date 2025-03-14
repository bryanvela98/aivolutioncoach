# Import Azure Cognitive Search, OpenAI, and other python modules

import os, json, requests, sys, re
import requests
from pprint import pprint
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient 
from azure.search.documents import SearchClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SemanticConfiguration,
    PrioritizedFields,
    SemanticField,
    SemanticSettings
)
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from typing import List
import openai
from openai import OpenAI
import numpy as np
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
assert API_KEY, "ERROR: Azure OpenAI Key is missing"

RESOURCE_ENDPOINT = os.getenv("OPENAI_API_BASE", "").strip()
assert RESOURCE_ENDPOINT, "ERROR: Azure OpenAI Endpoint is missing"

EMBEDDING_NAME = os.getenv("EMBEDDING_MODEL_NAME", "").strip()
assert EMBEDDING_NAME, "ERROR: Embedding Model Name is missing"

try:
    # Crear el cliente de Azure OpenAI
    client = openai.AzureOpenAI(
        api_key=API_KEY,
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=RESOURCE_ENDPOINT
    )
except Exception as e:
    print(f"Error al crear el cliente de Azure OpenAI: {str(e)}")
    exit(1)
    
# Función para obtener embeddings
def get_embedding(text: str, embedding_name: str = EMBEDDING_NAME) -> List[float]:
    """
    Obtiene el embedding de un texto usando la API de OpenAI
    
    Args:
        text (str): Texto para obtener el embedding
        model (str): Modelo de embedding a usar
        
    Returns:
        List[float]: Vector de embedding
    """
    response = client.embeddings.create(
        model=embedding_name,
        input=text
    )
    return response.data[0].embedding

# Función para calcular similitud del coseno
def cosine_similarity(a: List[float], b: List[float]) -> float:
    """
    Calcula la similitud del coseno entre dos vectores
    
    Args:
        a (List[float]): Primer vector
        b (List[float]): Segundo vector
        
    Returns:
        float: Similitud del coseno entre los vectores
    """
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# -- raw data
RAW_DATA_FOLDER= 'backend/unstructured-data'
# -- extracted json file 
EXTRACTED_DATA_FOLDER = 'backend/data-extracted'

endpoint = os.environ["AZURE_FORM_RECOGNIZER_ENDPOINT"]
key = os.environ["AZURE_FORM_RECOGNIZER_KEY"]

document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)

def extract_local_single_file(file_name: str):
    not_completed = True
    while not_completed:
        with open(file_name, "rb") as f:
            poller = document_analysis_client.begin_analyze_document(
                "prebuilt-layout", document=f
            )
            not_completed=False
    result = poller.result()
    return get_page_content(file_name, result)

def extract_files( folder_name: str, destination_folder_name: str):
    os.makedirs(destination_folder_name, exist_ok=True)
    for file in os.listdir(folder_name):
        if file[-3:].upper() in ['PDF','JPG','PNG']:
            print('Processing file:', file, end='')
        
            page_content = extract_local_single_file(os.path.join(folder_name, file))
            output_file = os.path.join(destination_folder_name, file[:-3] +'json')
            print(f'  write output to {output_file}')
            with open(output_file, "w") as f:
                f.write(json.dumps(page_content))


def get_page_content(file_name:str, result):
    page_content = []
    for page in result.pages:
        all_lines_content = []
        for line_idx, line in enumerate(page.lines):
            all_lines_content.append(' '.join([word.content for word in line.get_words()]))
        page_content.append({'page_number':page.page_number, 
                                'page_content':' '.join(all_lines_content)})
    return {'filename':file_name, 'content':page_content}

# Ejecutar la prueba
if __name__ == "__main__":
    #realizar_prueba_educativa()
    #extract_files(RAW_DATA_FOLDER, EXTRACTED_DATA_FOLDER)
    
    documents=[]
    for file in os.listdir(EXTRACTED_DATA_FOLDER):
        with open(os.path.join(EXTRACTED_DATA_FOLDER, file)) as f:
            page_content= json.loads(f.read())
        documents.extend(
            [
                {
                    'document_id':page_content['filename'].split('\\')[-1].split('.')[0].replace(' ', '_') + '-' + str(page['page_number']),
                    'document_name':page_content['filename'].split('\\')[-1],
                    'file_path':page_content['filename'],              
                    'page_number':page['page_number'],
                    'page_text':page['page_content']
                }
                for page in page_content['content']
            ]
        )
    #Example of a single page of research paper file that will be indexed in Azure Cognitive Search
    #print(documents[17])
    
    
    # Create an SDK client
    service_endpoint = os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT")   
    key = os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
    credential = AzureKeyCredential(key)
    index_name = os.getenv("AZURE_COGNITIVE_SEARCH_DOC_INDEX_NAME")
    
    search_client = SearchClient(endpoint=service_endpoint, index_name=index_name, credential=credential)
    result = search_client.upload_documents(documents)  
    print(f"Uploaded {len(documents)} documents")  