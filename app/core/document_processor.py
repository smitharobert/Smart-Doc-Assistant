import docx
from pypdf import PdfReader

class DocumentProcessor:
    def extract_text_from_docx(self,file_path:str)->str:
        doc=docx.Document(file_path)
        text_list=[]
        for para in doc.paragraphs:
            text_list.append(para.text)
        return "\n".join(text_list)
    
    def extract_text_from_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text_list = []
        for page in reader.pages:
            text_list.append(page.extract_text())
        return "\n".join(text_list)

    def chunk_text(self,text:str,chunk_size=50, overlap=10) -> list[str]:
        words = text.split()
        stepsize = chunk_size - overlap
        chunks = []
        start = 0
        while start < len(words):
            chunk_words = words[start:start + chunk_size]
            if len(chunk_words) >= 15:
                chunks.append(" ".join(chunk_words))
            start += stepsize
        return chunks


        
