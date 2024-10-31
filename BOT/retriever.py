import os
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from langchain_qdrant import QdrantVectorStore
from qdrant_client.http import models
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env')

class Retriever():
    def __init__(self):
        # Initialize Qdrant client
        qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        # Initialize Qdrant vector store
        self.vector_store = QdrantVectorStore(
            client=qdrant_client,
            collection_name="siel-ai-assignment",
            embedding=OpenAIEmbeddings(),
        )
        self.vector_store_user = QdrantVectorStore(
            client=qdrant_client,
            collection_name="siel-ai-user",
            embedding=OpenAIEmbeddings(),
        )
        self.filters = ['Taxation-Goods-and-service-Tax',
                        'Taxation-INCOME-TAX-LAW',
                        'Direct Tax Laws and International Taxation',
                        'Indirect Tax Laws',
                        'INDIAN Income Tax ACTS',
                        'ONLINESITES']
        self.groq = ChatGroq(model='llama3-70b-8192')

    
    
    def multi_questions(self,user_prompt):
        llm = self.groq
        prompt = f'''
# You are an excellent Query Decomposer for database retrieval optimization.
# You are given a user_query.
===============================
# TASK:
    -> Your task is to provide a structured and hierarchical breakdown of the user query.
    -> This breakdown should be in the form of an ordered sequence that helps in extracting the right context from the database.
    -> Build the user query from the bottom level (basic requirements) to the top level (more specific details), ensuring the retrieval context improves at each level.
===============================
# USER_QUERY: {{user}}
===============================
# EXAMPLE:
    1. #USER_QUERY: "For 5 lakh, what type of taxes should I pay and how much?"
       -> #EXPECTED OUTPUT: | I'm purchasing a car for 5 lakh. | What type of taxes should I pay on the purchase of automobiles? | What type of taxes should I pay on the purchase of a car for 5 lakh? |
    
    2. #USER_QUERY: "For 5 lakh, what type of taxes should I pay and how much?"
       -> #EXPECTED OUTPUT: | NEW TAX REGIME and Income tax. | My income is 5 lakh. What type of taxes should I pay and how much should I pay? |

===============================
# OUTPUT FORMAT:
    -> Provide the formatted output separated with the pipe '|' enclosed as: |...|...|
    -> Stick to the given format without any additional explanation. Your only response must be the formatted sequence of queries.
    -> Do not answer the user question directly. Your job is to provide the decomposed queries in the format shown in the examples.
'''

        rag_prompt = PromptTemplate.from_template(prompt)
        l = (rag_prompt | llm | StrOutputParser())
        stream = l.invoke({"user":user_prompt})
        return stream
    
    def multiple_contexts(self,user_prompt):
        questions = self.filters
        contexts = []
        for i in questions:
            contexts+=self.filter_multiple(user_prompt,i,18)
        return contexts
    
    def filter_multiple(self,query,mapper,k1=10):
        retriever1 = self.vector_store.as_retriever(
                                            search_type="similarity_score_threshold",
                                            search_kwargs={"k": k1,
                                                           'score_threshold':0.75,
                                                            'filter':models.Filter(must=[models.FieldCondition(key="metadata.DOCUMENT_IS_ABOUT", match=models.MatchValue(value=mapper),)])
                                                            },
                                        )
        ret = retriever1.invoke(query)
        return ret
    
    def filter(self,query,k1=10,k2=17):
        retriever1 = self.vector_store.as_retriever(
                                            search_type="mmr",
                                            search_kwargs={"k": k1,
                                                            'filter':models.Filter(must=[models.FieldCondition(key="metadata.DOCUMENT_IS_ABOUT", match=models.MatchValue(value=self.filters[-1]),)])
                                                            },
                                        )
        retriever2 = self.vector_store.as_retriever(
                                            search_type="mmr",
                                            search_kwargs={"k": k2,
                                                            'filter':models.Filter(must_not=[models.FieldCondition(key="metadata.DOCUMENT_IS_ABOUT", match=models.MatchValue(value=self.filters[-1]),)])
                                                           },
                                        )
        ret = retriever1.invoke(query)+retriever2.invoke(query)
        return ret

    def id_filter(self,query,id):
        retriever1 = self.vector_store_user.as_retriever(
                                            search_type="similarity_score_threshold",
                                            search_kwargs={"k": 10,
                                                           'score_threshold':0.7,
                                                            'filter':models.Filter(must=[models.FieldCondition(key="metadata.ID", match=models.MatchValue(value=id),)])
                                                            }
                                        )
        ret = retriever1.invoke(query)
        return ret

    def data_retrieve(self, query=''):
        retrieved_docs = self.vector_store.similarity_search_with_score(query, k=10)
        return [doc for doc, _ in retrieved_docs]

# ret = Retriever()
# print(ret.multiple_contexts("i'm purchasing a car for 5Lack, what type of taxes should I pay and how much?"))