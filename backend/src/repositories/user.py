from typing import Any, Optional, Union

from src.auth.hashing import get_password_hash, verify_password
from src.repositories.base import CRUDBase
from src.models import User, Project
from src.schemas.api.user.schemas import UserCreate, UserUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class UserRepository(CRUDBase[User, UserCreate, UserUpdate]):
    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        default_project = Project(name="Default")
        db.add(default_project)
        await db.flush()

        db_obj = User(
            username=obj_in.username,
            password=get_password_hash(obj_in.password),
            projects=[default_project],
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: User,
        obj_in: Union[UserUpdate, dict[str, Any]],
    ) -> User:
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)
        if password := update_data.get("password"):
            hashed_password = get_password_hash(password)
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        return await super().update(db, db_obj=db_obj, obj_in=update_data)

    async def get_user_by_username(
        self, db: AsyncSession, *, username: str
    ) -> Optional[User]:
        res = await db.execute(select(User).where(User.username == username))  # type: ignore
        return res.scalars().first()

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        user: Optional[User] = await self.get_user_by_username(db, username=username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user


user_repo = UserRepository(User)
