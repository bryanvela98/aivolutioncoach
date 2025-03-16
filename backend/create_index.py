from azure.ai.formrecognizer import DocumentAnalysisClient
import os
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
from dotenv import load_dotenv

def create_search_index(index_name: str = None, endpoint: str = None, key: str = None):
    """
    Creates or updates a search index in Azure Cognitive Search
    
    Parameters:
    -----------
    index_name : str
        Name of the index to create
    endpoint : str, optional
        Azure Cognitive Search endpoint. If None, reads from environment variable
    key : str, optional
        Azure Cognitive Search key. If None, reads from environment variable
    
    Returns:
    --------
    SearchIndex
        The created or updated search index
    """
    
    load_dotenv()
    
    # Use parameters or environment variables
    service_endpoint = endpoint or os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT")
    service_key = key or os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
    search_index_name = index_name or os.getenv("AZURE_COGNITIVE_SEARCH_DOC_INDEX_NAME")
    
    if not service_endpoint or not service_key:
        raise ValueError("Search endpoint and key must be provided either as parameters or environment variables")
    
    credential = AzureKeyCredential(service_key)
    index_client = SearchIndexClient(endpoint=service_endpoint, credential=credential)
    
    # Define the fields for the index
    fields = [
        SimpleField(name="document_id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int64),
        SimpleField(name="file_path", type=SearchFieldDataType.String),
        SearchableField(name="document_name", type=SearchFieldDataType.String,
                    searchable=True, retrievable=True),
        SearchableField(name="page_text", type=SearchFieldDataType.String,
                    filterable=True, searchable=True, retrievable=True),
    ]
    
    # Create semantic configuration
    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=PrioritizedFields(
            title_field=SemanticField(field_name="document_id"),
            prioritized_keywords_fields=[SemanticField(field_name="document_name")],
            prioritized_content_fields=[SemanticField(field_name="page_text")]
        )
    )
    
    # Create semantic settings
    semantic_settings = SemanticSettings(configurations=[semantic_config])
    
    # Create the index
    index = SearchIndex(
        name=search_index_name, 
        fields=fields, 
        semantic_settings=semantic_settings
    )
    
    # Create or update the index
    result = index_client.create_or_update_index(index)
    print(f'Index {result.name} created or updated successfully')
    
    return result

if __name__ == "__main__":
    # Create or update the search index
    create_search_index()
    