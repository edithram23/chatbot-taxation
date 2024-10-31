from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from retriever import Retriever
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os
import io
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
from groq import Groq
import soundfile as sf
from deepgram import DeepgramClient, SpeakOptions
from langchain_groq import ChatGroq
import hashlib
import time
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv('.env')

class Script():
    def __init__(self):
        self.retriever = Retriever()
        self.openai_client = ChatOpenAI(model="gpt-4o-mini",temperature=0.1)
        self.groq = ChatGroq(model='llama3-70b-8192')
        self.groq1 = ChatGroq(model='llama3-8b-8192')	
        

    def format_docs(self,format_results,id=False):
        formatted_docs = []
        for i,doc in enumerate(format_results,start=1):
            if(id==True):
                metadata = doc.metadata['DOCUMENT_NAME']
            else:
                metadata = doc.metadata['DOCUMENT_IS_ABOUT']
            page = doc.page_content.strip()
            content = f"**DOC {i}. METADATA : This DOC is about {metadata} \n CONTENT:{page}**"
            formatted_docs.append(content)
        return "".join(formatted_docs)
    
    def history(self,hist):
        text = ''
        for i in hist:
            if(i['content']!='Sorry! Unable to find an answer for your question. Try Again.'):
                text += '|Role:'+i['role']+'Content:'+i['content']+'|'
    
    def gpt_loaders(self,query:str,history:str):
        template= f"""
                    # You are an excellent Question & Answering BOT based on Context.
                    # TASK : Given a question and the context, you are required to answer the question..
                    # User questions may be given as a user_query (or) User_question (or) User_scenario.
                    ===============================
                    #USER_QUERY :  {{question}}
                    ===============================
                    #METADATA_OF_CONTEXT :
                    -> The context given is related to INDIAN-TAXATION.
                    #CONTEXT : {{context}}
                    ===============================
                    You are also given previous ChatHistories (User question and corresponding AI answer) to you as extra data.
                    --# When to take the history as CONTEXT: Only if the history is relevant to the current question, you are permitted to take the chat history as a context.
                    --# If it is not relevant to the current question, do not take it.
                    #Chat History : {{history}}
                    ===============================
                    -> Don't provide your own answer that is not in the given context.
                    -> If you can provide a similar answer from the context that may be relevant but not exactly correct for the question, you can provide that answer.
                    -> Try to provide a proper output for the question. Don't explain any questions too lengthy max[100 words].
                    ===============================
                    # OUTPUT FORMAT:
                    -> Your output may be given to a voice model for a speech output. Try to be precise with your words. At the same time, fill the user with your answer.
                    -> Don't provide any further explanation apart from the answer output.
                    # STEP 1 : Generate a output for the query from the context:
                    # STEP 2 : -> Based on the current output check if it is relevant to the question again.
                               -> If you are not 100% able to answer the given question from the context => PROVIDE "Sorry! Unable to find an answer for your question. Try Again."

                """
        # template = f"""ANSWER THE USER QUESTION BASED ON THE GIVEN CONTEXT ALONE.
        #     UESR QUESTION : {{question}}
        #             CONTEXT : {{context}}
        #             {{history}}
        # """
        rag_prompt = PromptTemplate.from_template(template)
        rag_chain = (
                    rag_prompt
                    | self.openai_client
                    | StrOutputParser()
                    )
        question ={"context": self.format_docs(self.retriever.multiple_contexts(query)), "question": query, "history": history}
        return rag_chain,question
    
    def gpt_loaders_id(self,query:str,history:str,id:str):
        template= f"""
                    # You are an excellent Question & Answering BOT. Given a question and the context you will answer the question only based on the given context.
                    # You will be given a user_query (or) User_question (or) User_scenario.
                    # TASK: Your task is to provide an Answer to the USER_QUERY with the given CONTEXT_DATA.
                    ===============================
                    #USER_QUERY :  {{question}}
                    ===============================
                    #METADATA_OF_CONTEXT : -> The context given is a given from the user pdf input.
                                        -> Based on the user_query use the context accordingly.
                    #CONTEXT : {{context}}
                    ===============================
                    You are also given previous ChatHistories (User question and corressponding AI answer) to you as an extra data.
                    --# When to take the history as CONTEXT : Only if the history is relevant to the current question you are permitted to take the chat history as a context.
                    --# If it is not relevant to the current question do not take it.
                    #Chat History : {{history}}
                    ===============================
                    -> You are allowed to provide the answer only from the given context.
                    -> Don't provide your own answer that is not in the given context.
                    -> If you are not able to answer the given question from the context => PROVIDE "Sorry! Unable to find an answer for your question. Try Again."
                    -> Try to be a precise and provide a proper output for the question. Don't explain any questions too lengthy max[100 words].
                    -> Provide answer only to the question that is asked.
                    ===============================
                    # OUTPUT FORMAT:
                        -> Your output may be given to a voice model for a speech output. Try to be precise with your words. At the same time, fill the user with your answer
                        -> Don't provide any etc explanation apart from the answer output.
                """
        rag_prompt = PromptTemplate.from_template(template)
        rag_chain = (
                    rag_prompt
                    | self.groq
                    | StrOutputParser()
                    )
        question ={"context": self.format_docs(self.retriever.id_filter(query,id),id=True), "question": query, "history": history}
        return rag_chain,question

