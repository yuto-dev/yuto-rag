from pprint import pprint
import rich
# Indexing Pipeline
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.utils import ComponentDevice
from haystack_integrations.document_stores.qdrant import QdrantDocumentStore

from haystack_integrations.components.generators.llama_cpp import LlamaCppGenerator

from fastapi import FastAPI, Form

app = FastAPI()

document_store = QdrantDocumentStore(
    path="qdrant/storage_local",
    index="Document",
    embedding_dim=1024,
    recreate_index=True,
    hnsw_config={"m": 16, "ef_construct": 64}  # Optional
)


# RAG Pipeline
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
rag.add_component("retriever", QdrantEmbeddingRetriever(document_store=document_store, top_k=5))
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

@app.get("/v1/completions")
async def completions(query: str):

    results = rag.run({
      "text_embedder": {"text": query},
      "prompt_builder": {"query": query}
    }
    )

    answer = results["llm"]["replies"][0]
    rich.print(answer)
    sourcesPlaceholder = ["Source 1", "Source 2"]

    return {"response": answer, "sourcesList": sourcesPlaceholder}

if __name__ == "__main__":
    # Run the FastAPI server
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)