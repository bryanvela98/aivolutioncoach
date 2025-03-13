# Import Azure Cognitive Search, OpenAI, and other python modules

import os, json, requests, sys, re
import requests
from pprint import pprint
import pandas as pd
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient 
from azure.search.documents import SearchClient
""" from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    SemanticConfiguration,
    PrioritizedFields,
    SemanticField,
    SemanticSettings
) """

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

def realizar_prueba_educativa():
    """
    Realiza una prueba simple para demostrar el funcionamiento de embeddings y similitud
    """
    try:
        # Textos de ejemplo relacionados con programación
        textos = [
            "Python es un lenguaje de programación muy popular",
            "Java es un lenguaje de programación orientado a objetos",
            "Los gatos son mascotas muy independientes",
            "Los perros son mascotas muy fieles",
            "La programación en Python es fácil de aprender"
        ]
        
        print("\n=== PRUEBA DE EMBEDDINGS Y SIMILITUD SEMÁNTICA ===\n")
        
        # Obtener embeddings para todos los textos
        embeddings = []
        for texto in textos:
            print(f"Generando embedding para: '{texto}'")
            embedding = get_embedding(texto)
            embeddings.append(embedding)
            
        # Comparar similitudes
        print("\nComparando similitudes entre textos:")
        for i in range(len(textos)):
            for j in range(i + 1, len(textos)):
                similitud = cosine_similarity(embeddings[i], embeddings[j])
                print(f"\nSimilitud entre:\n'{textos[i]}' y\n'{textos[j]}':\n{similitud:.4f}")
                
        print("\n=== FIN DE LA PRUEBA ===")
        
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")

# Ejecutar la prueba
if __name__ == "__main__":
    realizar_prueba_educativa()