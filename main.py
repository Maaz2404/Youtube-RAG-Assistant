from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_community.document_loaders import TextLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from youtube_transcript_api import YouTubeTranscriptApi
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os
from pinecone import Pinecone



from langchain_pinecone import PineconeVectorStore


load_dotenv()



embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

prompt = ChatPromptTemplate.from_template(
    """
    You are going to respond to user queries from a YouTube video transcript.
    You will only answer from the given context below.
    Answer "I don't know" if you are unable to answer using the context.

    Context: {context}
    User Query: {query}
    """
)

llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY"),
)

def get_transcript(video_id: str) -> str:
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([chunk["text"] for chunk in transcript_list])
    except Exception as e:
        print("Error fetching transcript:", e)
        return ""

def run_rag_pipeline(video_id: str, query: str) -> str:
    index_name = "yt-transcript"
    namespace = video_id  
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    # Check if namespace has already been indexed
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    already_indexed = namespace in stats.get("namespaces", {})
    
    if not already_indexed:
        print(f"Indexing transcript for video ID: {video_id}")
    
        full_transcript = get_transcript(video_id)

        from langchain_core.documents import Document

        docs = [Document(page_content=full_transcript)]


        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)
        PineconeVectorStore.from_documents(
        chunks,
        embedding_model,
        index_name=index_name,
        namespace=video_id,            # separate space per video
            
        )

    vectorstore = PineconeVectorStore(
        embedding=embedding_model,
        index_name=index_name,
        namespace=video_id,
    )
        
    retriever = vectorstore.as_retriever(k=4)

    def retrieve_context(inputs):
        q = inputs["query"]
        relevant_docs = retriever.invoke(q)
        return " ".join(doc.page_content for doc in relevant_docs)

    parallel_chain = RunnableParallel({
        'context': RunnableLambda(retrieve_context),
        'query': RunnablePassthrough()
    })

    parser = StrOutputParser()
    final_chain = parallel_chain | prompt | llm | parser

    return final_chain.invoke({"query": query})
