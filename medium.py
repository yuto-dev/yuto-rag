from haystack.nodes import Crawler
url = "https://airflow.apache.org/docs/apache-airflow-providers-google/stable/operators/cloud/index.html"
crawler = Crawler(output_dir="data/crawled_gcp", crawler_depth=1)
crawled_docs = crawler.crawl(urls=[url])

import os
json_files = []
for crawled_doc in crawled_docs:
    # Extract name from file path
    name = os.path.splitext(os.path.basename(str(crawled_doc)))[0]
    # Load file and add 'name' key-value pair to 'meta'
    with open(crawled_doc) as f:
        file_data = json.load(f)
        file_data['meta']['name'] = name
        json_files.append(file_data)

from haystack.nodes import PreProcessor
preprocessor = PreProcessor(
    clean_empty_lines=True,
    clean_whitespace=True,
    clean_header_footer=False,
    split_by="word",
    split_length=100,
    split_respect_sentence_boundary=True
)

docs = preprocessor.process(json_files)

from qdrant_haystack.document_stores import QdrantDocumentStore
document_store = QdrantDocumentStore(host="your-qdrant-instance-prefix.cloud.qdrant.io",
                                     api_key="your_api_key",
                                     https=True,
                                     index="airflowDocs",
                                     embedding_dim=768,
                                     recreate_index=True,
                                     timeout=120,
                                     grpc_port=6334,
                                     prefer_grpc=True )
document_store.write_documents(docs)