class Vector_db():
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1024,
                            chunk_overlap=256,
                            length_function=len,
                            is_separator_regex=False,
                            )
        self.qdrant_client = QdrantClient(
                        url=os.getenv("QDRANT_URL"),
                        api_key=os.getenv("QDRANT_API_KEY")
                    )
        self.openai_client = OpenAI()

    def get_embed(self, texts):
        return self.openai_client.embeddings.create(input = texts, model="text-embedding-3-large").data[0].embedding
    
    def text_split(self,full_text,meta):
        documents = self.text_splitter.create_documents([full_text],metadatas=[meta])
        return documents

    def load_data(self,pdf_path:str):
        loader = PyPDFLoader(pdf_path)
        file = loader.load()
        text = ''
        for i in file:
            text+=i.page_content
        return text
    
    def getdocs(self,about,filename):
        text = self.load_data(filename)
        data = (text+str(time.time())).encode('utf-8')
        identifier = hashlib.sha256(data).hexdigest()
        metadata = {'DOCUMENT_NAME':about,'ID':str(identifier)}
        documents = self.text_split(text,metadata)
        return documents,identifier
    
    def upload_pdfs_user(self,path,delete=False):
        if delete==True:
            if(self.qdrant_client.collection_exists("siel-ai-user")):
                    self.qdrant_client.delete_collection("siel-ai-user")
        if(not(self.qdrant_client.collection_exists("siel-ai-user"))):
            self.qdrant_client.create_collection(
                            collection_name="siel-ai-user",
                            vectors_config=VectorParams(size=1536,
                                                        distance=Distance.COSINE),
                                            )
        vector_store = QdrantVectorStore(
                        client=self.qdrant_client,
                        collection_name="siel-ai-user",
                        embedding=OpenAIEmbeddings(),
                                        )
        documents = []
        meta_data = os.path.basename(path)
        docs,identifier = self.getdocs(meta_data,path)
        documents+=docs
        # uuid4 is used to generate unique id number of documents to use that particular doc alone as context.
        ids = [str(uuid4())]*len(documents)
        vector_store.add_documents(documents=documents, ids=ids)
        return identifier

class Speech_Text():
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.deepgram = DeepgramClient(os.environ.get("VOICE_API_KEY"))
        self.options = SpeakOptions(
            model="aura-luna-en",
        )
        
    # Function to get transcript from audio
    def get_transcript(self,audio):
        audio_buffer = io.BytesIO()
        sf.write(audio_buffer, audio[1], samplerate=audio[0], format="MP3")
        audio_buffer.seek(0)
        translation = self.client.audio.transcriptions.create(
            file=("audio.mp3", audio_buffer.read()),
            model="distil-whisper-large-v3-en",
            response_format="json",
            temperature=0.0,
        )
        
        return translation.text

    # Function for speech synthesis
    def speech_synthesis(self,text: str):
        TEXT = {"text": text}
        FILENAME = "audio.mp3"
        try:
            self.deepgram.speak.v("1").save(FILENAME, TEXT, self.options)
            with open(FILENAME, "rb") as audio_file:
                audio_data = audio_file.read()
            return audio_data
        except Exception as e:
            print(f"Exception: {e}")
            return None
