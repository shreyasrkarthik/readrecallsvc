"""
Pydantic schemas for API request/response models
"""

from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime


# User schemas
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    is_active: bool
    role: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


# Auth schemas
class Token(BaseModel):
    token: str
    user: UserResponse


# Book schemas
class BookCreate(BaseModel):
    title: str
    author: str
    coverUrl: Optional[str] = None
    epubUrl: Optional[str] = None
    isPublicDomain: bool = False


class BookUpload(BaseModel):
    filename: str
    content_type: str


class BookResponse(BaseModel):
    id: str
    title: str
    author: str
    coverUrl: Optional[str] = None
    epubUrl: Optional[str] = None
    fileName: Optional[str] = None
    s3Key: Optional[str] = None
    uploadBucketName: Optional[str] = None
    processingStatus: Optional[str] = None
    isPublicDomain: bool
    uploadedById: Optional[str] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
    readingState: Optional[Dict[str, Any]] = None
    sections: Optional[List[Dict[str, Any]]] = None

    model_config = ConfigDict(from_attributes=True)


# Summary schemas
class SummaryResponse(BaseModel):
    id: str
    bookId: str
    userId: Optional[str] = None
    progress: int
    content: str
    createdAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Character schemas
class CharacterResponse(BaseModel):
    id: str
    bookId: str
    userId: Optional[str] = None
    progress: int
    name: str
    description: str
    charactersList: Optional[str] = None
    createdAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Reading State schemas
class ReadingStateUpdate(BaseModel):
    position: int
    currentReadingPercentage: Optional[int] = None
    totalLocations: Optional[int] = None


class ReadingStateResponse(BaseModel):
    id: str
    userId: str
    bookId: str
    position: int
    currentReadingPercentage: Optional[int] = None
    totalLocations: Optional[int] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# Upload response schemas
class UploadResponse(BaseModel):
    upload_url: Optional[str] = None
    upload_path: Optional[str] = None
    s3_key: Optional[str] = None
    book_id: str
    message: str


# Search schemas
class SearchQuery(BaseModel):
    query: str
    size: Optional[int] = 10


# Health check schema
class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: Optional[str] = None
    message: Optional[str] = None


# Error schemas
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
