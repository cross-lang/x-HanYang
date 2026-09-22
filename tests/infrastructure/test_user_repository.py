"""用户仓储实现测试。"""

import pytest


class TestSqlUserRepository:
    """SqlUserRepository 测试。"""

    def test_save_and_find_by_id(self):
        """保存后应能通过 ID 查找。"""
        # TODO: 使用 SQLite 内存数据库实现测试
        pass

    def test_find_by_email(self):
        """应能通过邮箱查找用户。"""
        # TODO: 实现测试
        pass

    def test_domain_orm_conversion(self):
        """领域模型与 ORM 模型应能正确双向转换。"""
        # TODO: 实现测试
        pass
