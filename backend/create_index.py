from azure.ai.formrecognizer import DocumentAnalysisClient
import os, json, requests
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from dotenv import load_dotenv
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

load_dotenv()

# Create an SDK client
service_endpoint = os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT")   
key = os.getenv("AZURE_COGNITIVE_SEARCH_KEY")
credential = AzureKeyCredential(key)

index_name = os.getenv("AZURE_COGNITIVE_SEARCH_DOC_INDEX_NAME")

index_client = SearchIndexClient(
    endpoint=service_endpoint, credential=credential)
print(index_client)

fields = [
    SimpleField(name="document_id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="page_number", type=SearchFieldDataType.Int64),
    SimpleField(name="file_path", type=SearchFieldDataType.String),
    SearchableField(name="document_name", type=SearchFieldDataType.String,
                searchable=True, retrievable=True),
    SearchableField(name="page_text", type=SearchFieldDataType.String,
                filterable=True, searchable=True, retrievable=True),
]

semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=PrioritizedFields(
        title_field=SemanticField(field_name="document_id"),
        prioritized_keywords_fields=[SemanticField(field_name="document_name")],
        prioritized_content_fields=[SemanticField(field_name="page_text")]
    )
)


# Create the semantic settings with the configuration
semantic_settings = SemanticSettings(configurations=[semantic_config])

# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields, semantic_settings=semantic_settings)
result = index_client.create_or_update_index(index)
print(f' {result.name} created')