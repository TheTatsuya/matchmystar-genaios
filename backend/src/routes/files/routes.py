import shutil
from typing import Optional
import uuid
import logging

from pathlib import Path
from fastapi import (
    UploadFile,
    File,
    Form,
    HTTPException,
    APIRouter,
    status,
)
from fastapi.responses import FileResponse
from pydantic import ValidationError
from src.utils.validation_error_handler import validation_exception_handler
from src.auth.dependencies import CurrentUserByAgentOrUserTokenDependency
from src.schemas.api.files.dto import FileIdDTO, FileDTO
from src.core.settings import get_settings
from src.repositories.files import files_repo
from src.schemas.api.files.schemas import FileCreate
from src.db.session import AsyncDBSession
from src.utils.constants import FILES_DIR

logger = logging.getLogger(__name__)
settings = get_settings()


files_router = APIRouter(tags=["Files"])


@files_router.get("/files/{file_id}", response_class=FileResponse)
async def get_file(
    file_id: str,
    db: AsyncDBSession,
    user: CurrentUserByAgentOrUserTokenDependency,
):
    file = await files_repo.get_file_content_by_id(
        db=db, file_id=file_id, user_model=user
    )
    return FileResponse(
        path=file.fp,
        media_type=file.mime_type or "application/octet-stream",
        filename=file.file_name,
    )


@files_router.get("/files/{file_id}/metadata", response_model=FileDTO)
async def get_file_metadata(
    file_id: uuid.UUID,
    db: AsyncDBSession,
    user: CurrentUserByAgentOrUserTokenDependency,
) -> Optional[FileDTO]:
    metadata = await files_repo.get_metadata_by_id(
        db=db, file_id=str(file_id), user_model=user
    )
    if not metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File with id {file_id} does not exist",
        )

    return metadata


@files_router.post("/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    db: AsyncDBSession,
    user: CurrentUserByAgentOrUserTokenDependency,
    file: UploadFile = File(...),
    request_id: Optional[uuid.UUID] = Form(None),
    session_id: Optional[uuid.UUID] = Form(None),
) -> Optional[FileIdDTO]:
    file_id = str(uuid.uuid4())
    internal_file_name = f"{file_id}{Path(file.filename).suffix or ''}"
    file_path = Path(FILES_DIR) / internal_file_name
    # TODO: if request_id and session_id: from_agent=True
    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        session_id = str(session_id) if session_id else None
        request_id = str(request_id) if request_id else None

        if request_id and session_id:
            file_in = FileCreate(
                id=file_id,
                session_id=session_id,
                request_id=request_id,
                mimetype=file.content_type,
                original_name=file.filename,
                internal_name=internal_file_name,
                internal_id=file_id,
                from_agent=True,
            )
        else:
            file_in = FileCreate(
                id=file_id,
                session_id=session_id,
                request_id=request_id,
                mimetype=file.content_type,
                original_name=file.filename,
                internal_name=internal_file_name,
                internal_id=file_id,
                from_agent=False,
            )

        new_file = await files_repo.create_by_user(
            db=db, obj_in=file_in, user_model=user
        )
        return FileIdDTO(id=str(new_file.id))

    except OSError as e:
        logger.critical(f"Failed to save file {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save file",
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=validation_exception_handler(e))


@files_router.get("/user/files/metadata")
async def get_files_metadata_by_user(
    db: AsyncDBSession,
    user: CurrentUserByAgentOrUserTokenDependency,
    limit: int = 100,
    offset: int = 0,
):
    files = await files_repo.get_files_metadata_by_user(
        db=db, user_model=user, limit=limit, offset=offset
    )
    return files
