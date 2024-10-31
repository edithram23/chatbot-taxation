# Chatbot 
## Taxation RAG & ChatPDF

## Overview
This repository contains an AI chatbot application that uses Gradio to provide a user-friendly interface for interacting with a LLM which uses taxation data as context by default (RAG) and also supports users to upload PDF documents and chat with it. The bot accepts both text and voice inputs and can respond in both formats.

### Features
- **Conversational AI**: The chatbot is capable of conversing about Indian Taxation by default.
- **Voice and Text Inputs**: Accepts input through both microphone and text.
- **User-uploaded PDF Support**: Users can upload their own PDFs to use it like a NOTEBOOKLLM and can talk/chat with that as the knowledge base and query the chatbot regarding the content.

## Prerequisites
- Python 3.9 or higher
- Docker (optional for containerized deployment)
- Environment variables for API keys must be set in a `.env` file (see Environment Variables section below).

### Key Libraries
- `gradio`: Provides an interface for the chatbot.
- `deepgram`: Used for voice-to-text and text-to-speech operations.
- `langchain_openai`, `langchain_qdrant`: Used for managing the AI models and vector stores for efficient context retrieval.
- `qdrant-client`: Manages the vector database.

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/your_username/ai_chatbot.git
    cd ai_chatbot
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # Linux/macOS
    venv\Scripts\activate  # Windows
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file and add your environment variables (see below).

## Environment Variables
Create a `.env` file in the root directory of your project and add the following variables:
- `QDRANT_URL`: URL of your Qdrant instance.
- `QDRANT_API_KEY`: API key for Qdrant access.
- `VOICE_API_KEY`: API key for Deepgram or any other voice service.
- `GROQ_API_KEY`: API key for Groq service.

## Usage

1. Run the chatbot using the command below:
    ```sh
    python App.py
    ```
2. Access the Gradio UI from the URL displayed in your terminal (usually `http://localhost:80`).

### Chatbot Inputs
- **Textbox**: Type your queries related to taxation or the uploaded PDF.
- **Microphone**: Click on the microphone to record and submit a voice query.
- **PDF Upload**: Upload a PDF to add specific content for querying <=> NotebookLLM

### Chatbot Outputs
- **Text**: The assistant will reply to your query in the conversation box.
- **Voice**: You will also receive the response in an audio format.

## Deployment
This application can be accessed on Huggingface and on Azure.
HF might not contain latest version.
**Hugging Face** : ```https://huggingface.co/spaces/edithram23/Chatbot```<br>
**Azure** : ```https://siel-app-dughf2h6bvfvdtaf.centralindia-01.azurewebsites.net/```
```

## Project Structure
- **App.py**: Main file that initializes Gradio and handles user interaction.
- **Retriever.py**: Handles retrieval of data from Qdrant vector store.
- **Setup.py**: Provides utilities for embedding, formatting data, and integrating with the chatbot.
- **..\requirements.txt**: Lists all required Python packages.
