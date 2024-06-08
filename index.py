#from IPython.display import Image
from pprint import pprint
import torch
#import rich
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
Linkin Park""".split("\n")

raw_docs=[]

for title in favourite_bands:
    page = wikipedia.page(title=title, auto_suggest=False)
    doc = Document(content=page.content, meta={"title": page.title, "url":page.url})
    raw_docs.append(doc)

print(raw_docs)
print(type(raw_docs))
print(type(raw_docs[0]))

# Indexing Pipeline
from haystack import Pipeline
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.preprocessors import DocumentCleaner, DocumentSplitter
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils import ComponentDevice

document_store = InMemoryDocumentStore(embedding_similarity_function="cosine")
indexing = Pipeline()
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
pprint(document_store.filter_documents()[0])
print(len(document_store.filter_documents()[0].embedding)) # embedding size