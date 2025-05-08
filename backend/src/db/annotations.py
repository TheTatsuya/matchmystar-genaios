from datetime import datetime
from typing import Annotated, Dict, Any, List
import uuid
from sqlalchemy.orm import mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy import func

int_pk = Annotated[
    int,
    mapped_column(primary_key=True, index=True, autoincrement=True),
]
uuid_pk = Annotated[
    str,
    mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    ),
]
created_at = Annotated[datetime, mapped_column(server_default=func.now())]
updated_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]
last_invoked_at = Annotated[
    datetime, mapped_column(server_default=func.now(), onupdate=datetime.now)
]

not_null_json_column = Annotated[Dict[str, Any], mapped_column(JSON)]
not_null_json_column_flow = Annotated[List[Dict[str, str]], mapped_column(JSON)]
