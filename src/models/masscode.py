from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class SnippetContent(BaseModel):
    label: str = Field(...)
    language: str = Field(...)
    value: str = Field(...)

    class Config:
        allow_population_by_field_name = True

class Snippet(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    content: List[SnippetContent] = Field(...)
    description: Optional[str] = Field(default=None)
    folderId: str = Field(default="")
    tagsIds: List[str] = Field(default_factory=list)
    isDeleted: bool = Field(default=False)
    isFavorites: bool = Field(default=False)
    createdAt: int = Field(...)  # timestamp in milliseconds
    updatedAt: int = Field(...)

    class Config:
        allow_population_by_field_name = True

class Folder(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    defaultLanguage: str = Field(...)
    parentId: Optional[str] = Field(default=None)
    isOpen: bool = Field(default=False)
    isSystem: bool = Field(default=False)
    createdAt: int = Field(...)
    updatedAt: int = Field(...)

    class Config:
        allow_population_by_field_name = True

class Tag(BaseModel):
    id: str = Field(...)
    name: str = Field(...)
    createdAt: int = Field(...)
    updatedAt: int = Field(...)

    class Config:
        allow_population_by_field_name = True

class MassCodeDB(BaseModel):
    folders: List[Folder] = Field(default_factory=list)
    snippets: List[Snippet] = Field(default_factory=list)
    tags: List[Tag] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True

    def add_default_folder(self) -> str:
        """Add default folder if none exists and return its ID"""
        if not self.folders:
            now = int(datetime.now().timestamp() * 1000)
            default_folder = Folder(
                id="default",
                name="Default",
                defaultLanguage="plain_text",
                createdAt=now,
                updatedAt=now
            )
            self.folders.append(default_folder)
            return default_folder.id
        return self.folders[0].id
