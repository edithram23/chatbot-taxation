"""
    This script splits PDF documents into chunks, generates embeddings using OpenAI (text-embedding-3-small), 
    and uploads them to a Qdrant vector database for efficient semantic search.
"""

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
import os
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from openai import OpenAI
from tqdm import tqdm
import glob
from uuid import uuid4
from dotenv import load_dotenv

load_dotenv('..\.env')
class vector_db():
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
                            chunk_size=1024,
                            chunk_overlap=256,
                            length_function=len,
                            is_separator_regex=False,
                            )
        # self.files = self.get_files()
        self.qdrant_client = QdrantClient(
                        url=os.getenv("QDRANT_URL"),
                        api_key=os.getenv("QDRANT_API_KEY")
                    )
        self.openai_client = OpenAI()

        
    def get_embed(self, texts):
        return self.openai_client.embeddings.create(input = texts, model="text-embedding-3-large").data[0].embedding

    def get_files(self):
        cur_folders = {
                'data\CA\Final_CA\Taxation-Goods-and-service-Tax':[],
                'data\CA\Final_CA\Taxation-INCOME-TAX-LAW':[],
                'data\CA\Inter_CA\Direct Tax Laws and International Taxation':[],
                'data\CA\Inter_CA\Indirect Tax Laws':[],
                'data\INDIAN Income Tax ACTS':[],
                'data\ONLINESITES':[]
              }
        for path in cur_folders.keys():
            cur_folders[path]=glob.glob(path+'/*.pdf')
        return cur_folders
    
    
    def text_split(self,full_text,path):
        documents = self.text_splitter.create_documents([full_text],metadatas=[{'DOCUMENT_IS_ABOUT':path}])
        return documents

    def load_data(self,pdf_path):
        loader = PyPDFLoader(pdf_path)
        file = loader.load()
        text = ''
        for i in file:
            text+=i.page_content
        return text
    
    def getdocs(self,meta,filename):
        text = self.load_data(filename)
        documents = self.text_split(text,meta)
        return documents
    
    def upload_pdfs_user(self,path,delete=False):
        if delete==True:
            if(self.qdrant_client.collection_exists("siel-ai-user")):
                    self.qdrant_client.delete_collection("siel-ai-user")
        
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
        docs = self.getdocs(meta_data,path)
        documents+=docs
        
        # uuid4 is used to generate unique id number of documents to use that particular doc alone as context.
        uid = str(uuid4())
        ids = [uid]*len(documents)
        vector_store.add_documents(documents=documents, ids=ids)
        return ids

    #Main function to get documents and upload them to QDRANT DB
    def upload_pdfs(self,collection_name):
        if self.qdrant_client.collection_exists("siel-ai-assignment"):
            # self.qdrant_client.delete_collection("siel-ai-assignment")
            print("Collection-EXISTS....!!!")
            # return
        
        print("Creating",collection_name)
        self.qdrant_client.create_collection(
                        collection_name="siel-ai-assignment",
                        vectors_config=VectorParams(size=1536,
                                                    distance=Distance.COSINE),
                                        )
        vector_store = QdrantVectorStore(
                        client=self.qdrant_client,
                        collection_name="siel-ai-assignment",
                        embedding=OpenAIEmbeddings(),
                                        )
        print("Uploading to ",collection_name)
        documents = []
        for path, filelist in tqdm(self.files.items()):
            meta_data = os.path.basename(path)
            for i in tqdm(filelist):
                docs = self.getdocs(meta_data,i)
                documents+=docs
        # uuid4 is used to generate unique id number of documents which is not needed
        ids = [str(uuid4()) for _ in range(len(documents))]
        print(f"Uploaded {len(documents)} records to 'siel-ai-assignment'")
        vector_store.add_documents(documents=documents, ids=ids)
        

         
vec = vector_db()
vec.upload_pdf('siel-ai-assignment')