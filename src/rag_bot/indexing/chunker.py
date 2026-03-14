from __future__ import annotations
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.rag_bot.config import config
from src.rag_bot.model import DocumentRecord,ChunkRecord
from src.rag_bot.utils import make_doc_id

class DocumentChunker:
    def __init__(self)->None:
        self.splitter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=["\n\n","\n","."," ",""],
        )

    def chunk_documents(self,docs:list[DocumentRecord])->list[ChunkRecord]:
        chunks:list[ChunkRecord]=[]
        for doc in docs:
            split_texts=self.splitter.split_text(doc.text)
            for idx,chunk_text in enumerate(split_texts):
                chunk_id=make_doc_id(doc.doc_id,str(idx))
                metadata=dict(doc.metadata)
                metadata.update(
                    {
                        "chunk_idx":idx,
                        "parent_doc_id":doc.doc_id,
                    }
                )
                chunks.append(ChunkRecord(
                    chunk_id=chunk_id,
                    parent_doc_id=doc.doc_id,
                    text=chunk_text,
                    metadata=metadata,
                ))
        print(chunks)
        return chunks
