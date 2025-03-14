import os
import json
import requests
import sys
import re
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
import numpy as np
from doc_intelligence import get_embedding, cosine_similarity
from dotenv import load_dotenv, find_dotenv

# Cargar variables de entorno
load_dotenv(find_dotenv())

# Configuración de Azure OpenAI
API_KEY = os.getenv("OPENAI_API_KEY")
RESOURCE_ENDPOINT = os.getenv("OPENAI_API_BASE", "").strip()
chat_model = os.getenv("CHAT_MODEL_NAME")
EMBEDDING_NAME = os.getenv("EMBEDDING_MODEL_NAME", "").strip()

# Validaciones
assert API_KEY, "ERROR: Azure OpenAI Key is missing"
assert RESOURCE_ENDPOINT, "ERROR: Azure OpenAI Endpoint is missing"
assert chat_model, "ERROR: CHAT_MODEL_NAME is missing in .env file"
assert EMBEDDING_NAME, "ERROR: Embedding Model Name is missing"

# Configuración de Azure Cognitive Search
service_endpoint = os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT")   
key = os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
index_name = os.getenv("AZURE_COGNITIVE_SEARCH_DOC_INDEX_NAME")

# Inicializar clientes
try:
    # Cliente de Azure OpenAI
    client = openai.AzureOpenAI(
        api_key=API_KEY,
        api_version=os.getenv("OPENAI_API_VERSION"),
        azure_endpoint=RESOURCE_ENDPOINT
    )
    
    # Cliente de Azure Cognitive Search
    credential = AzureKeyCredential(key)
    search_client = SearchClient(
        endpoint=service_endpoint, 
        index_name=index_name, 
        credential=credential
    )
except Exception as e:
    print(f"Error al inicializar clientes: {str(e)}")
    exit(1)



def get_chat_completion(prompt: str, model: str = chat_model, temperature: float = 0, 
                       max_tokens: int = 200, frequency_penalty: float = 0) -> str:
    """
    Gets a response from the chat model
    """
    try:
        messages = [
            {"role": "system", "content": '''You are AIvolution Coach, a professional and empathetic assistant 
                                          specialized in employability for people with disabilities.

                                          BEHAVIOR:
                                          - Use a friendly, respectful and motivating tone
                                          - Keep responses clear and structured 
                                          - Include relevant emojis to make communication more approachable
                                          - Be specific and concise in recommendations
                                          - Show empathy and understanding
                                          
                                          RESTRICTIONS:
                                          - Do not provide medical information
                                          - Do not make unrealistic employment promises
                                          - Do not discriminate based on disability type
                                          - If you don't have accurate information, clearly state it
                                          
                                          RESPONSE FORMAT:
                                          1. Personalized greeting with emoji
                                          2. Clear and structured response
                                          3. Key points or recommendations if applicable
                                          4. Motivational closing message'''},
            {"role": "user", "content": prompt}
        ]
        
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            frequency_penalty=frequency_penalty
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in get_chat_completion: {str(e)}")
        return None

def semantic_search(query: str, top_k: int = 3) -> pd.DataFrame:
    """
    Realiza una búsqueda semántica usando Azure Cognitive Search y embeddings
    """
    try:
        results = search_client.search(
            search_text=query, 
            top=10,
            include_total_count=True
        )
        
        page_chunks = []
        citations = []
        for result in results:
            page_chunks.append(result['page_text'])
            citations.append(result['document_name'])
            
        embed_df = pd.DataFrame({
            "page_chunks": page_chunks,
            "citations": citations
        })
        
        embed_df['embedding'] = embed_df["page_chunks"].apply(
            lambda text: get_embedding(text, embedding_name=EMBEDDING_NAME)
        )
        
        query_embedding = get_embedding(query, embedding_name=EMBEDDING_NAME)
        embed_df["similarities"] = embed_df['embedding'].apply(
            lambda embedding: cosine_similarity(embedding, query_embedding)
        )
        
        top_results = (
            embed_df.sort_values("similarities", ascending=False)
            .head(top_k)
            .reset_index(drop=True)
        )
        
        return top_results
        
    except Exception as e:
        print(f"Error en semantic_search: {str(e)}")
        return pd.DataFrame()

def generate_answer(query: str, context_results: pd.DataFrame) -> str:
    """
    Generates an answer based on search results
    """
    prompt = f"""
    As AIvolution Coach, use the following information to provide a helpful response:

    User Query: ```{query}```
    Context Information: ```{context_results['page_chunks'].to_list()}```
    Sources: ```{context_results['citations'].to_list()}```

    Requirements:
    1. Provide a clear and empathetic response
    2. Include specific recommendations if applicable
    3. Cite sources when possible
    4. Keep the response concise, brief and well-structured
    5. Use a motivating tone
    6. Include relevant emojis to make the response more engaging
    """
    
    return get_chat_completion(prompt, temperature=0.5)

def search_and_answer(query: str) -> str:
    """
    Función principal que combina búsqueda y generación de respuesta
    """
    try:
        search_results = semantic_search(query)
        
        if search_results.empty:
            return "Lo siento, no pude encontrar información relevante para tu consulta."
        
        answer = generate_answer(query, search_results)
        return answer
        
    except Exception as e:
        print(f"Error en search_and_answer: {str(e)}")
        return "Lo siento, ocurrió un error al procesar tu consulta."

# Ejemplo de uso
if __name__ == "__main__":
    query = "Who you are"
    response = search_and_answer(query)
    print(response)