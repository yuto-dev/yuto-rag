
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
  print(type(doc)) #dict
  #print(doc)
  print(doc.keys())
  print(type(doc['documents'])) #list
  print(type(doc['documents'][0])) #document
  
  print("-------------------------------------------------------------------------")
  raw_docs.append(doc['documents'][0])

#print(raw_docs)
#print(type(raw_docs))
print("=========================================================================")
print('READ HERE')
print(type(raw_docs[0]))
print(type(raw_docs[1]))
print("=========================================================================")

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

# RAG Pipeline
from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

generator = LlamaCppGenerator(
    model="content/zephyr-7b-beta.Q5_K_S.gguf", 
    n_ctx=2048,
    n_batch=128,
    model_kwargs={"n_gpu_layers": 32, "offload_kqv": True},
		generation_kwargs={"max_tokens": 1024, "temperature": 0.1},
)
generator.warm_up()

#Prompt Builder
from haystack.components.builders import PromptBuilder

prompt_template = """<|system|>Using the information contained in the context, give a comprehensive answer to the question.
If the answer is contained in the context, also report the source file path.
If the answer cannot be deduced from the context, do not give an answer.</s>
<|user|>
Context:
  {% for document in documents %}
    {{ document.content }}
  {% endfor %}
  Question: {{query}}
  </s>
<|assistant|>
"""
prompt_builder = PromptBuilder(template=prompt_template)

#RAG
from haystack_integrations.components.retrievers.qdrant import QdrantEmbeddingRetriever

rag = Pipeline()
rag.add_component("text_embedder", SentenceTransformersTextEmbedder(model="thenlper/gte-large",device=ComponentDevice.from_str("cuda:0")))
rag.add_component("retriever", QdrantEmbeddingRetriever(document_store=document_store))
rag.add_component("prompt_builder", prompt_builder)
rag.add_component("llm", generator)

rag.connect("text_embedder", "retriever")
rag.connect("retriever.documents", "prompt_builder.documents")
rag.connect("prompt_builder.prompt", "llm.prompt")

def get_generative_answer(query):

  results = rag.run({
      "text_embedder": {"text": query},
      "prompt_builder": {"query": query}
    }
  )

  answer = results["llm"]["replies"][0]
  print(answer)
  #print(results)

get_generative_answer("Who is Tom DeLonge?")

while True:
  prompt = input("Enter question: ")
  get_generative_answer(prompt)
