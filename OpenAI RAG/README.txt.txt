This project is aimed to learn about how to deploy AI and Embedding model to work together for an RAG-AI Architecture.

Objective:
- To make AI output grounded.
- To provide relevant context that is wanted to AI.

What’s Happening in the Index Creation Process?
Crack: This means the system extracts text from the PDF (often using OCR or PDF parsing tools).

Chunk: It breaks down the extracted text into manageable chunks (like paragraphs or sentences).

Embed: These chunks are converted into vector embeddings (numeric representations of meaning) using an AI model.

Create Index: These embeddings + metadata are stored in an Azure Cognitive Search index.

Register: The index is registered so it can be queried or used by other AI components.