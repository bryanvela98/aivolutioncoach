import os
import json
from typing import List, Dict
from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchableField,
    SearchFieldDataType
)
from dotenv import load_dotenv, find_dotenv

class DocumentProcessor:
    def __init__(self):
        """
        Inicializa el procesador de documentos usando configuración del ambiente
        """
        # Cargar y validar configuración
        self.config = self._load_environment()
        
        # Configurar carpetas
        self.raw_data_folder = self.config["RAW_DATA_FOLDER"]
        self.extracted_data_folder = self.config["EXTRACTED_DATA_FOLDER"]
        os.makedirs(self.extracted_data_folder, exist_ok=True)

        # Inicializar Document Intelligence client
        self.doc_client = DocumentAnalysisClient(
            endpoint=self.config["FORM_RECOGNIZER_ENDPOINT"],
            credential=AzureKeyCredential(self.config["FORM_RECOGNIZER_KEY"])
        )
        
        # Inicializar Search clients
        self.search_cred = AzureKeyCredential(self.config["SEARCH_KEY"])
        self.index_client = SearchIndexClient(
            endpoint=self.config["SEARCH_ENDPOINT"],
            credential=self.search_cred
        )
        self.search_client = SearchClient(
            endpoint=self.config["SEARCH_ENDPOINT"],
            index_name=self.config["SEARCH_INDEX_NAME"],
            credential=self.search_cred
        )
        
        self.index_name = self.config["SEARCH_INDEX_NAME"]

    def _load_environment(self) -> Dict[str, str]:
        """
        Carga y valida las variables de entorno necesarias
        """
        load_dotenv(find_dotenv())
        
        config = {
            # Azure Form Recognizer
            "FORM_RECOGNIZER_ENDPOINT": os.getenv("AZURE_FORM_RECOGNIZER_ENDPOINT"),
            "FORM_RECOGNIZER_KEY": os.getenv("AZURE_FORM_RECOGNIZER_KEY"),
            
            # Azure Cognitive Search
            "SEARCH_ENDPOINT": os.getenv("AZURE_COGNITIVE_SEARCH_ENDPOINT"),
            "SEARCH_KEY": os.getenv("AZURE_COGNITIVE_SEARCH_KEY"),
            "SEARCH_INDEX_NAME": os.getenv("AZURE_COGNITIVE_SEARCH_DOC_INDEX_NAME"),
            
            # Folders
            "RAW_DATA_FOLDER": "backend/unstructured-data",
            "EXTRACTED_DATA_FOLDER": "backend/data-extracted"
        }
        
        # Validación de variables requeridas
        required_vars = [
            "FORM_RECOGNIZER_ENDPOINT",
            "FORM_RECOGNIZER_KEY",
            "SEARCH_ENDPOINT",
            "SEARCH_KEY",
            "SEARCH_INDEX_NAME"
        ]
        
        missing_vars = [var for var in required_vars if not config[var]]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
        return config

    def extract_single_file(self, file_path: str) -> dict:
        """
        Extrae el contenido de un único archivo
        """
        try:
            with open(file_path, "rb") as f:
                poller = self.doc_client.begin_analyze_document(
                    "prebuilt-layout", 
                    document=f
                )
            result = poller.result()
            return self.get_page_content(file_path, result)
        except Exception as e:
            print(f"Error extracting file {file_path}: {str(e)}")
            raise

    def get_page_content(self, file_name: str, result) -> dict:
        """
        Obtiene el contenido de las páginas del resultado del análisis
        """
        page_content = []
        for page in result.pages:
            all_lines_content = []
            for line in page.lines:
                all_lines_content.append(' '.join([word.content for word in line.get_words()]))
            page_content.append({
                'page_number': page.page_number,
                'page_content': ' '.join(all_lines_content)
            })
        return {
            'filename': file_name,
            'content': page_content
        }

    def extract_files(self) -> None:
        """
        Extrae contenido de todos los archivos en la carpeta raw_data
        """
        for file in os.listdir(self.raw_data_folder):
            if file.upper().endswith(('.PDF', '.JPG', '.PNG')):
                print('Processing file:', file, end='')
                
                input_file = os.path.join(self.raw_data_folder, file)
                page_content = self.extract_single_file(input_file)
                
                output_file = os.path.join(self.extracted_data_folder, f"{file.rsplit('.', 1)[0]}.json")
                print(f'  write output to {output_file}')
                
                with open(output_file, "w") as f:
                    json.dump(page_content, f)

    def process_extracted_documents(self) -> List[dict]:
        """
        Procesa los documentos JSON extraídos y los prepara para subir
        """
        documents = []
        try:
            for file in os.listdir(self.extracted_data_folder):
                if file.endswith('.json'):
                    with open(os.path.join(self.extracted_data_folder, file)) as f:
                        page_content = json.load(f)
                    
                    documents.extend([
                        {
                            'document_id': f"{page_content['filename'].split('\\')[-1].split('.')[0].replace(' ', '_')}-{page['page_number']}",
                            'document_name': page_content['filename'].split('/')[-1],
                            'file_path': page_content['filename'],
                            'page_number': page['page_number'],
                            'page_text': page['page_content']
                        }
                        for page in page_content['content']
                    ])
            return documents
        except Exception as e:
            print(f"Error processing extracted documents: {str(e)}")
            raise

    def create_search_index(self) -> None:
        """
        Crea el índice de búsqueda si no existe
        """
        try:
            fields = [
                SimpleField(name="document_id", type=SearchFieldDataType.String, key=True),
                SimpleField(name="document_name", type=SearchFieldDataType.String),
                SimpleField(name="file_path", type=SearchFieldDataType.String),
                SimpleField(name="page_number", type=SearchFieldDataType.Int32),
                SearchableField(name="page_text", type=SearchFieldDataType.String)
            ]
            
            index = SearchIndex(name=self.index_name, fields=fields)
            self.index_client.create_or_update_index(index)
            print(f"Index '{self.index_name}' created or updated successfully")
        except Exception as e:
            print(f"Error creating index: {str(e)}")
            raise

    def upload_to_index(self, documents: List[dict]) -> None:
        """
        Sube documentos al índice de búsqueda
        """
        try:
            result = self.search_client.upload_documents(documents)
            print(f"Successfully uploaded {len(documents)} documents")
            return result
        except Exception as e:
            print(f"Error uploading documents: {str(e)}")
            raise

    def process_all(self) -> None:
        """
        Ejecuta el proceso completo de extracción, procesamiento e indexación
        """
        try:
            # 1. Extraer archivos
            print("1. Extracting files...")
            self.extract_files()
            
            # 2. Crear índice
            print("\n2. Creating search index...")
            self.create_search_index()
            
            # 3. Procesar documentos extraídos
            print("\n3. Processing extracted documents...")
            documents = self.process_extracted_documents()
            
            # 4. Subir al índice
            print("\n4. Uploading to search index...")
            self.upload_to_index(documents)
            
            print("\nComplete process finished successfully!")
            
        except Exception as e:
            print(f"Error in complete process: {str(e)}")
            raise

if __name__ == "__main__":
    try:
        # Crear instancia del procesador
        processor = DocumentProcessor()
        
        # Ejecutar proceso completo
        processor.process_all()
        
    except Exception as e:
        print(f"Error: {str(e)}")