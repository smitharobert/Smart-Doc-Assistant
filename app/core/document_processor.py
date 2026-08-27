import docx 
from pypdf import PdfReader

class DocumentProcessor:
    def extract_text_from_docx(self, file_path):
        doc = docx.Document(file_path)
        text_list = []
        for d in doc.paragraphs:
            text_list.append(d.text)
        return "\n".join(text_list) 

    def extract_text_from_pdf(self, file_path):
        reader = PdfReader(file_path)
        text_list = []
        for page in reader.pages:
            text_list.append(page.extract_text())
        return "\n".join(text_list)

    def chunk_text(self, text, chunk_size=50, overlap=10):
        words = text.split()
        stepsize = chunk_size - overlap
        chunks = []
        start = 0
        while start < len(words):
            chunk_words = words[start:start+chunk_size]
            if len(chunk_words) >= 15:
                chunks.append(" ".join(chunk_words))
            start += stepsize
        return chunks
