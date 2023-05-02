import os
os.environ["OPENAI_API_KEY"] = "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"

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Pinecone

import pinecone

# initialize pinecone
pinecone.init(
    api_key="258a5561-3828-4a8e-9807-ad8df86ef5be",  # find at app.pinecone.io
    environment="eu-west1-gcp"  # next to api key in console
)
index = pinecone.Index("cosiw-project")

embeddings = OpenAIEmbeddings()
vectorstore = Pinecone(index, embeddings.embed_query, "text")

print(vectorstore.add_texts(["""Press start."""]))

docs = vectorstore.similarity_search_with_score("Press start")

print(docs)
