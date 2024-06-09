# Indexing Pipeline
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import ComponentDevice
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore
from haystack.components.converters import PyPDFToDocument
from pathlib import Path
import os

raw_docs = []

converter = PyPDFToDocument()

# Path to the directory containing PDF files
pdf_directory = Path("content/docs/")

# List all files in the directory
pdf_files = os.listdir(pdf_directory)

# Filter only PDF files
pdf_files = [file for file in pdf_files if file.lower().endswith(".pdf")]

# Loop through each PDF file
for pdf_file in pdf_files:
  pdf_path = pdf_directory / pdf_file
  doc = converter.run(sources=[pdf_path])
  raw_docs.append(doc['documents'][0])

document_store = QdrantDocumentStore(
    path="qdrant/storage_local",
    index="Document",
    embedding_dim=1024,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)
indexing = Pipeline()
#indexing.add_component("converter", PyPDFToDocument())
indexing.add_component("cleaner", DocumentCleaner())
indexing.add_component("splitter", DocumentSplitter(split_by='sentence', split_length=2))
indexing.add_component("doc_embedder", SentenceTransformersDocumentEmbedder(model="thenlper/gte-large",
                                                                            device=ComponentDevice.from_str("cuda:0"), 
                                                                            meta_fields_to_embed=["title"]))
indexing.add_component("writer", DocumentWriter(document_store=document_store, policy=DuplicatePolicy.OVERWRITE))

indexing.connect("cleaner", "splitter")
indexing.connect("splitter", "doc_embedder")
indexing.connect("doc_embedder", "writer")

indexing.run({"cleaner":{"documents":raw_docs}})
len(document_store.filter_documents())
document_store.filter_documents()[0].meta
print(document_store.filter_documents()[0])
print(len(document_store.filter_documents()[0].embedding)) # embedding size