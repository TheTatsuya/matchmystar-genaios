import uuid
from typing import List

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.annotations import (
    created_at,
    int_pk,
    last_invoked_at,
    not_null_json_column,
    not_null_json_column_flow,
    updated_at,
    uuid_pk,
)
from src.db.base import Base


class UserProjectAssociation(Base):
    __tablename__ = "user_project_associations"
    id: Mapped[int] = mapped_column(autoincrement=True, index=True, primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )


class UserTeamAssociation(Base):
    __tablename__ = "user_team_associations"
    id: Mapped[int] = mapped_column(autoincrement=True, index=True, primary_key=True)

    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    team_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("teams.id", ondelete="CASCADE"), nullable=False, index=True
    )


class AgentProjectAssociation(Base):
    __tablename__ = "agent_project_associations"
    id: Mapped[int] = mapped_column(autoincrement=True, index=True, primary_key=True)

    agent_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )


class AgentFlowProjectAssociation(Base):
    __tablename__ = "agentflow_project_associations"
    id: Mapped[int] = mapped_column(autoincrement=True, index=True, primary_key=True)

    flow_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("agentworkflows.id", ondelete="CASCADE"), nullable=False, index=True
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )


class User(Base):
    id: Mapped[uuid_pk]
    username: Mapped[str] = mapped_column(index=True, unique=True)
    password: Mapped[str]  # hash
    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    agents: Mapped[List["Agent"]] = relationship(  # noqa: F821
        back_populates="creator",
    )

    workflows: Mapped[List["AgentWorkflow"]] = relationship(  # noqa: F821
        back_populates="creator",
    )

    projects: Mapped[List["Project"]] = relationship(
        secondary="user_project_associations", back_populates="users"
    )

    teams: Mapped[List["Team"]] = relationship(
        secondary="user_team_associations", back_populates="members"
    )

    logs: Mapped[List["Log"]] = relationship(
        back_populates="creator",
    )

    files: Mapped[List["File"]] = relationship(
        back_populates="creator",
    )

    model_configs: Mapped[List["ModelConfig"]] = relationship(
        back_populates="creator",
    )

    def __repr__(self) -> str:
        return f"<User(uuid={self.id!r}, username={self.username!r})>"


class Agent(Base):
    id: Mapped[uuid_pk]

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    jwt: Mapped[str] = mapped_column(unique=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    creator: Mapped["User"] = relationship(back_populates="agents")  # noqa: F821

    input_parameters: Mapped[not_null_json_column]

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
    last_invoked_at: Mapped[last_invoked_at]
    is_active: Mapped[bool] = mapped_column(nullable=False)

    projects: Mapped[List["Project"]] = relationship(
        secondary="agent_project_associations", back_populates="agents"
    )


class AgentWorkflow(Base):
    id: Mapped[uuid_pk]

    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    flow: Mapped[not_null_json_column_flow]

    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    creator: Mapped["User"] = relationship(back_populates="workflows")  # noqa: F821

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    projects: Mapped[List["Project"]] = relationship(
        secondary="agentflow_project_associations", back_populates="flows"
    )


class Project(Base):
    id: Mapped[uuid_pk]

    name: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[List["User"]] = relationship(
        secondary="user_project_associations", back_populates="projects"
    )

    agents: Mapped[List["Agent"]] = relationship(
        secondary="agent_project_associations", back_populates="projects"
    )

    flows: Mapped[List["AgentWorkflow"]] = relationship(
        secondary="agentflow_project_associations", back_populates="projects"
    )


class Team(Base):
    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(unique=True, nullable=False)

    members: Mapped[List["User"]] = relationship(
        secondary="user_team_associations", back_populates="teams"
    )


class Log(Base):
    id: Mapped[int_pk]

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    agent_id: Mapped[str] = mapped_column(index=True, nullable=True)
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    creator: Mapped["User"] = relationship(back_populates="logs")

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]

    message: Mapped[str] = mapped_column(nullable=False)
    log_level: Mapped[str] = mapped_column(nullable=False)  # TODO: enum


class File(Base):
    id: Mapped[uuid_pk]

    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=True
    )
    request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=True
    )
    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    creator: Mapped["User"] = relationship(back_populates="files")
    mimetype: Mapped[str]
    original_name: Mapped[str]
    internal_name: Mapped[str]
    internal_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), index=True, nullable=False
    )
    from_agent: Mapped[bool]


class ModelConfig(Base):
    id: Mapped[uuid_pk]
    name: Mapped[str] = mapped_column(unique=True)
    model: Mapped[str] = mapped_column(nullable=False, index=True)
    provider: Mapped[str] = mapped_column(nullable=False, index=True)

    system_prompt: Mapped[str]
    temperature: Mapped[float] = mapped_column(default=0.7)

    credentials: Mapped[not_null_json_column]  # api_key must be hashed

    creator_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=True, index=True
    )
    creator: Mapped["User"] = relationship(back_populates="model_configs")

    created_at: Mapped[created_at]
    updated_at: Mapped[updated_at]
