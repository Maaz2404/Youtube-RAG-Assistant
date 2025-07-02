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
from sqlalchemy.orm import Session
import json
from models import Transcript
import time

os.environ["GEMINI_API_KEY"] = os.getenv("GEMINI_API_KEY")

load_dotenv()

# ✅ Gemini Embedding Model (768-dim)
embedding_model = GoogleGenerativeAIEmbeddings(
    model="models/embedding-001",
    api_key=os.getenv("GEMINI_API_KEY")
)
test_embed = embedding_model.embed_query("Hello, world!")
print(len(test_embed))

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
def run_rag_pipeline(video_id: str, user_id: int, query: str, db: Session, session_id: str, video_title: str, channel_name: str) -> str:
    index_name = "yt-transcript"
    use_user_namespace = False
    if user_id:
        transcript = db.query(Transcript).filter(
            Transcript.video_id == video_id,
            Transcript.user_id == str(user_id),
            Transcript.is_saved == True
        ).first()
        if transcript:
            use_user_namespace = True

    if use_user_namespace:
        namespace = f"{user_id}:{video_id}"
    else:
        namespace = f"{video_id}_temp"

    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    already_indexed = namespace in stats.get("namespaces", {})
    print(already_indexed)
    if not already_indexed:
        print(f"Indexing transcript for video ID: {video_id}")
        full_transcript = get_transcript(video_id)
        from langchain_core.documents import Document
        docs = [Document(page_content=full_transcript)]

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=100
        )
        chunks = splitter.split_documents(docs)
        vector_ids = []
        vectors = []
        for i, chunk in enumerate(chunks):
            vector_id = f"{video_id}_chunk_{i}"
            vector_ids.append(vector_id)
            chunk.metadata = chunk.metadata or {}
            chunk.metadata["text"] = chunk.page_content
            chunk.metadata["type"] = "chunk"
            vectors.append((vector_id, embedding_model.embed_query(chunk.page_content), chunk.metadata))

        index.upsert(vectors=vectors, namespace=namespace)

        # Upsert the "__index__" vector
        index_vector = ("__index__", [1.0] + [0.0]*767, {"vector_ids": json.dumps(vector_ids), "type": "index"})
        index.upsert(vectors=[index_vector], namespace=namespace)

        from services.transcript_ops import create_temp_transcript
        create_temp_transcript(db, session_id, video_id, video_title, channel_name)
        
    vectorstore = PineconeVectorStore(
    embedding=embedding_model,
    index_name=index_name,
    namespace=namespace,
)
      
    normal_retriever = vectorstore.as_retriever(
        search_type='mmr',
        search_kwargs={"k": 4, "filter": {"type": "chunk"}}
)

    summarize_retriever = MultiQueryRetriever.from_llm(
        retriever=vectorstore.as_retriever(
            search_type="mmr",
            search_kwargs={"k": 10, "filter": {"type": "chunk"}}
        ),
        llm=llm
    )

    def retrieve_context(inputs):
        q = inputs["query"]
        if any(kw in q.lower() for kw in ["summarize", "overview", "summary", "all", "complete"]):
            relevant_docs = summarize_retriever.invoke(q)
            if not relevant_docs:
                time.sleep(1)
                relevant_docs = summarize_retriever.invoke(q)
            print(relevant_docs)
            context = " ".join(doc.page_content for doc in relevant_docs)
            print(f"\n[DEBUG] Context for query '{q}':\n{context[:500]}{'...' if len(context) > 500 else ''}\n")
        else:
            relevant_docs = normal_retriever.invoke(q)
            if not relevant_docs:
                time.sleep(1)
                relevant_docs = summarize_retriever.invoke(q)
            print(relevant_docs)
            context = " ".join(doc.page_content for doc in relevant_docs)
            print(f"\n[DEBUG] Context for query '{q}':\n{context[:500]}{'...' if len(context) > 500 else ''}\n")  # Print first 500 chars for readability
        return context

    parallel_chain = RunnableParallel({
        'context': RunnableLambda(retrieve_context),
        'query': RunnablePassthrough()
    })

    parser = StrOutputParser()
    final_chain = parallel_chain | prompt | llm | parser

    return final_chain.invoke({"query": query})
def delete_embeddings(namespace):
    index_name = "yt-transcript"
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    index.delete(delete_all=True, namespace=namespace)
    print(f"Deleted embeddings for namespace: {namespace}")
    
def move_embeddings(old_namespace, new_namespace):
    import json
    index_name = "yt-transcript"
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    index = pc.Index(index_name)
    stats = index.describe_index_stats()
    
    print(f"Namespaces before move: {stats.get('namespaces', {}).keys()}")
    if old_namespace not in stats.get("namespaces", {}):
        print(f"No vectors found in namespace: {old_namespace}")
        return
    index_vector = index.fetch(ids=["__index__"], namespace=old_namespace).vectors.get("__index__")
    if not index_vector:
        print(f"No index vector found in namespace: {old_namespace}")
        return
    try:
        vector_ids = json.loads(index_vector["metadata"]["vector_ids"])
        print(f"Vector IDs to move: {vector_ids}")

        vectors = index.fetch(ids=vector_ids, namespace=old_namespace).vectors
        print(f"Fetched {len(vectors)} vectors from {old_namespace}")

        upsert_data = []
        for k, v in vectors.items():
            metadata = getattr(v, "metadata", {}) or {}
            if k == "__index__":
                metadata["type"] = "index"
            else:
                metadata["type"] = "chunk"
            upsert_data.append((k, v.values, metadata))
        print(f"Upserting {len(upsert_data)} vectors to {new_namespace}")

        index.upsert(vectors=upsert_data, namespace=new_namespace)

    except Exception as e:
        print(f"Error occurred while moving embeddings: {e}")
        return f"Error occurred while moving embeddings: {e}"

    index.delete_namespace(namespace=old_namespace)
    print(f"Deleted namespace {old_namespace}")

    stats_after = index.describe_index_stats()
    print(f"Namespaces after move: {stats_after.get('namespaces', {}).keys()}")
    return f"Moved embeddings from {old_namespace} to {new_namespace} and deleted old namespace."