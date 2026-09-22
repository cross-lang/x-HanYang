"""创建用户用例测试。"""

import pytest


class TestCreateUserHandler:
    """CreateUserHandler 测试。"""

    def test_create_user_success(self):
        """正常创建用户应成功返回。"""
        # TODO: 使用 mock repository 实现测试
        pass

    def test_duplicate_email_raises_conflict(self):
        """重复邮箱应抛出 ConflictException。"""
        # TODO: 实现测试
        pass

    def test_duplicate_username_raises_conflict(self):
        """重复用户名应抛出 ConflictException。"""
        # TODO: 实现测试
        pass
