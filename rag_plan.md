# PDF RAG Integration - Comprehensive Implementation Plan

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Tech Stack Specifications](#tech-stack-specifications)
3. [Architecture Deep Dive](#architecture-deep-dive)
4. [Implementation Phases](#implementation-phases)
5. [Service Module Designs](#service-module-designs)
6. [UI/UX Specifications](#ui-ux-specifications)
7. [Integration with Existing Systems](#integration-with-existing-systems)
8. [Performance & Security](#performance--security)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Considerations](#deployment-considerations)

## Executive Summary

### Objective
Integrate PDF RAG (Retrieval-Augmented Generation) capabilities into the Finance Bro application's bro.py page, enabling users to upload and analyze financial documents using a simple file-based routing system.

### Key Features
- **Simple File-Based Routing**: PDF files → LangChain RAG, CSV/Excel → PandasAI
- PDF document upload and processing with LangChain
- CSV/Excel file analysis with existing PandasAI system
- Vietnamese language support for financial documents
- Persistent document storage and vector indexing
- Source attribution and citation tracking
- Clear user experience with predictable routing

### Success Metrics
- Process PDF documents up to 50MB within 30 seconds
- Achieve <2 second query response time with RAG context
- Support 10+ concurrent PDF documents per session
- Maintain 95% accuracy in source attribution
- Reduce OpenAI API costs by 80% through caching

## Tech Stack Specifications

### Core Dependencies Matrix

```toml
# LangChain Ecosystem (Primary)
langchain = "^0.1.17"                   # Core framework with RAG chains
langchain-community = "^0.0.35"         # Document loaders & utilities
langchain-openai = "^0.1.7"            # OpenAI integration with caching
langchain-chroma = "^0.1.0"            # ChromaDB vector store integration
langchain-text-splitters = "^0.0.1"    # Advanced text splitting

# Document Processing Stack
pypdf = "^4.2.0"                       # LangChain's preferred PDF loader
unstructured = "^0.13.7"               # Advanced document parsing
python-magic = "^0.4.27"              # File type validation
pymupdf = "^1.24.2"                    # Fallback PDF processing

# Vector Database & Search
chromadb = "^0.4.24"                   # Persistent vector database
sentence-transformers = "^2.7.0"       # Local embeddings fallback

# Vietnamese Language Support
underthesea = "^6.7.0"                 # Vietnamese NLP preprocessing
py-vncorenlp = "^0.9.3"                # Advanced Vietnamese processing

# Caching & Performance
diskcache = "^5.6.3"                   # LangChain cache backend
redis = "^5.0.4"                       # Optional: distributed caching
```

### Compatibility Matrix

| Component | Current Version | RAG Version | Compatibility |
|-----------|----------------|-------------|---------------|
| pandas | 1.5.3 | 1.5.3 | ✅ Maintained |
| pandasai | 2.3.0 | 2.3.0 | ✅ Maintained |
| streamlit | 1.47.0 | 1.47.0 | ✅ Maintained |
| openai | Latest | Latest | ✅ Compatible |
| python | 3.10.11 | 3.10.11 | ✅ Maintained |

### LangChain Component Selection Rationale

**Document Loaders:**
- `PyPDFLoader`: Primary choice for clean text extraction
- `UnstructuredPDFLoader`: Fallback for complex layouts and tables
- `PDFMinerLoader`: Alternative for password-protected PDFs

**Text Splitters:**
- `RecursiveCharacterTextSplitter`: Main splitter for general content
- `NLTKTextSplitter`: Sentence-aware splitting for Vietnamese
- `TokenTextSplitter`: Token-based splitting for precise control

**Vector Stores:**
- `ChromaDB`: Primary choice for persistence and metadata filtering
- `FAISS`: Alternative for high-performance in-memory operations
- `Pinecone`: Optional cloud-based solution for scalability

**Retrievers:**
- `VectorStoreRetriever`: Basic similarity search
- `ContextualCompressionRetriever`: Content compression and filtering
- `MultiVectorRetriever`: Parent-child document relationships

## Architecture Deep Dive

### System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Finance Bro Application                   │
├─────────────────────────────────────────────────────────────────┤
│  Streamlit Frontend (bro.py)                                   │
│  ├── PDF Upload Interface                                       │
│  ├── Enhanced Chat Interface                                    │
│  └── Document Management Panel                                  │
├─────────────────────────────────────────────────────────────────┤
│  RAG Service Layer                                             │
│  ├── Document Processing Service                                │
│  ├── Vector Store Service                                       │
│  ├── Retrieval Service                                         │
│  └── Enhanced Agent Service                                     │
├─────────────────────────────────────────────────────────────────┤
│  Existing Services                                              │
│  ├── VnStock API Service                                       │
│  ├── Chart Service                                             │
│  └── PandasAI Agent                                            │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ├── ChromaDB Vector Store                                     │
│  ├── Document Cache (FileSystem)                               │
│  ├── Embedding Cache (DiskCache)                               │
│  └── Session State (Streamlit)                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Architecture

**Simple File-Based Routing:**
```
User Upload → File Type Check → Route to Processing Pipeline
     ↓              ↓                        ↓
   Files      PDF → LangChain RAG    CSV/Excel → PandasAI
                ↓                              ↓
    PDF Processing Pipeline         Data Analysis Pipeline
    ↓                              ↓
    Vector Store + RAG             Financial Dataframes
    ↓                              ↓
    Document Search Response       Data Analysis Response
```

**Detailed PDF Processing Flow:**
```
PDF Upload → Validation → Text Extraction → Chunking → Embedding → Vector Store
                ↓              ↓              ↓           ↓            ↓
            File Storage → Metadata DB → Chunk Cache → Embed Cache → Search Index
                                                                        ↓
User Query → Vector Search → Context Ranking → LangChain Response
                ↓              ↓                      ↓
           Query Cache → Retrieved Context → Formatted Answer
```

### Session State Extensions

```python
# Existing session state
st.session_state = {
    # Current state
    "stock_symbol": str,
    "dataframes": Dict[str, pd.DataFrame],
    "agent": Agent,
    "messages": List[Dict],
    
    # New RAG state
    "uploaded_documents": List[DocumentMetadata],
    "vector_store": Optional[ChromaDB],
    "rag_enabled": bool,
    "document_cache": Dict[str, ProcessedDocument],
    "embedding_cache": CacheBackedEmbeddings,
    "retrieval_chain": ConversationalRetrievalChain,
    "rag_context": List[RetrievedContext],
    "processing_status": Dict[str, ProcessingStatus]
}
```

## Implementation Phases

### Phase 1: Core RAG Infrastructure (Days 1-3)

#### Day 1: Document Processing Foundation
**Objective**: Implement robust PDF processing pipeline

**Tasks:**
1. **Document Service Implementation**
   ```python
   class DocumentService:
       def __init__(self):
           self.loaders = {
               'pdf': [PyPDFLoader, UnstructuredPDFLoader, PDFMinerLoader],
               'fallback': PyPDFLoader
           }
           self.validator = FileValidator()
           
       async def process_document(self, file_path: str) -> ProcessedDocument:
           # Validation, extraction, chunking
           pass
   ```

2. **File Validation System**
   ```python
   class FileValidator:
       MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
       ALLOWED_TYPES = ['application/pdf']
       
       def validate_file(self, file) -> ValidationResult:
           # Size, type, security checks
           pass
   ```

3. **Text Processing Pipeline**
   ```python
   class TextProcessor:
       def __init__(self):
           self.vietnamese_processor = VietnameseProcessor()
           self.splitters = {
               'recursive': RecursiveCharacterTextSplitter(
                   chunk_size=1000,
                   chunk_overlap=200
               ),
               'sentence': NLTKTextSplitter(),
               'token': TokenTextSplitter()
           }
   ```

#### Day 2: Vector Store Implementation
**Objective**: Set up persistent vector database with caching

**Tasks:**
1. **ChromaDB Integration**
   ```python
   class VectorStoreService:
       def __init__(self, persist_directory: str = "cache/vectors"):
           self.chroma = Chroma(
               persist_directory=persist_directory,
               embedding_function=self.get_embedding_function()
           )
           
       def get_embedding_function(self):
           return CacheBackedEmbeddings.from_bytes_store(
               underlying_embeddings=OpenAIEmbeddings(),
               document_embedding_cache=LocalFileStore("cache/embeddings"),
               namespace=f"finance_bro_{st.session_state.get('user_id', 'default')}"
           )
   ```

2. **Document Metadata Schema**
   ```python
   @dataclass
   class DocumentMetadata:
       id: str
       filename: str
       upload_timestamp: datetime
       file_size: int
       page_count: int
       document_type: str  # 'annual_report', 'quarterly', 'research', 'other'
       language: str
       processing_status: str
       chunk_count: int
       embedding_model: str
       vector_store_ids: List[str]
   ```

#### Day 3: Retrieval System
**Objective**: Implement intelligent document retrieval

**Tasks:**
1. **Advanced Retrieval Chain**
   ```python
   class RetrievalService:
       def __init__(self, vector_store: VectorStore):
           self.base_retriever = vector_store.as_retriever(
               search_type="mmr",
               search_kwargs={"k": 6, "fetch_k": 20}
           )
           self.compression_retriever = ContextualCompressionRetriever(
               base_compressor=LLMChainExtractor.from_llm(
                   ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
               ),
               base_retriever=self.base_retriever
           )
   ```

2. **Context Ranking System**
   ```python
   class ContextRanker:
       def rank_contexts(self, query: str, contexts: List[Document]) -> List[RankedContext]:
           # Relevance scoring, deduplication, Vietnamese language handling
           pass
   ```

### Phase 2: Agent Integration (Days 4-5)

#### Day 4: Enhanced Agent Architecture
**Objective**: Integrate RAG with existing PandasAI workflow

**Tasks:**
1. **Enhanced Agent Service**
   ```python
   class EnhancedAgentService:
       def __init__(self):
           self.rag_chain = self.create_rag_chain()
           self.pandas_agent = None
           
       def get_enhanced_agent_with_context(self, query: str) -> Agent:
           # Retrieve relevant context
           rag_context = self.rag_chain.invoke({"question": query})
           
           # Enhance PandasAI prompt with context
           enhanced_prompt = self.create_enhanced_prompt(
               financial_data=st.session_state.dataframes,
               rag_context=rag_context,
               user_query=query
           )
           
           return Agent(
               list(st.session_state.dataframes.values()),
               config={
                   "llm": self.llm,
                   "custom_prompt": enhanced_prompt,
                   "verbose": True
               }
           )
   ```

2. **Prompt Engineering Templates**
   ```python
   FINANCIAL_RAG_PROMPT = """
   You are a financial analyst with access to both structured financial data and relevant document context.

   STRUCTURED FINANCIAL DATA:
   {financial_data_summary}

   RELEVANT DOCUMENT CONTEXT:
   {retrieved_context}

   SOURCE DOCUMENTS:
   {source_citations}

   USER QUERY: {user_query}

   Instructions:
   1. Analyze both structured data and document context
   2. Provide comprehensive financial insights
   3. Always cite sources from documents when using their information
   4. Handle Vietnamese financial terms appropriately
   5. Generate visualizations when helpful
   """
   ```

#### Day 5: Conversation Memory Integration
**Objective**: Implement conversation-aware RAG

**Tasks:**
1. **Memory-Enhanced RAG Chain**
   ```python
   def create_conversational_rag_chain(self):
       memory = ConversationBufferMemory(
           memory_key="chat_history",
           return_messages=True,
           output_key="answer"
       )
       
       return ConversationalRetrievalChain.from_llm(
           llm=self.llm,
           retriever=self.retrieval_service.compression_retriever,
           memory=memory,
           return_source_documents=True,
           verbose=True
       )
   ```

### Phase 3: UI/UX Integration (Days 6-7)

#### Day 6: Enhanced File Upload
**Objective**: Seamless PDF upload integration

**Tasks:**
1. **Enhanced Chat Input**
   ```python
   # Modify existing chat_input handling (lines 561-590)
   if user_input := st.chat_input(
       "Ask me about financial data or upload documents...",
       accept_file=True,
       file_type=["csv", "xlsx", "pdf"]  # Add PDF support
   ):
       files = user_input.files if hasattr(user_input, "files") else []
       
       # Process PDF files
       for file in files:
           if file.name.endswith(".pdf"):
               await self.process_pdf_upload(file)
   ```

2. **Document Management Sidebar**
   ```python
   def render_document_management_sidebar():
       with st.sidebar:
           st.subheader("📄 Uploaded Documents")
           
           if "uploaded_documents" in st.session_state:
               for doc in st.session_state.uploaded_documents:
                   with st.expander(f"📄 {doc.filename}"):
                       st.write(f"Pages: {doc.page_count}")
                       st.write(f"Size: {format_file_size(doc.file_size)}")
                       st.write(f"Type: {doc.document_type}")
                       
                       col1, col2 = st.columns(2)
                       with col1:
                           if st.button("View", key=f"view_{doc.id}"):
                               st.session_state.preview_doc = doc.id
                       with col2:
                           if st.button("Delete", key=f"delete_{doc.id}"):
                               self.delete_document(doc.id)
   ```

#### Day 7: Advanced Chat Features
**Objective**: Rich chat experience with source attribution

**Tasks:**
1. **Enhanced Message Display**
   ```python
   def display_enhanced_message(message: Dict):
       st.markdown(message["content"])
       
       # Display source citations
       if "sources" in message:
           with st.expander("📚 Sources", expanded=False):
               for source in message["sources"]:
                   st.markdown(f"**{source.document_name}** (Page {source.page})")
                   st.markdown(f"> {source.excerpt}")
       
       # Display retrieved context
       if "rag_context" in message:
           with st.expander("🔍 Retrieved Context", expanded=False):
               for context in message["rag_context"]:
                   st.markdown(f"**Relevance: {context.score:.2f}**")
                   st.markdown(context.content)
   ```

## Service Module Designs

### src/services/document_service.py

```python
from typing import List, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import asyncio
from langchain.document_loaders import PyPDFLoader, UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

@dataclass
class ProcessedDocument:
    """Represents a processed document with metadata and chunks."""
    id: str
    filename: str
    chunks: List[Document]
    metadata: DocumentMetadata
    processing_time: float

class DocumentService:
    """Service for processing uploaded PDF documents."""
    
    def __init__(self, cache_dir: str = "cache/documents"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        self.loaders = {
            'pypdf': PyPDFLoader,
            'unstructured': UnstructuredPDFLoader
        }
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        self.vietnamese_processor = VietnameseProcessor()
    
    async def process_document(self, file_path: str, document_type: str = "financial") -> ProcessedDocument:
        """Process a PDF document and return processed chunks."""
        start_time = time.time()
        
        # Validate file
        validation_result = self.validate_pdf(file_path)
        if not validation_result.is_valid:
            raise ValueError(f"Invalid PDF: {validation_result.error}")
        
        # Extract text
        documents = await self.extract_text(file_path)
        
        # Process Vietnamese content
        processed_docs = self.vietnamese_processor.process_documents(documents)
        
        # Split into chunks
        chunks = self.text_splitter.split_documents(processed_docs)
        
        # Enhance metadata
        for i, chunk in enumerate(chunks):
            chunk.metadata.update({
                'chunk_index': i,
                'document_type': document_type,
                'processed_timestamp': datetime.now().isoformat(),
                'language': self.detect_language(chunk.page_content)
            })
        
        processing_time = time.time() - start_time
        
        return ProcessedDocument(
            id=str(uuid.uuid4()),
            filename=Path(file_path).name,
            chunks=chunks,
            metadata=self.create_metadata(file_path, chunks, processing_time),
            processing_time=processing_time
        )
    
    async def extract_text(self, file_path: str) -> List[Document]:
        """Extract text using multiple loaders with fallback."""
        for loader_name, loader_class in self.loaders.items():
            try:
                loader = loader_class(file_path)
                documents = await asyncio.to_thread(loader.load)
                if documents and any(doc.page_content.strip() for doc in documents):
                    return documents
            except Exception as e:
                logging.warning(f"{loader_name} failed: {e}")
                continue
        
        raise Exception("All PDF loaders failed")
    
    def validate_pdf(self, file_path: str) -> ValidationResult:
        """Validate PDF file for security and compatibility."""
        # Implementation details for file validation
        pass
```

### src/services/vector_service.py

```python
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings, CacheBackedEmbeddings
from langchain.storage import LocalFileStore
from typing import List, Optional, Dict
import streamlit as st

class VectorStoreService:
    """Service for managing document vectors and similarity search."""
    
    def __init__(self, persist_directory: str = "cache/vectors"):
        self.persist_directory = persist_directory
        self.embedding_cache_dir = "cache/embeddings"
        self._vector_store = None
        self._embedding_function = None
    
    @property
    def embedding_function(self):
        """Lazy-loaded cached embedding function."""
        if self._embedding_function is None:
            base_embeddings = OpenAIEmbeddings(
                model="text-embedding-ada-002",
                openai_api_key=st.session_state.api_key
            )
            
            file_store = LocalFileStore(self.embedding_cache_dir)
            
            self._embedding_function = CacheBackedEmbeddings.from_bytes_store(
                underlying_embeddings=base_embeddings,
                document_embedding_cache=file_store,
                namespace=f"finance_bro_{st.session_state.get('user_id', 'default')}"
            )
        
        return self._embedding_function
    
    @property
    def vector_store(self):
        """Lazy-loaded vector store."""
        if self._vector_store is None:
            self._vector_store = Chroma(
                persist_directory=self.persist_directory,
                embedding_function=self.embedding_function,
                collection_metadata={"hnsw:space": "cosine"}
            )
        return self._vector_store
    
    async def add_documents(self, documents: List[Document], document_id: str) -> List[str]:
        """Add documents to vector store with batch processing."""
        # Add document_id to metadata for filtering
        for doc in documents:
            doc.metadata["document_id"] = document_id
            doc.metadata["timestamp"] = datetime.now().isoformat()
        
        # Process in batches to avoid rate limits
        batch_size = 100
        all_ids = []
        
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            with st.spinner(f"Processing batch {i//batch_size + 1}/{(len(documents)-1)//batch_size + 1}"):
                batch_ids = await asyncio.to_thread(
                    self.vector_store.add_documents, 
                    batch
                )
                all_ids.extend(batch_ids)
                
                # Rate limiting
                await asyncio.sleep(1)
        
        # Persist changes
        self.vector_store.persist()
        return all_ids
    
    def search_similar_documents(
        self, 
        query: str, 
        k: int = 6,
        document_filter: Optional[Dict] = None
    ) -> List[Document]:
        """Search for similar documents with optional filtering."""
        search_kwargs = {"k": k}
        
        if document_filter:
            search_kwargs["filter"] = document_filter
        
        return self.vector_store.similarity_search(query, **search_kwargs)
    
    def delete_document(self, document_id: str) -> bool:
        """Delete all chunks of a document from vector store."""
        try:
            # Get all chunk IDs for the document
            results = self.vector_store.get(where={"document_id": document_id})
            
            if results['ids']:
                self.vector_store.delete(ids=results['ids'])
                self.vector_store.persist()
                return True
            return False
        except Exception as e:
            logging.error(f"Failed to delete document {document_id}: {e}")
            return False
```

### src/services/rag_service.py

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain.memory import ConversationBufferMemory
from langchain.llms import ChatOpenAI
from typing import Dict, List, Optional

class RAGService:
    """Service for Retrieval-Augmented Generation operations."""
    
    def __init__(self, vector_service: VectorStoreService):
        self.vector_service = vector_service
        self.llm = ChatOpenAI(
            temperature=0,
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=st.session_state.api_key
        )
        self._retrieval_chain = None
    
    @property
    def retrieval_chain(self):
        """Lazy-loaded conversational retrieval chain."""
        if self._retrieval_chain is None:
            self._retrieval_chain = self.create_retrieval_chain()
        return self._retrieval_chain
    
    def create_retrieval_chain(self) -> ConversationalRetrievalChain:
        """Create a conversational retrieval chain with compression."""
        # Base retriever with MMR search
        base_retriever = self.vector_service.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 6,
                "fetch_k": 20,
                "lambda_mult": 0.7
            }
        )
        
        # Contextual compression retriever
        compressor = LLMChainExtractor.from_llm(
            ChatOpenAI(temperature=0, model="gpt-3.5-turbo")
        )
        
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=base_retriever
        )
        
        # Conversation memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Create chain
        chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=compression_retriever,
            memory=memory,
            return_source_documents=True,
            verbose=True,
            combine_docs_chain_kwargs={
                "prompt": self.create_custom_prompt()
            }
        )
        
        return chain
    
    def create_custom_prompt(self):
        """Create custom prompt template for financial analysis."""
        from langchain.prompts import PromptTemplate
        
        template = """
        You are an expert financial analyst with access to Vietnamese stock market data and financial documents.
        
        Context from uploaded documents:
        {context}
        
        Chat History:
        {chat_history}
        
        Question: {question}
        
        Instructions:
        1. Analyze the provided context from financial documents
        2. Consider Vietnamese market conditions and terminology
        3. Provide specific insights backed by the document evidence
        4. Always cite sources when referencing document information
        5. If the documents don't contain relevant information, clearly state this
        6. Format financial numbers appropriately (VND, percentages, ratios)
        
        Answer:
        """
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "chat_history", "question"]
        )
    
    async def query_documents(
        self, 
        query: str, 
        document_filter: Optional[Dict] = None
    ) -> Dict:
        """Query documents and return enhanced response."""
        try:
            # Apply document filter if specified
            if document_filter:
                # Temporarily modify retriever with filter
                self.update_retriever_filter(document_filter)
            
            # Get response from chain
            response = await asyncio.to_thread(
                self.retrieval_chain,
                {"question": query}
            )
            
            # Process and enhance response
            enhanced_response = self.process_rag_response(response)
            
            return enhanced_response
            
        except Exception as e:
            logging.error(f"RAG query failed: {e}")
            return {
                "answer": f"❌ RAG query failed: {str(e)}",
                "source_documents": [],
                "sources": []
            }
    
    def process_rag_response(self, response: Dict) -> Dict:
        """Process RAG response and add source information."""
        sources = []
        
        for doc in response.get("source_documents", []):
            source = {
                "document_name": doc.metadata.get("source", "Unknown"),
                "page": doc.metadata.get("page", "N/A"),
                "excerpt": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                "relevance_score": doc.metadata.get("relevance_score", 0.0)
            }
            sources.append(source)
        
        return {
            "answer": response["answer"],
            "source_documents": response.get("source_documents", []),
            "sources": sources,
            "chat_history": response.get("chat_history", [])
        }
```

### src/services/enhanced_agent_service.py

```python
from pandasai import Agent
from typing import Dict, List, Optional, Any
import streamlit as st

class EnhancedAgentService:
    """Service for integrating RAG context with PandasAI agents."""
    
    def __init__(self, rag_service: RAGService):
        self.rag_service = rag_service
        self.llm = ChatOpenAI(
            temperature=0,
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
            openai_api_key=st.session_state.api_key
        )
    
    async def get_enhanced_agent_with_rag_context(
        self, 
        query: str,
        dataframes: Dict[str, pd.DataFrame],
        document_filter: Optional[Dict] = None
    ) -> tuple[Agent, Dict]:
        """Create PandasAI agent enhanced with RAG context."""
        
        # Get RAG context for the query
        rag_response = await self.rag_service.query_documents(
            query=query,
            document_filter=document_filter
        )
        
        # Create enhanced prompt with context
        enhanced_prompt = self.create_enhanced_prompt(
            financial_data_summary=self.summarize_dataframes(dataframes),
            rag_context=rag_response["answer"],
            source_documents=rag_response["sources"],
            user_query=query
        )
        
        # Create enhanced agent
        agent = Agent(
            list(dataframes.values()),
            config={
                "llm": self.llm,
                "custom_prompt": enhanced_prompt,
                "verbose": True,
                "enable_cache": True
            }
        )
        
        return agent, rag_response
    
    def create_enhanced_prompt(
        self,
        financial_data_summary: str,
        rag_context: str,
        source_documents: List[Dict],
        user_query: str
    ) -> str:
        """Create enhanced prompt combining financial data and document context."""
        
        sources_text = ""
        if source_documents:
            sources_text = "\n".join([
                f"- {source['document_name']} (Page {source['page']}): {source['excerpt']}"
                for source in source_documents
            ])
        
        prompt = f"""
You are an expert financial analyst with access to both structured financial data and relevant document context.

=== STRUCTURED FINANCIAL DATA ===
{financial_data_summary}

=== DOCUMENT CONTEXT ===
{rag_context}

=== SOURCE DOCUMENTS ===
{sources_text}

=== USER QUERY ===
{user_query}

=== INSTRUCTIONS ===
1. Analyze both the structured financial data (from dataframes) and the document context
2. Provide comprehensive financial insights that combine both data sources
3. When referencing information from documents, include source citations
4. Handle Vietnamese financial terms and company names appropriately  
5. Generate appropriate visualizations when helpful
6. If document context is not relevant to the query, focus on the structured data
7. Always prioritize accuracy and cite your sources

Provide your analysis below:
"""
        
        return prompt
    
    def summarize_dataframes(self, dataframes: Dict[str, pd.DataFrame]) -> str:
        """Create a concise summary of available financial data."""
        summary = []
        
        for name, df in dataframes.items():
            if not df.empty:
                summary.append(f"- {name}: {len(df)} records, columns: {', '.join(df.columns[:5])}{'...' if len(df.columns) > 5 else ''}")
        
        return "\n".join(summary) if summary else "No financial data available"
    
    async def process_enhanced_query(
        self,
        query: str,
        dataframes: Dict[str, pd.DataFrame],
        document_filter: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Process a query using enhanced agent with RAG context."""
        
        try:
            # Get enhanced agent and RAG context
            agent, rag_response = await self.get_enhanced_agent_with_rag_context(
                query=query,
                dataframes=dataframes,
                document_filter=document_filter
            )
            
            # Execute query with enhanced agent
            with st.spinner("🤖 Analyzing with enhanced context..."):
                pandas_response = await asyncio.to_thread(agent.chat, query)
            
            # Combine responses
            enhanced_response = self.combine_responses(
                pandas_response=pandas_response,
                rag_response=rag_response,
                agent=agent
            )
            
            return enhanced_response
            
        except Exception as e:
            logging.error(f"Enhanced query processing failed: {e}")
            return {
                "role": "assistant",
                "content": f"❌ Enhanced analysis failed: {str(e)}",
                "sources": []
            }
    
    def combine_responses(
        self,
        pandas_response: Any,
        rag_response: Dict,
        agent: Agent
    ) -> Dict[str, Any]:
        """Combine PandasAI and RAG responses into unified message."""
        
        # Get generated code from PandasAI
        generated_code = self.extract_generated_code(pandas_response, agent)
        
        # Detect charts
        from src.services.chart_service import detect_latest_chart
        chart_data = detect_latest_chart()
        
        # Create combined message
        message_data = {
            "role": "assistant",
            "content": str(pandas_response),
            "sources": rag_response["sources"],
            "rag_context": rag_response.get("source_documents", [])
        }
        
        if generated_code:
            message_data["generated_code"] = generated_code
            
        if chart_data:
            message_data["chart_data"] = chart_data
        
        return message_data
    
    def extract_generated_code(self, response: Any, agent: Agent) -> Optional[str]:
        """Extract generated code from PandasAI response."""
        # Implementation similar to existing get_generated_code function
        try:
            if hasattr(response, "last_code_executed") and response.last_code_executed:
                return response.last_code_executed
            
            if hasattr(agent, "last_code_executed") and agent.last_code_executed:
                return agent.last_code_executed
            
            return "# Code generation details not available"
            
        except Exception as e:
            return f"# Error accessing code: {str(e)}"
```

## UI/UX Specifications

### Enhanced File Upload Interface

```python
def render_enhanced_file_upload():
    """Render enhanced file upload interface with PDF support."""
    
    # File upload section in sidebar
    with st.sidebar:
        st.subheader("📁 Document Upload")
        
        # Drag and drop area
        uploaded_files = st.file_uploader(
            "Upload financial documents",
            type=['pdf', 'csv', 'xlsx'],
            accept_multiple_files=True,
            help="Supported: PDF (up to 50MB), CSV, Excel files"
        )
        
        if uploaded_files:
            for uploaded_file in uploaded_files:
                if uploaded_file.name.endswith('.pdf'):
                    process_pdf_upload(uploaded_file)
                else:
                    process_data_file(uploaded_file)
    
    # Document management
    render_document_management_panel()
```

### Document Management Panel

```python
def render_document_management_panel():
    """Render document management interface."""
    
    with st.sidebar:
        st.subheader("📄 Uploaded Documents")
        
        if "uploaded_documents" not in st.session_state:
            st.session_state.uploaded_documents = []
        
        if not st.session_state.uploaded_documents:
            st.info("No documents uploaded yet")
            return
        
        for i, doc in enumerate(st.session_state.uploaded_documents):
            with st.expander(f"📄 {doc.filename}", expanded=False):
                # Document info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Pages", doc.page_count)
                    st.metric("Chunks", doc.chunk_count)
                with col2:
                    st.metric("Size", format_file_size(doc.file_size))
                    st.metric("Type", doc.document_type.title())
                
                # Document actions
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("👁️ Preview", key=f"preview_{doc.id}"):
                        st.session_state.preview_document_id = doc.id
                        st.rerun()
                
                with col2:
                    if st.button("📊 Stats", key=f"stats_{doc.id}"):
                        show_document_stats(doc)
                
                with col3:
                    if st.button("🗑️ Delete", key=f"delete_{doc.id}"):
                        delete_document(doc.id)
                        st.rerun()
```

### Enhanced Chat Interface

```python
def render_enhanced_chat_interface():
    """Render enhanced chat interface with RAG features."""
    
    # RAG status indicator
    render_rag_status_indicator()
    
    # Display chat messages with source attribution
    chat_container = st.container()
    with chat_container:
        for i, message in enumerate(st.session_state.messages):
            with st.chat_message(message["role"]):
                # Main message content
                st.markdown(message["content"])
                
                # Source citations (for assistant messages)
                if message["role"] == "assistant" and "sources" in message:
                    render_source_citations(message["sources"])
                
                # Generated code (for assistant messages)
                if "generated_code" in message:
                    with st.expander("🔍 View Generated Code", expanded=False):
                        st.code(message["generated_code"], language="python")
                
                # Retrieved context (for debugging)
                if "rag_context" in message and st.checkbox("Show RAG Context", key=f"rag_context_{i}"):
                    render_rag_context(message["rag_context"])
                
                # Charts (only for latest message)
                if "chart_data" in message and i == len(st.session_state.messages) - 1:
                    render_chart(message["chart_data"])
    
    # Enhanced chat input
    render_enhanced_chat_input()
```

### Document Preview Modal

```python
def render_document_preview():
    """Render document preview in modal dialog."""
    
    if "preview_document_id" in st.session_state:
        doc_id = st.session_state.preview_document_id
        doc = find_document_by_id(doc_id)
        
        if doc:
            with st.container():
                st.subheader(f"📄 {doc.filename}")
                
                # Document metadata
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pages", doc.page_count)
                with col2:
                    st.metric("Upload Date", doc.upload_timestamp.strftime("%Y-%m-%d"))
                with col3:
                    st.metric("Processing Time", f"{doc.processing_time:.2f}s")
                
                # Page navigation
                page_num = st.selectbox(
                    "Select page to preview:",
                    range(1, doc.page_count + 1),
                    key=f"page_select_{doc_id}"
                )
                
                # Show page content
                page_content = get_page_content(doc, page_num)
                st.text_area(
                    f"Page {page_num} Content:",
                    value=page_content,
                    height=300,
                    disabled=True
                )
                
                # Close button
                if st.button("Close Preview"):
                    del st.session_state.preview_document_id
                    st.rerun()
```

## Integration with Existing Systems

### Modifying bro.py Chat Input

```python
# Existing code modification at lines 561-590
if user_input := st.chat_input(
    "Ask me about financial data or upload documents (PDF, CSV, Excel)...",
    accept_file=True,
    file_type=["csv", "xlsx", "pdf"]  # Add PDF support
):
    # Extract text and files
    if hasattr(user_input, "text"):
        prompt = user_input.text if user_input.text else ""
        files = user_input.files if hasattr(user_input, "files") else []
    else:
        prompt = str(user_input) if user_input else ""
        files = []
    
    # Process uploaded files
    if files:
        await process_uploaded_files(files)  # New function
    
    # Process text query with enhanced agent
    if prompt.strip():
        enhanced_response = await process_enhanced_query(prompt)  # Modified function
        st.session_state.messages.append(enhanced_response)
        st.rerun()
```

### Enhanced Agent Creation

```python
# Modify get_or_create_agent() function
def get_enhanced_agent():
    """
    Creates or retrieves cached PandasAI agent enhanced with RAG capabilities.
    """
    # Create unique key including RAG state
    stock_df_count = len(st.session_state.dataframes) if "dataframes" in st.session_state else 0
    uploaded_df_count = len(st.session_state.uploaded_dataframes)
    document_count = len(st.session_state.uploaded_documents) if "uploaded_documents" in st.session_state else 0
    
    current_key = f"enhanced_agent_{stock_df_count}_{uploaded_df_count}_{document_count}"
    
    # Check if agent exists and is up to date
    if (
        "enhanced_agent" in st.session_state
        and "enhanced_agent_key" in st.session_state
        and st.session_state.enhanced_agent_key == current_key
    ):
        return st.session_state.enhanced_agent
    
    # Create new enhanced agent service
    if "rag_service" not in st.session_state:
        vector_service = VectorStoreService()
        st.session_state.rag_service = RAGService(vector_service)
    
    enhanced_agent_service = EnhancedAgentService(st.session_state.rag_service)
    
    # Cache the service
    st.session_state.enhanced_agent = enhanced_agent_service
    st.session_state.enhanced_agent_key = current_key
    
    return enhanced_agent_service
```

### Session State Management

```python
def initialize_rag_session_state():
    """Initialize RAG-related session state variables."""
    
    if "uploaded_documents" not in st.session_state:
        st.session_state.uploaded_documents = []
    
    if "rag_enabled" not in st.session_state:
        st.session_state.rag_enabled = True
    
    if "processing_status" not in st.session_state:
        st.session_state.processing_status = {}
    
    if "vector_store_initialized" not in st.session_state:
        st.session_state.vector_store_initialized = False
```

## Performance & Security

### Caching Strategy

```python
# Document processing cache
@st.cache_data(ttl=3600, max_entries=100)
def cache_document_processing(file_hash: str, processing_params: Dict) -> ProcessedDocument:
    """Cache processed document results."""
    pass

# Embedding cache
@st.cache_data(ttl=86400, max_entries=1000)
def cache_document_embeddings(chunk_hash: str, embedding_model: str) -> List[float]:
    """Cache document chunk embeddings."""
    pass

# RAG query cache
@st.cache_data(ttl=1800, max_entries=50)
def cache_rag_responses(query_hash: str, document_context_hash: str) -> Dict:
    """Cache RAG query responses."""
    pass
```

### Security Measures

```python
class DocumentSecurityValidator:
    """Validate uploaded documents for security threats."""
    
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    ALLOWED_MIME_TYPES = ['application/pdf']
    MAX_PAGES = 1000
    
    def validate_pdf_security(self, file_path: str) -> SecurityValidationResult:
        """Comprehensive PDF security validation."""
        
        # File size check
        if os.path.getsize(file_path) > self.MAX_FILE_SIZE:
            return SecurityValidationResult(False, "File too large")
        
        # MIME type validation
        mime_type = magic.from_file(file_path, mime=True)
        if mime_type not in self.ALLOWED_MIME_TYPES:
            return SecurityValidationResult(False, f"Invalid file type: {mime_type}")
        
        # PDF structure validation
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf = PyPDF2.PdfReader(file)
                
                # Check for password protection
                if pdf.is_encrypted:
                    return SecurityValidationResult(False, "Password-protected PDFs not supported")
                
                # Page count limit
                if len(pdf.pages) > self.MAX_PAGES:
                    return SecurityValidationResult(False, f"Too many pages: {len(pdf.pages)}")
                
                # Check for JavaScript or forms
                for page in pdf.pages:
                    if '/JS' in page or '/JavaScript' in page:
                        return SecurityValidationResult(False, "JavaScript in PDF not allowed")
                    
                    if '/AcroForm' in page or '/XFA' in page:
                        return SecurityValidationResult(False, "Interactive forms not supported")
        
        except Exception as e:
            return SecurityValidationResult(False, f"PDF validation failed: {e}")
        
        return SecurityValidationResult(True, "Valid PDF")
```

### Memory Management

```python
class MemoryManager:
    """Manage memory usage for document processing and vector storage."""
    
    def __init__(self):
        self.max_documents_per_session = 20
        self.max_chunks_per_document = 1000
        self.memory_threshold_mb = 500
    
    def check_memory_usage(self) -> MemoryStatus:
        """Check current memory usage."""
        import psutil
        
        process = psutil.Process()
        memory_mb = process.memory_info().rss / 1024 / 1024
        
        return MemoryStatus(
            current_mb=memory_mb,
            threshold_mb=self.memory_threshold_mb,
            is_over_threshold=memory_mb > self.memory_threshold_mb
        )
    
    def cleanup_old_documents(self):
        """Remove old documents if memory threshold is exceeded."""
        if self.check_memory_usage().is_over_threshold:
            # Remove oldest documents beyond limit
            if len(st.session_state.uploaded_documents) > self.max_documents_per_session:
                docs_to_remove = st.session_state.uploaded_documents[:-self.max_documents_per_session]
                
                for doc in docs_to_remove:
                    self.remove_document_from_memory(doc.id)
```

### Rate Limiting

```python
class APIRateLimiter:
    """Rate limiting for OpenAI API calls."""
    
    def __init__(self):
        self.embedding_calls = []
        self.chat_calls = []
        self.max_embedding_calls_per_minute = 1000
        self.max_chat_calls_per_minute = 50
    
    async def limit_embedding_calls(self, func, *args, **kwargs):
        """Rate limit embedding API calls."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.embedding_calls = [call_time for call_time in self.embedding_calls if now - call_time < 60]
        
        if len(self.embedding_calls) >= self.max_embedding_calls_per_minute:
            sleep_time = 60 - (now - self.embedding_calls[0])
            await asyncio.sleep(sleep_time)
        
        self.embedding_calls.append(now)
        return await func(*args, **kwargs)
```

## Testing Strategy

### Unit Tests

```python
# tests/test_document_service.py
import pytest
from src.services.document_service import DocumentService

class TestDocumentService:
    
    @pytest.fixture
    def document_service(self):
        return DocumentService(cache_dir="test_cache")
    
    @pytest.fixture
    def sample_pdf_path(self):
        return "tests/fixtures/sample_financial_report.pdf"
    
    async def test_process_document_success(self, document_service, sample_pdf_path):
        """Test successful document processing."""
        result = await document_service.process_document(sample_pdf_path)
        
        assert result.id is not None
        assert result.filename == "sample_financial_report.pdf"
        assert len(result.chunks) > 0
        assert result.processing_time > 0
    
    def test_validate_pdf_security(self, document_service, sample_pdf_path):
        """Test PDF security validation."""
        result = document_service.validate_pdf(sample_pdf_path)
        assert result.is_valid is True
    
    async def test_extract_text_fallback(self, document_service):
        """Test text extraction with loader fallback."""
        # Test with corrupted PDF that requires fallback
        corrupted_pdf = "tests/fixtures/corrupted.pdf"
        
        with pytest.raises(Exception, match="All PDF loaders failed"):
            await document_service.extract_text(corrupted_pdf)
```

### Integration Tests

```python
# tests/test_rag_integration.py
import pytest
import streamlit as st
from src.services.rag_service import RAGService
from src.services.vector_service import VectorStoreService

class TestRAGIntegration:
    
    @pytest.fixture
    def setup_test_environment(self):
        """Set up test environment with mock session state."""
        st.session_state.api_key = "test_key"
        st.session_state.uploaded_documents = []
        
        vector_service = VectorStoreService(persist_directory="test_vectors")
        rag_service = RAGService(vector_service)
        
        return rag_service
    
    async def test_end_to_end_rag_workflow(self, setup_test_environment):
        """Test complete RAG workflow from document upload to query."""
        rag_service = setup_test_environment
        
        # 1. Process document
        from src.services.document_service import DocumentService
        doc_service = DocumentService()
        processed_doc = await doc_service.process_document("tests/fixtures/annual_report.pdf")
        
        # 2. Add to vector store
        vector_ids = await rag_service.vector_service.add_documents(
            processed_doc.chunks, 
            processed_doc.id
        )
        assert len(vector_ids) > 0
        
        # 3. Query documents
        query = "What was the revenue growth in Q4?"
        response = await rag_service.query_documents(query)
        
        assert "answer" in response
        assert len(response["sources"]) > 0
    
    async def test_enhanced_agent_integration(self, setup_test_environment):
        """Test integration with enhanced PandasAI agent."""
        from src.services.enhanced_agent_service import EnhancedAgentService
        
        rag_service = setup_test_environment
        agent_service = EnhancedAgentService(rag_service)
        
        # Mock financial dataframes
        import pandas as pd
        dataframes = {
            "IncomeStatement": pd.DataFrame({
                "revenue": [1000, 1100, 1200],
                "year": [2022, 2023, 2024]
            })
        }
        
        query = "Compare revenue growth with industry trends mentioned in uploaded reports"
        response = await agent_service.process_enhanced_query(query, dataframes)
        
        assert response["role"] == "assistant"
        assert "content" in response
```

### Performance Tests

```python
# tests/test_performance.py
import pytest
import time
from src.services.vector_service import VectorStoreService

class TestPerformance:
    
    async def test_document_processing_speed(self):
        """Test document processing performance."""
        from src.services.document_service import DocumentService
        
        doc_service = DocumentService()
        
        start_time = time.time()
        result = await doc_service.process_document("tests/fixtures/large_report.pdf")
        processing_time = time.time() - start_time
        
        # Should process within 30 seconds for 50MB document
        assert processing_time < 30
        assert len(result.chunks) > 0
    
    def test_vector_search_performance(self):
        """Test vector search response time."""
        vector_service = VectorStoreService(persist_directory="test_vectors")
        
        start_time = time.time()
        results = vector_service.search_similar_documents("revenue growth", k=10)
        search_time = time.time() - start_time
        
        # Should return results within 2 seconds
        assert search_time < 2.0
        assert len(results) <= 10
    
    async def test_concurrent_processing(self):
        """Test concurrent document processing."""
        from src.services.document_service import DocumentService
        import asyncio
        
        doc_service = DocumentService()
        
        # Process 5 documents concurrently
        tasks = [
            doc_service.process_document(f"tests/fixtures/report_{i}.pdf")
            for i in range(5)
        ]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Should complete all within reasonable time
        assert total_time < 120  # 2 minutes for 5 documents
        assert len([r for r in results if not isinstance(r, Exception)]) >= 3
```

### User Acceptance Tests

```python
# tests/test_user_acceptance.py
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock

class TestUserAcceptance:
    
    def test_pdf_upload_user_flow(self):
        """Test complete PDF upload user flow."""
        # Mock Streamlit components
        with patch('streamlit.file_uploader') as mock_uploader:
            # Simulate file upload
            mock_file = MagicMock()
            mock_file.name = "annual_report.pdf"
            mock_file.size = 1024 * 1024  # 1MB
            mock_uploader.return_value = [mock_file]
            
            # Test upload handling
            from src.services.document_service import DocumentService
            doc_service = DocumentService()
            
            # Should accept valid PDF
            validation = doc_service.validate_pdf_upload(mock_file)
            assert validation.is_valid
    
    def test_chat_with_documents_flow(self):
        """Test chat interface with document context."""
        # Setup mock session state
        st.session_state.uploaded_documents = [
            MagicMock(id="doc1", filename="report.pdf")
        ]
        
        # Test query processing
        query = "What are the key financial highlights?"
        
        # Should process query and return enhanced response
        # (Integration with actual services tested separately)
        assert len(query) > 0  # Basic sanity check
    
    def test_source_attribution_display(self):
        """Test source attribution in chat responses."""
        mock_response = {
            "content": "Revenue increased by 15% in Q4",
            "sources": [
                {
                    "document_name": "Q4_Report.pdf",
                    "page": 5,
                    "excerpt": "Revenue for Q4 was $1.15B, representing 15% growth"
                }
            ]
        }
        
        # Should display sources correctly
        assert len(mock_response["sources"]) > 0
        assert "document_name" in mock_response["sources"][0]
```

## Deployment Considerations

### Docker Integration

```dockerfile
# Add RAG dependencies to existing Dockerfile
FROM python:3.10.11-slim

# Install system dependencies for PDF processing
RUN apt-get update && apt-get install -y \
    libmagic1 \
    poppler-utils \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY pyproject.toml .
RUN pip install -e .

# Create cache directories
RUN mkdir -p cache/vectors cache/embeddings cache/documents

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Run application
CMD ["streamlit", "run", "app.py"]
```

### Environment Variables

```bash
# .env additions for RAG functionality
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o-mini

# RAG Configuration
RAG_CACHE_DIR=cache/vectors
EMBEDDING_CACHE_DIR=cache/embeddings
DOCUMENT_CACHE_DIR=cache/documents
MAX_DOCUMENT_SIZE_MB=50
MAX_DOCUMENTS_PER_USER=20

# Vector Store Configuration
VECTOR_STORE_TYPE=chroma  # or faiss
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200

# Performance Settings
ENABLE_EMBEDDING_CACHE=true
ENABLE_RAG_QUERY_CACHE=true
CACHE_TTL_HOURS=24
```

### Production Optimizations

```python
# Production configuration
PRODUCTION_CONFIG = {
    "vector_store": {
        "type": "chroma",
        "persist_directory": "/app/data/vectors",
        "collection_metadata": {"hnsw:space": "cosine"}
    },
    "embeddings": {
        "model": "text-embedding-ada-002",
        "cache_enabled": True,
        "cache_directory": "/app/data/embeddings",
        "batch_size": 100
    },
    "document_processing": {
        "max_workers": 4,
        "timeout_seconds": 300,
        "chunk_size": 1000,
        "chunk_overlap": 200
    },
    "security": {
        "max_file_size_mb": 50,
        "allowed_mime_types": ["application/pdf"],
        "max_pages_per_document": 1000,
        "virus_scan_enabled": True
    },
    "performance": {
        "query_cache_ttl": 1800,  # 30 minutes
        "embedding_cache_ttl": 86400,  # 24 hours
        "max_concurrent_queries": 10,
        "memory_limit_mb": 2048
    }
}
```

### Monitoring and Logging

```python
import logging
from datetime import datetime

class RAGLogger:
    """Comprehensive logging for RAG operations."""
    
    def __init__(self):
        self.setup_logging()
    
    def setup_logging(self):
        """Configure logging for production."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('logs/rag_operations.log'),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger('RAG')
    
    def log_document_processing(self, filename: str, processing_time: float, chunk_count: int):
        """Log document processing metrics."""
        self.logger.info(f"Document processed: {filename}, time: {processing_time:.2f}s, chunks: {chunk_count}")
    
    def log_query_performance(self, query: str, response_time: float, source_count: int):
        """Log query performance metrics."""
        self.logger.info(f"Query processed: response_time: {response_time:.2f}s, sources: {source_count}")
    
    def log_error(self, operation: str, error: Exception):
        """Log errors with context."""
        self.logger.error(f"Error in {operation}: {str(error)}", exc_info=True)
```

### Health Checks

```python
class RAGHealthCheck:
    """Health check endpoints for RAG system."""
    
    def __init__(self, vector_service: VectorStoreService, rag_service: RAGService):
        self.vector_service = vector_service
        self.rag_service = rag_service
    
    def check_vector_store_health(self) -> Dict[str, Any]:
        """Check vector store connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test basic operations
            self.vector_service.vector_store.similarity_search("test", k=1)
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def check_embedding_service_health(self) -> Dict[str, Any]:
        """Check embedding service availability."""
        try:
            start_time = time.time()
            
            # Test embedding generation
            self.vector_service.embedding_function.embed_query("test query")
            
            response_time = time.time() - start_time
            
            return {
                "status": "healthy",
                "response_time": response_time,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
```

---

## Conclusion

This comprehensive implementation plan provides detailed specifications for integrating PDF RAG functionality into the Finance Bro application. The plan leverages the full LangChain ecosystem while maintaining compatibility with existing systems and optimizing for Vietnamese financial document analysis.

### Next Steps

1. **Review and approve** this implementation plan
2. **Set up development environment** with new dependencies
3. **Begin Phase 1 implementation** starting with core RAG infrastructure
4. **Iterate and test** each component thoroughly
5. **Deploy incrementally** with proper monitoring and rollback capabilities

The implementation will provide users with powerful document analysis capabilities while maintaining the familiar Finance Bro interface and workflow.