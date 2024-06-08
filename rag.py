from IPython.display import Image
from pprint import pprint
import torch
import rich
import random
import wikipedia
from haystack.dataclasses import Document

favourite_bands="""Audioslave
Blink-182
Dire Straits
Evanescence
Green Day
Muse (band)
Nirvana (band)
Sum 41
The Cure
The Smiths
Dragonforce
Nissan Skyline GT-R
Gloryhammer
Nightwish
Linkin Park
Coldplay""".split("\n")

raw_docs=[]

for title in favourite_bands:
    page = wikipedia.page(title=title, auto_suggest=False)
    doc = Document(content=page.content, meta={"title": page.title, "url":page.url})
    raw_docs.append(doc)

# Indexing Pipeline
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import ComponentDevice
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

document_store = QdrantDocumentStore(
    path="qdrant/storage_local",
    index="Document",
    embedding_dim=1024,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)

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
If the answer is contained in the context, also report the source URL.
If the answer cannot be deduced from the context, do not give an answer.</s>
<|user|>
Context:
  {% for doc in documents %}
  {{ doc.content }} URL:{{ doc.meta['url'] }}
  {% endfor %};
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
  rich.print(answer)

import time
start_time = time.time()
get_generative_answer("Who is Herman Li?")
end_time = time.time()

# Calculate the difference in time
execution_time = end_time - start_time

# Print out the execution time in seconds
print("Execution time:", execution_time, "seconds")


while True:
  prompt = input("Enter question: ")
  start_time = time.time()
  get_generative_answer(prompt)
  end_time = time.time()

  # Calculate the difference in time
  execution_time = end_time - start_time

  # Print out the execution time in seconds
  print("Execution time:", execution_time, "seconds")
