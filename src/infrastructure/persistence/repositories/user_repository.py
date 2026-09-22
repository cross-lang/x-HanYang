"""用户仓储实现。

实现 domain/user/repository.py 中定义的 UserRepository 接口。
负责领域模型 ↔ ORM 模型的双向转换。
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.domain.user.user import User
from src.domain.user.value_objects import Email, UserStatus
from src.domain.user.repository import UserRepository
from src.domain.shared.domain_exception import ConflictException
from src.infrastructure.persistence.orm.user_mapping import UserTable


class SqlUserRepository(UserRepository):
    """SQLAlchemy 用户仓储实现。

    职责：
    1. 实现领域层定义的 UserRepository 接口
    2. 领域模型 ↔ ORM 表模型的双向转换
    3. 处理数据库异常并转换为领域异常
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    # ── 查询 ──────────────────────────────────────────

    def find_by_id(self, id: int) -> User | None:
        stmt = select(UserTable).where(UserTable.id == id, UserTable.deleted_at.is_(None))
        row = self._session.execute(stmt).scalars().first()
        return self._to_domain(row) if row else None

    def find_by_email(self, email: str) -> User | None:
        stmt = select(UserTable).where(UserTable.email == email)
        row = self._session.execute(stmt).scalars().first()
        return self._to_domain(row) if row else None

    def find_by_username(self, username: str) -> User | None:
        stmt = select(UserTable).where(UserTable.username == username)
        row = self._session.execute(stmt).scalars().first()
        return self._to_domain(row) if row else None

    def search(
        self,
        keyword: str | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[User], int]:
        from sqlalchemy import func

        conditions = [UserTable.deleted_at.is_(None)]
        if keyword:
            like = f"%{keyword}%"
            conditions.append((UserTable.username.like(like)) | (UserTable.email.like(like)))
        if status:
            conditions.append(UserTable.status == status)

        # 总数
        count_stmt = select(func.count()).select_from(select(UserTable).where(*conditions).subquery())
        total = self._session.execute(count_stmt).scalar() or 0

        # 分页
        stmt = select(UserTable).where(*conditions).offset(skip).limit(limit)
        rows = list(self._session.execute(stmt).scalars().all())

        return [self._to_domain(r) for r in rows], total

    # ── 写入 ──────────────────────────────────────────

    def save(self, user: User) -> None:
        try:
            if user.id and user.id > 0:
                # 更新
                existing = self._session.get(UserTable, user.id)
                if existing:
                    self._update_orm(existing, user)
            else:
                # 新增
                orm = self._to_orm(user)
                self._session.add(orm)
                self._session.flush()
                user.id = orm.id
        except Exception:
            self._session.rollback()
            raise

    def delete(self, id: int) -> bool:
        row = self._session.get(UserTable, id)
        if row is None:
            return False
        from datetime import datetime, timezone

        row.deleted_at = datetime.now(timezone.utc)
        self._session.flush()
        return True

    # ── 转换方法 ──────────────────────────────────────

    @staticmethod
    def _to_domain(row: UserTable) -> User:
        """ORM → 领域模型。"""
        return User(
            id=row.id,
            username=row.username,
            email=Email(row.email),
            password_hash=row.password_hash or "",
            name=row.name,
            age=row.age,
            phone=row.phone,
            avatar_url=row.avatar_url,
            role_id=row.role_id,
            status=UserStatus(row.status) if row.status else UserStatus.ACTIVE,
            last_login_at=row.last_login_at,
            last_login_ip=row.last_login_ip,
            created_at=row.created_at,
            updated_at=row.updated_at,
            deleted_at=row.deleted_at,
        )

    @staticmethod
    def _to_orm(user: User) -> UserTable:
        """领域模型 → ORM。"""
        return UserTable(
            username=user.username,
            email=user.email.value,
            password_hash=user.password_hash,
            name=user.name,
            age=user.age,
            phone=user.phone,
            avatar_url=user.avatar_url,
            role_id=user.role_id,
            status=user.status.value,
        )

    @staticmethod
    def _update_orm(row: UserTable, user: User) -> None:
        """将领域模型的变更同步到已加载的 ORM 对象。"""
        row.username = user.username
        row.email = user.email.value
        row.password_hash = user.password_hash
        row.name = user.name
        row.age = user.age
        row.phone = user.phone
        row.avatar_url = user.avatar_url
        row.role_id = user.role_id
        row.status = user.status.value
        row.deleted_at = user.deleted_at
