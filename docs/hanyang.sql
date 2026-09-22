-- ============================================================
-- 汉阳（HanYang）数据库初始化脚本
-- 
-- 数据库: MySQL 8.0+
-- 字符集: utf8mb4
-- ============================================================

-- 创建数据库
CREATE DATABASE IF NOT EXISTS `hanyang`
    DEFAULT CHARACTER SET utf8mb4
    DEFAULT COLLATE utf8mb4_unicode_ci;

USE `hanyang`;

-- ============================================================
-- 用户表
-- ============================================================
CREATE TABLE IF NOT EXISTS `users` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `username` VARCHAR(50) NOT NULL COMMENT '用户名',
    `email` VARCHAR(100) NOT NULL COMMENT '邮箱',
    `name` VARCHAR(100) NULL COMMENT '姓名',
    `age` INT NULL COMMENT '年龄',
    `password_hash` VARCHAR(255) NULL COMMENT '密码哈希',
    `phone` VARCHAR(20) NULL COMMENT '手机号',
    `avatar_url` VARCHAR(500) NULL COMMENT '头像URL',
    `role_id` BIGINT NULL COMMENT '主角色ID',
    `status` VARCHAR(20) NOT NULL DEFAULT 'active' COMMENT '状态',
    `last_login_at` DATETIME NULL COMMENT '最后登录时间',
    `last_login_ip` VARCHAR(45) NULL COMMENT '最后登录IP',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME NULL COMMENT '软删除时间',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `uk_email` (`email`),
    INDEX `idx_role_id` (`role_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户表';

-- ============================================================
-- 角色表
-- ============================================================
CREATE TABLE IF NOT EXISTS `roles` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_name` VARCHAR(50) NOT NULL COMMENT '角色名称',
    `role_code` VARCHAR(50) NOT NULL COMMENT '角色编码',
    `description` VARCHAR(255) NULL COMMENT '角色描述',
    `role_type` VARCHAR(20) NOT NULL DEFAULT 'custom' COMMENT '类型',
    `status` VARCHAR(20) NOT NULL DEFAULT 'enabled' COMMENT '状态',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    `deleted_at` DATETIME NULL COMMENT '软删除时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色表';

-- ============================================================
-- 权限表
-- ============================================================
CREATE TABLE IF NOT EXISTS `permissions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `perm_code` VARCHAR(100) NOT NULL COMMENT '权限编码',
    `perm_name` VARCHAR(100) NOT NULL COMMENT '权限名称',
    `module` VARCHAR(50) NOT NULL COMMENT '所属模块',
    `operation` VARCHAR(20) NOT NULL COMMENT '操作类型',
    `description` VARCHAR(255) NULL COMMENT '权限说明',
    `sort_order` INT NOT NULL DEFAULT 0 COMMENT '排序序号',
    PRIMARY KEY (`id`),
    UNIQUE INDEX `uk_perm_code` (`perm_code`),
    INDEX `idx_module` (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='权限表';

-- ============================================================
-- 角色权限关联表
-- ============================================================
CREATE TABLE IF NOT EXISTS `role_permissions` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `role_id` BIGINT NOT NULL COMMENT '角色ID',
    `permission_id` BIGINT NOT NULL COMMENT '权限ID',
    PRIMARY KEY (`id`),
    INDEX `idx_rp_role_id` (`role_id`),
    INDEX `idx_rp_permission_id` (`permission_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='角色权限关联表';

-- ============================================================
-- 审计日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS `audit_logs` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `entity_type` VARCHAR(50) NOT NULL COMMENT '实体类型',
    `entity_id` INT NOT NULL COMMENT '实体ID',
    `action` VARCHAR(20) NOT NULL COMMENT '操作类型',
    `operator_id` INT NULL COMMENT '操作人ID',
    `operator_name` VARCHAR(50) NULL COMMENT '操作人名称',
    `before_data` TEXT NULL COMMENT '变更前数据',
    `after_data` TEXT NULL COMMENT '变更后数据',
    `ip_address` VARCHAR(45) NULL COMMENT 'IP地址',
    `remarks` VARCHAR(255) NULL COMMENT '备注',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='审计日志表';

-- ============================================================
-- 登录日志表
-- ============================================================
CREATE TABLE IF NOT EXISTS `login_logs` (
    `id` INT NOT NULL AUTO_INCREMENT COMMENT '主键ID',
    `user_id` INT NULL COMMENT '用户ID',
    `login_type` VARCHAR(20) NOT NULL COMMENT '登录方式',
    `status` VARCHAR(20) NOT NULL COMMENT '登录状态',
    `ip_address` VARCHAR(45) NULL COMMENT 'IP地址',
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录日志表';

-- ============================================================
-- 种子数据
-- ============================================================

-- 超级管理员角色
INSERT INTO `roles` (`role_name`, `role_code`, `description`, `role_type`, `status`)
SELECT '超级管理员', 'super_admin', '系统内置超级管理员角色，拥有全部权限', 'system', 'enabled'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `roles` WHERE `role_code` = 'super_admin');

-- 超级管理员用户 (密码: admin@123456)
INSERT INTO `users` (`username`, `email`, `password_hash`, `phone`, `avatar_url`, `role_id`, `status`)
SELECT 'superadmin', 'superadmin@system.local', 
       '$2b$12$LJ3m4ys8Gz5Y9rGqKq.5xOQ9x6v5v5v5v5v5v5v5v5v5v5v5v5v5',  -- 需要替换为实际哈希值
       NULL, NULL, 
       (SELECT id FROM roles WHERE role_code = 'super_admin'),
       'active'
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `users` WHERE `username` = 'superadmin');

-- 内置权限
INSERT INTO `permissions` (`perm_code`, `perm_name`, `module`, `operation`, `description`, `sort_order`)
SELECT 'user:view', '查看用户', 'user', 'view', '查看用户列表与详情', 1
FROM DUAL
WHERE NOT EXISTS (SELECT 1 FROM `permissions` WHERE `perm_code` = 'user:view');

-- 角色权限关联
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r, `permissions` p
WHERE r.role_code = 'super_admin' AND p.perm_code = 'user:view'
AND NOT EXISTS (
    SELECT 1 FROM `role_permissions` rp 
    WHERE rp.role_id = r.id AND rp.permission_id = p.id
);