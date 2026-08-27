from dotenv import load_dotenv
from app.core.document_processor import DocumentProcessor
from app.core.rag_engine import RagEngine
load_dotenv() 
processor=DocumentProcessor()
engine=RagEngine() 
raw_text = "The human brain is the command center of the body, controlling thoughts, memory, balance, movement, emotions, and all vital functions"
chunks = processor.chunk_text(raw_text) 
engine.add_documents(chunks)
answer = engine.answer_question("what does the brain control?")
print(answer)