"""用户聚合根领域模型测试。"""

import pytest


class TestUser:
    """User 聚合根测试。"""

    def test_create_user_emits_event(self):
        """创建用户应产生 UserCreated 事件。"""
        # TODO: 实现测试
        pass

    def test_change_email_emits_event(self):
        """变更邮箱应产生 EmailChanged 事件。"""
        # TODO: 实现测试
        pass

    def test_lock_user(self):
        """锁定用户应改变状态。"""
        # TODO: 实现测试
        pass

    def test_soft_delete(self):
        """软删除应设置 deleted_at。"""
        # TODO: 实现测试
        pass


class TestEmail:
    """Email 值对象测试。"""

    def test_valid_email(self):
        """合法邮箱应成功构造。"""
        # TODO: 实现测试
        pass

    def test_invalid_email_raises(self):
        """非法邮箱应抛出 ValidationException。"""
        # TODO: 实现测试
        pass


class TestPassword:
    """Password 值对象测试。"""

    def test_short_password_raises(self):
        """短密码应抛出 ValidationException。"""
        # TODO: 实现测试
        pass

    def test_password_hashing(self):
        """密码哈希应可验证。"""
        # TODO: 实现测试
        pass
