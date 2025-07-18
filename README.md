# 🎥 YouTube RAG Assistant Chrome Extension

> Transform any YouTube video into an interactive Q&A experience with AI-powered retrieval-augmented generation

## 📹 Demo

[![YouTube RAG Assistant Demo](https://i9.ytimg.com/vi_webp/YMjDTDVrC5s/mq3.webp?sqp=CJiJ6sMG-oaymwEmCMACELQB8quKqQMa8AEB-AH-CYAC0AWKAgwIABABGH8gEygdMA8=&rs=AOn4CLBWkgp8Dcga_pFXhdElOXqvO_ASqw)](https://youtu.be/YMjDTDVrC5s)

*Click the image above to watch the demo video*

---

## 🚀 Overview

YouTube RAG Assistant is a powerful Chrome extension that lets you chat with YouTube videos using advanced AI. Simply navigate to any YouTube video, transcribe it with one click, and ask questions about the content. The extension uses retrieval-augmented generation (RAG) to provide accurate, contextual answers based on the video's transcript.

### ✨ Key Features

- **🎯 One-Click Transcription**: Instantly transcribe any YouTube video
- **💬 Interactive Q&A**: Ask questions and get AI-powered answers from video content
- **👤 User Authentication**: Secure login/signup system with JWT tokens
- **💾 Save Transcripts**: Save your favorite video transcripts for later reference
- **🔍 Smart Retrieval**: Advanced multi-query retrieval for comprehensive answers
- **📱 Responsive UI**: Clean, modern interface built with React and Tailwind CSS
- **☁️ Cloud Deployment**: Fully deployed backend on Render

---

## 🛠️ Tech Stack

### Frontend
- **React** - Modern UI framework
- **Tailwind CSS** - Utility-first CSS framework
- **Chrome Extension APIs** - Browser integration
- **Axios** - HTTP client for API calls
- **React Toastify** - Elegant notifications

### Backend
- **FastAPI** - High-performance Python web framework
- **LangChain** - AI application framework
- **Google Gemini AI** - Large language model and embeddings
- **Pinecone** - Vector database for semantic search
- **PostgreSQL** - Relational database for user data and transcripts
- **SQLAlchemy** - Python SQL toolkit and ORM
- **JWT** - JSON Web Tokens for authentication

### AI/ML
- **Google Generative AI** - Gemini 1.5 Flash model
- **LangChain Retrievers** - Multi-query retrieval system
- **Vector Embeddings** - Semantic search capabilities
- **RAG Pipeline** - Retrieval-augmented generation

---

## 📋 Prerequisites

- Python 
- Node.js 
- Google AI API key
- Pinecone API key
- PostgreSQL database

---

## 🔧 Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/youtube-rag-assistant.git
cd youtube-rag-assistant
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database URL
```

### 3. Environment Variables
Create a `.env` file in the backend directory:
```env
# AI APIs
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost/youtube_rag

# JWT
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256



### 4. Database Setup
```bash
# Install PostgreSQL and create database
createdb youtube_rag

# Run migrations (if using Alembic)
alembic upgrade head
```

### 5. Frontend Setup
```bash
# Navigate to extension directory
cd ../extension

# Install dependencies
npm install

# Build the extension
npm run build
```

### 6. Chrome Extension Installation
1. Open Chrome and go to `chrome://extensions/`
2. Enable "Developer mode"
3. Click "Load unpacked" and select the `extension/build` folder
4. The extension icon should appear in your Chrome toolbar

---

## 🚀 Usage

### 1. Start the Backend Server
```bash
cd backend
python main.py
# Server will start on http://localhost:8000
```

### 2. Using the Extension
1. **Navigate** to any YouTube video
2. **Click** the extension icon in your Chrome toolbar
3. **Sign up/Login** to create an account
4. **Transcribe** the video by clicking "Transcribe Video"
5. **Ask questions** about the video content
6. **Save** transcripts for future reference

### 3. Features in Action

#### Transcription
- Click "Transcribe Video" to process the YouTube video
- The extension automatically extracts video ID, title, and channel name
- Transcript is processed and stored in vector database

#### Q&A Interface
- Type your question in the text area
- Click "Ask" to get AI-powered answers
- Supports both specific questions and summary requests

#### Transcript Management
- Save transcripts to your personal library
- Load previously saved transcripts
- View all your saved transcripts in the sidebar

---

## 🏗️ Architecture

### System Overview
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Chrome         │    │  FastAPI        │    │  External       │
│  Extension      │────│  Backend        │────│  Services       │
│  (React)        │    │  (Python)       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ├── Pinecone (Vector DB)
                                ├── PostgreSQL (User Data)
                                └── Google AI (LLM & Embeddings)
```

### RAG Pipeline
1. **Transcription**: YouTube video → Text transcript
2. **Chunking**: Split transcript into manageable chunks
3. **Embedding**: Convert chunks to vector embeddings
4. **Indexing**: Store embeddings in Pinecone
5. **Retrieval**: Find relevant chunks for user queries
6. **Generation**: Use LLM to generate contextual answers

---

## 🔐 Security Features

- **JWT Authentication**: Secure token-based user authentication
- **Password Hashing**: Bcrypt for secure password storage
- **CORS Configuration**: Proper cross-origin resource sharing
- **Input Validation**: Pydantic models for request validation
- **Environment Variables**: Secure API key management

---

## 📊 API Endpoints

### Authentication
- `POST /signup` - Create new user account
- `POST /login` - User login with JWT token

### Transcription
- `POST /transcribe` - Transcribe YouTube video
- `POST /ask` - Ask questions about video content

### Transcript Management
- `GET /transcripts` - Get user's saved transcripts
- `GET /transcripts/{video_id}` - Get specific transcript
- `PATCH /save/{video_id}` - Save transcript to user library

---

## 🚀 Deployment

### Backend (Render)
1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set environment variables in Render dashboard
4. Deploy with automatic builds on push

### Extension (Chrome Web Store)
1. Create a developer account
2. Package the extension as a .zip file
3. Upload to Chrome Web Store
4. Complete the review process



## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
