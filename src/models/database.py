from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Enum, Text, Boolean, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from core.database import Base
import enum
import uuid

class TierEnum(str, enum.Enum):
    free = "free"
    pro = "pro"
    enterprise = "enterprise"

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(36), primary_key=True)
    name = Column(String(255), unique=True, nullable=False)
    slug = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True)
    stripe_customer_id = Column(String(255), unique=True, nullable=True)
    tier = Column(Enum(TierEnum), default=TierEnum.free)
    max_monthly_tokens = Column(Integer, default=100000)
    max_concurrent_requests = Column(Integer, default=5)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True)

    users = relationship("User", back_populates="tenant")
    api_keys = relationship("APIKey", back_populates="tenant")
    knowledge_bases = relationship("KnowledgeBase", back_populates="tenant")
    usage_metrics = relationship("UsageMetric", back_populates="tenant")
    invoices = relationship("Invoice", back_populates="tenant")
    chat_sessions = relationship("ChatSession", back_populates="tenant")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    role = Column(String(20), default="user")
    name = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="users")

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    key = Column(String(64), unique=True, index=True)
    secret_hash = Column(String(255))
    name = Column(String(255))
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    tenant = relationship("Tenant", back_populates="api_keys")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    name = Column(String(255))
    description = Column(Text, nullable=True)
    storage_type = Column(String(50), default="local")
    storage_path = Column(String(500))
    doc_count = Column(Integer, default=0)
    last_indexed = Column(DateTime, nullable=True)
    index_status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="knowledge_bases")
    documents = relationship("Document", back_populates="knowledge_base")
    chat_sessions = relationship("ChatSession", back_populates="knowledge_base")

class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True)
    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id"), index=True)
    filename = Column(String(500))
    source_url = Column(String(500), nullable=True)
    file_hash = Column(String(64), unique=True)
    content_size_bytes = Column(Integer)
    doc_count = Column(Integer)
    indexed_at = Column(DateTime, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    knowledge_base = relationship("KnowledgeBase", back_populates="documents")

class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    knowledge_base_id = Column(String(36), ForeignKey("knowledge_bases.id"), index=True, nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    title = Column(String(500), default="New Chat")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    total_tokens_used = Column(Integer, default=0)

    tenant = relationship("Tenant", back_populates="chat_sessions")
    knowledge_base = relationship("KnowledgeBase", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True)
    session_id = Column(String(36), ForeignKey("chat_sessions.id"), index=True)
    role = Column(String(10))
    content = Column(Text)
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    sources = Column(Text, default="[]")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    session = relationship("ChatSession", back_populates="messages")

class UsageMetric(Base):
    __tablename__ = "usage_metrics"

    id = Column(Integer, primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    date = Column(DateTime, default=datetime.utcnow, index=True)
    chat_sessions = Column(Integer, default=0)
    total_prompt_tokens = Column(Integer, default=0)
    total_completion_tokens = Column(Integer, default=0)
    total_inference_ms = Column(Integer, default=0)
    gpu_seconds_used = Column(Float, default=0)

    tenant = relationship("Tenant", back_populates="usage_metrics")

class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(String(36), primary_key=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id"), index=True)
    stripe_invoice_id = Column(String(255), unique=True, nullable=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    base_tier_cost = Column(Float)
    overage_tokens = Column(Integer, default=0)
    overage_cost = Column(Float, default=0)
    total_amount = Column(Float)
    status = Column(String(20), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime, nullable=True)

    tenant = relationship("Tenant", back_populates="invoices")

class TrackedRepo(Base):
    __tablename__ = "tracked_repos"

    id = Column(Integer, primary_key=True)
    repo_name = Column(String(255), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime, nullable=True)
    doc_count = Column(Integer, default=0)

class RepoSync(Base):
    __tablename__ = "repo_syncs"

    id = Column(Integer, primary_key=True)
    repo_name = Column(String(255), index=True)
    last_synced = Column(DateTime, default=datetime.utcnow)
    doc_count = Column(Integer)
    status = Column(String(20), default="success")
    error_message = Column(Text, nullable=True)
