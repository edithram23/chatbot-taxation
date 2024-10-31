# PDF to Qdrant Vector Store

## Overview

This script is used for splitting PDF documents into text chunks, generating embeddings using OpenAI, and uploading them to a Qdrant vector database for semantic search. It supports handling a large collection of PDF files, generating unique vector embeddings, and efficiently uploading them to Qdrant for similarity search purposes.

## Features

- Splits PDF documents into manageable chunks using `RecursiveCharacterTextSplitter`.
- Generates embeddings using OpenAI's embedding model (`text-embedding-3-large`).
- Uploads documents and their vector embeddings to a Qdrant vector database.
- Handles multiple directories containing PDF files.

## Dependencies

Install all dependencies using the following command:

```sh
pip install -r requirements.txt
```

## How to Use

1. **Configure Environment Variables:**

   Create an `.env` file in the root directory and provide the following keys:

   ```plaintext
   QDRANT_URL=<your_qdrant_url>
   QDRANT_API_KEY=<your_qdrant_api_key>
   OPENAI_API_KEY=<your_openai_api_key>
   ```

2. **Initialization**

   The `vector_db` class initializes key components such as the Qdrant and OpenAI clients.

   ```python
   vec = vector_db()
   ```

3. **Upload PDFs to Qdrant**

   Uploads PDF documents to a Qdrant vector database. Files are loaded and split, embeddings are generated, and they are uploaded to Qdrant.

   ```python
   vec.upload_pdfs('your_collection_name')
   ```

4. **Script Description**

   - `upload_pdfs_user(path, delete=False)`: Uploads PDFs to the "siel-ai-user" collection.
   - `upload_pdfs(collection_name)`: Uploads PDFs to a specific collection, for example, "siel-ai-assignment".

   The script also checks if a collection exists before creating a new one.

```
```

## Example Usage

An example usage of the `vector_db` class to upload a specific folder of PDFs:

```python
vec = vector_db()
vec.upload_pdfs_user(path='data/CA/Final_CA/Taxation-Goods-and-service-Tax', delete=True)
```

## Notes

- `uuid4` is used to generate unique document IDs.
- Each chunk of text has its own unique embedding to facilitate better semantic search.

##
