from services.transcript import get_transcript
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.runnable import RunnablePassthrough, RunnableLambda, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.retrievers.multi_query import MultiQueryRetriever
from dotenv import load_dotenv
import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore


os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

load_dotenv()

# ✅ Gemini Embedding Model (768-dim)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-exp-03-07",
    api_key=os.getenv("GEMINI_API_KEY")
)

# ✅ Prompt Template
prompt = ChatPromptTemplate.from_template(
    """
    You are going to respond to user queries from a YouTube video transcript.
    You will only answer from the given context below.
    Answer "I don't have enough information to answer that" if you are unable to answer using the context.

    Context: {context}
    User Query: {query}
    """
)

# ✅ Gemini LLM (Flash 1.5)
llm = GoogleGenerativeAI(
    model="gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# ✅ Main RAG function
def run_rag_pipeline(video_id: str, query: str) -> str:
    index_name = "yt-transcript"
    namespace = video_id  
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
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
            namespace=video_id,
        )

    vectorstore = PineconeVectorStore(
        embedding=embedding_model,
        index_name=index_name,
        namespace=video_id,
    )
    normal_retriever = vectorstore.as_retriever(k=4)
        
    summarize_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(search_type="mmr", k=10),
        llm=llm
    )

    def retrieve_context(inputs):
        q = inputs["query"]
        if any(kw in q.lower() for kw in ["summarize", "overview", "summary"]):
            relevant_docs = summarize_retriever.invoke(q)
            return " ".join(doc.page_content for doc in relevant_docs)
        relevant_docs = normal_retriever.invoke(q)
        return " ".join(doc.page_content for doc in relevant_docs)

    parallel_chain = RunnableParallel({
        'context': RunnableLambda(retrieve_context),
        'query': RunnablePassthrough()
    })

    parser = StrOutputParser()
    final_chain = parallel_chain | prompt | llm | parser

    return final_chain.invoke({"query": query})
