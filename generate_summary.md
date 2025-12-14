# Blog Summary Generator 使用说明

```
v3
created: 2025-12-14T09:48+08:00
published: 2025-12-14T15:29+08:00
```


## 功能

-   扫描目录下所有 markdown 文件
-   解析 v2 标签中的元数据
-   验证必需字段（v2, created, published, category）
-   生成包含 timeline 和 categories 的 SUMMARY.md 文件

## 使用方法

### 基本用法

```bash
python generate_summary.py
```

这将扫描当前目录并生成 SUMMARY.md 文件。

### 指定输出文件

```bash
python generate_summary.py --output custom_summary.md
```

### 指定扫描目录

```bash
python generate_summary.py --directory /path/to/blog
```

### 组合参数

```bash
python generate_summary.py --output summary.md --directory ./myblog
```

## v2 标签格式

脚本支持两种元数据格式：

### 格式 1（逗号分隔）

```
v3
created, 2025-05-02T16:08+08:00
published, 2025-05-02T17:11+08:00
category: spirit
tags: energy, efficiency
modified, 2025-05-03T11:02+08:00, 修正标点符号
```

### 格式 2（冒号分隔）

```
v3
created: 2025-05-02T16:08+08:00
published: 2025-05-02T17:11+08:00
category: spirit
tags: energy, efficiency
modified: 2025-05-03T11:02+08:00, 修正标点符号
```

## 必需字段

-   `created`: 文章创建时间
-   `published`: 文章发布时间
-   `category`: 文章分类

## 可选字段

-   `tags`: 文章标签列表
-   `modified`: 文章修改记录

## 输出格式

生成的 SUMMARY.md 包含三个部分：

1. **timeline**: 按年份和发布日期组织的文章时间线
2. **categories**: 按分类组织的文章列表
3. **tags**: 标签部分（待脚本生成）

## 错误处理

-   ❌ **错误**: 缺少必需字段、缺少 v2 标签等严重问题
-   ⚠️ **警告**: 缺少可选字段（tags、modified）
