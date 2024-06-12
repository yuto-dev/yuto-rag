# yuto-rag
This is a RAG system built with Haystack that consists of two distinct pipelines. The indexing pipeline takes in PDF files, creates vector embeddings of the files' contents, and stores them in a Qdrant vector database. The RAG pipeline retrieves information from the embeddings and concatenate them into a template as context alongside user prompt. This leads to better generated responses from the LLM as it provides the LLM with clear context go guide it in the right direction.
