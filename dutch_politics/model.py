from pydantic import BaseModel
from typing import List, Optional


class StatementQuery(BaseModel):
    politician_name: str
    statement_description: str


class Reference(BaseModel):
    title: str
    subtitle: str
    content_url_html: str
    content_url_pdf: str
    publication_date: str


class EntryElement(BaseModel):
    type: str
    speaker_name: Optional[str] = None
    speaker_name_title: str
    text: str


class PoliticalEntry(BaseModel):
    reference: Reference
    entry_elements: List[EntryElement]
