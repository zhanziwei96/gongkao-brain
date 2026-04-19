# 公考大脑 (Gongkao Brain) 系统设计文档

**日期**: 2026-04-19
**状态**: 已确认
**版本**: v1.0

---

## 1. 项目概述

公考大脑是一个面向公务员考试和事业单位考试备考的智能化个人学习管理系统。系统深度集成 Graphify 知识图谱构建工具和 Karpathy Wiki 知识管理方法论，帮助用户高效管理行测错题、申论练习、素材积累，并通过 AI 对话随时获得学习指导。

### 1.1 目标用户

备考公务员考试（国考/省考）和事业单位考试的个人用户。

### 1.2 核心目标

- 行测：错题智能解析与分类、知识图谱可视化、80分目标拆解与追踪、每日进度自动记录
- 申论：答案要点匹配与彩色标记、素材知识图谱、作文打分与 AI 改写
- 全局：AI 对话面板随时答疑、Karpathy Wiki 知识库持续累积、Graphify 多源知识图谱构建

---

## 2. 需求总结

### 2.1 行测模块

1. **错题录入与解析**：上传题目（图片/文本/PDF），OCR 提取，AI 解析错因并自动分类
2. **知识图谱**：基于 Graphify 构建行测知识点图谱，可视化薄弱点（God 节点高亮）
3. **80分目标拆解**：根据用户历史数据动态调整各模块目标正确率，给出分数预测
4. **题目记录**：原始题目和答案的完整记录，支持历史追踪和导出
5. **每日进度**：自动记录做题数量、正确率、用时、各模块错题分布

### 2.2 申论模块

1. **答案匹配与彩色标记**：上传申论题目、自己的答案和多个标准答案，AI 逐点匹配并用颜色标记（绿/黄/红/蓝）
2. **素材知识图谱**：上传申论素材，Graphify 构建素材-话题-关键词关联图谱
3. **作文模板管理**：记录申论大作文模板，标注适用话题和作文类型
4. **作文打分与改写**：AI 四维打分（立意/结构/论证/语言），基于模板和素材生成改写建议

### 2.3 全局需求

1. **AI 对话面板**：页面右下角悬浮聊天窗口，SSE 流式输出，支持上下文感知和 Wiki 联动
2. **Karpathy Wiki 集成**：Ingest/Query/Lint 全流程，Markdown 知识库，Obsidian 兼容
3. **Graphify 集成**：多源解析（文本/图片/PDF）、增量构建、双图谱模式（行测+申论）
4. **多端访问**：Web 应用，支持电脑/平板/手机浏览器访问

---

## 3. 系统架构

### 3.1 分层架构

```
┌─────────────────────────────────────────────────────┐
│                    前端层 (Vue3 + TS)                  │
│  行测模块 │ 申论模块 │ 知识图谱 │ 进度面板 │ AI聊天    │
└─────────────────────────────────────────────────────┘
                         │ API (REST + SSE)
┌─────────────────────────────────────────────────────┐
│                   API网关 / 认证层                     │
│              (Nginx 反向代理 + JWT认证)                │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                   后端服务层 (FastAPI)                 │
│  用户管理 │ OCR服务 │ 知识图谱 │ Wiki管理 │ AI对话   │
│  行测引擎 │ 申论引擎 │ 文件存储 │ 任务队列           │
└─────────────────────────────────────────────────────┘
                         │
┌─────────────────────────────────────────────────────┐
│                    数据与基础设施层                     │
│  PostgreSQL │ Redis │ MinIO │ 外部AI API            │
│  (主数据库+pgvector) (缓存/队列) (对象存储) (Claude)  │
└─────────────────────────────────────────────────────┘
```

### 3.2 技术选型

| 层级 | 技术 | 选型理由 |
|------|------|---------|
| 前端框架 | Vue3 + Vite + Element Plus | 组件丰富，适合管理后台类应用，开发效率高 |
| 状态管理 | Pinia | Vue3 官方推荐，TypeScript 友好 |
| 图表/图谱 | ECharts + Graphify 输出 | ECharts 处理常规统计图表，Graphify 生成交互式知识图谱 HTML |
| 后端框架 | Python FastAPI | 异步性能优秀，与 Graphify（Python）同生态，AI 库丰富 |
| 数据库 | PostgreSQL + pgvector | 关系数据与向量检索一体化，避免多数据库运维；初期完全够用，远期预留 Milvus 接口 |
| 任务队列 | Celery + Redis | OCR 和知识图谱构建是耗时操作，需要异步处理 |
| 对象存储 | MinIO | 兼容 S3 API，本地部署友好，存储题目图片和素材文件 |
| AI 对话 | Claude API (SSE 流式) | 在页面聊天面板中实现流式回复体验 |
| 知识管理 | Karpathy Wiki 模式 | Markdown 知识库 + Schema 文档 + Ingest/Query/Lint 流程 |
| 容器化 | Docker Compose | 单服务器部署，运维简单 |

### 3.3 核心数据流

1. **用户上传题目/素材** -> 前端 -> FastAPI -> 若为图片则触发 Celery OCR 任务 -> 文本存入 PostgreSQL -> 触发 Graphify 增量构建
2. **构建知识图谱** -> Graphify 解析文本/图片 -> 生成 `graph.json` + `graph.html` -> 存入文件存储 -> 前端自动刷新
3. **AI 对话** -> 前端 SSE 连接 -> FastAPI 调用 Claude API（注入页面上下文）-> 流式返回 -> 支持一键 Ingest 到 Wiki
4. **行测错题分析** -> 用户输入知识点分类 -> 后端按分类统计 -> ECharts 渲染知识图谱 + 更新 Wiki 知识点页
5. **申论答案匹配** -> LLM 逐点对比用户答案与多个标准答案 -> 输出匹配结果（带颜色标记）-> 更新 Wiki 答题技巧页
6. **Karpathy Wiki Lint** -> 每周定时任务 -> LLM 检查矛盾、孤立页、过时内容 -> 生成 Lint 报告

---

## 4. 数据库设计

### 4.1 实体关系

```
users --┬--> aptitude_attempts --> aptitude_questions --> knowledge_nodes
        │                           (错题关联知识点)
        ├--> essay_answers --> essay_questions
        │      (用户答案匹配标准答案)
        ├--> essay_materials --> knowledge_nodes (素材知识图谱)
        ├--> essays --> essay_templates
        │      (作文打分+改写)
        ├--> daily_progress
        └--> wiki_pages (Karpathy Wiki)
```

### 4.2 核心表结构

#### users - 用户表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 用户唯一标识 |
| username | VARCHAR(50) | 用户名 |
| email | VARCHAR(100) | 邮箱 |
| password_hash | VARCHAR(255) | 密码哈希 |
| exam_type | VARCHAR(20) | 默认考试类型（国考副省级/行政执法/省考/事业单位） |
| created_at | TIMESTAMP | 创建时间 |

#### aptitude_questions - 行测题目

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 题目唯一标识 |
| user_id | UUID FK | 所属用户 |
| source_exam | VARCHAR(20) | 来源考试（国考副省级/行政执法/事业单位） |
| question_type | VARCHAR(20) | 题型（政治理论/常识判断/言语理解/数量关系/判断推理/资料分析） |
| question_text | TEXT | 题目文本 |
| question_image_url | VARCHAR(500) | 题目图片 URL |
| options | JSONB | 选项（A/B/C/D 文本） |
| correct_answer | VARCHAR(10) | 正确答案 |
| difficulty | INTEGER | 难度（1-5） |
| knowledge_node_ids | UUID[] | 关联知识点 ID 数组 |
| created_at | TIMESTAMP | 创建时间 |

#### aptitude_attempts - 行测答题记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录唯一标识 |
| user_id | UUID FK | 所属用户 |
| question_id | UUID FK | 关联题目 |
| user_answer | VARCHAR(10) | 用户答案 |
| is_correct | BOOLEAN | 是否正确 |
| time_spent_seconds | INTEGER | 用时（秒） |
| attempt_date | DATE | 答题日期 |
| is_mistake | BOOLEAN | 是否错题（用于快速筛选） |

#### knowledge_nodes - 知识点节点

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 节点唯一标识 |
| user_id | UUID FK | 所属用户 |
| name | VARCHAR(100) | 知识点名称 |
| category | VARCHAR(20) | 大类（行测/申论） |
| sub_category | VARCHAR(50) | 子类（如"逻辑判断-加强削弱"） |
| description | TEXT | 知识点描述 |
| embedding | VECTOR(1536) | pgvector 语义向量 |
| mistake_count | INTEGER | 关联错题数（用于 God 节点计算） |
| created_at | TIMESTAMP | 创建时间 |

#### knowledge_edges - 知识点关系

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 边唯一标识 |
| source_node_id | UUID FK | 源节点 |
| target_node_id | UUID FK | 目标节点 |
| relation_type | VARCHAR(20) | 关系类型（prerequisite/related/similar/contains/mistake_on/applies_to） |
| weight | FLOAT | 权重（0-1） |
| provenance | VARCHAR(20) | 来源（EXTRACTED/INFERRED/AMBIGUOUS） |
| created_at | TIMESTAMP | 创建时间 |

#### essay_questions - 申论题目

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 题目唯一标识 |
| user_id | UUID FK | 所属用户 |
| question_text | TEXT | 题目文本 |
| question_image_url | VARCHAR(500) | 题目图片 URL |
| material_text | TEXT | 给定材料文本 |
| standard_answers | JSONB | 多个标准答案数组 |
| question_type | VARCHAR(20) | 题型（归纳概括/综合分析/提出对策/贯彻执行/大作文） |
| created_at | TIMESTAMP | 创建时间 |

#### essay_answers - 申论答案与匹配结果

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录唯一标识 |
| user_id | UUID FK | 所属用户 |
| essay_question_id | UUID FK | 关联申论题目 |
| user_answer_text | TEXT | 用户答案 |
| matched_points | JSONB | 匹配结果数组：{point_id, point_text, match_score, color_code, matched_standard_idx} |
| coverage_rate | FLOAT | 要点覆盖率（0-100%） |
| overall_score | FLOAT | 总评分 |
| ai_comment | TEXT | AI 评语 |
| created_at | TIMESTAMP | 创建时间 |

#### essay_materials - 申论素材

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 素材唯一标识 |
| user_id | UUID FK | 所属用户 |
| title | VARCHAR(200) | 素材标题 |
| content | TEXT | 素材内容 |
| tags | JSONB | 标签数组 |
| topics | JSONB | 适用话题数组 |
| embedding | VECTOR(1536) | pgvector 语义向量 |
| source | VARCHAR(200) | 来源 |
| file_url | VARCHAR(500) | 原始文件 URL |
| created_at | TIMESTAMP | 创建时间 |

#### essays - 申论大作文

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 作文唯一标识 |
| user_id | UUID FK | 所属用户 |
| title | VARCHAR(200) | 作文标题 |
| content | TEXT | 作文内容 |
| topic | VARCHAR(100) | 作文话题 |
| ai_score | JSONB | AI 评分：{structure, argument, language, total} |
| ai_rewrite_suggestion | TEXT | AI 改写建议 |
| ai_rewrite_content | TEXT | AI 改写后的完整作文 |
| used_template_id | UUID FK | 使用的模板 |
| created_at | TIMESTAMP | 创建时间 |

#### essay_templates - 作文模板

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 模板唯一标识 |
| user_id | UUID FK | 所属用户 |
| name | VARCHAR(100) | 模板名称 |
| essay_type | VARCHAR(20) | 作文类型（政论文/策论文/评论文） |
| structure | JSONB | 结构模板（开头/分论点/结尾） |
| example_opening | TEXT | 开头示例 |
| example_closing | TEXT | 结尾示例 |
| applicable_topics | JSONB | 适用话题数组 |
| usage_count | INTEGER | 使用次数 |
| avg_score | FLOAT | 平均得分 |

#### daily_progress - 每日进度

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 记录唯一标识 |
| user_id | UUID FK | 所属用户 |
| date | DATE | 日期 |
| aptitude_questions_count | INTEGER | 行测做题数 |
| aptitude_correct_count | INTEGER | 行测正确数 |
| essay_practice_count | INTEGER | 申论练习数 |
| essay_avg_score | FLOAT | 申论平均得分 |
| study_minutes | INTEGER | 学习时长（分钟） |
| notes | TEXT | 用户备注 |

#### wiki_pages - Karpathy Wiki 页面

| 字段 | 类型 | 说明 |
|------|------|------|
| id | UUID PK | 页面唯一标识 |
| user_id | UUID FK | 所属用户 |
| title | VARCHAR(200) | 页面标题 |
| slug | VARCHAR(200) | URL 友好标识 |
| content | TEXT | Markdown 内容 |
| page_type | VARCHAR(20) | 页面类型（index/entity/summary/log） |
| category | VARCHAR(20) | 分类（行测/申论/全局） |
| source_refs | JSONB | 来源引用数组 |
| last_linted_at | TIMESTAMP | 上次 Lint 时间 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

---

## 5. 行测模块详细设计

### 5.1 错题录入与解析

**用户交互流程**：

1. 用户上传题目（支持图片、文本、PDF）
2. 若为图片/PDF：触发 Celery OCR 任务（PaddleOCR 或商业 API）提取文本
3. 用户校正 OCR 结果（必要时）
4. 用户输入自己的答案
5. 系统判定对错，若答错进入错题解析流程

**AI 解析流程（触发 Karpathy Wiki Ingest）**：

```
错题录入
    ↓
LLM 分析错因（"用户选 B 是因为混淆了加强和假设的区别"）
    ↓
提取知识点标签（自动推荐 + 用户确认）
    ↓
更新数据库：knowledge_nodes + knowledge_edges
    ↓
更新 Wiki 页面：
    - 知识点实体页（如"逻辑判断-加强削弱"）
    - 错题摘要页（记录错因、关联题目 ID）
    - log.md（追加审计记录：时间、操作、变更摘要）
```

### 5.2 知识点自动分类与知识图谱

**分类体系**（2026 年国考 6 模块）：

| 一级分类 | 二级分类示例 |
|---------|------------|
| 政治理论 | 时政热点、党史党建、马克思主义基本原理 |
| 常识判断 | 法律、科技、人文、地理、经济 |
| 言语理解 | 逻辑填空、片段阅读、语句表达 |
| 数量关系 | 行程问题、工程问题、排列组合、概率 |
| 判断推理 | 图形推理、定义判断、类比推理、逻辑判断 |
| 资料分析 | 增长率、比重、平均数、综合分析 |

**Graphify 集成**：

```
题目文本 + 解析文本 + 知识点标签 + 错题标记
        ↓
    Graphify 构建行测知识图谱
        ↓
    输出 graph.json（结构化数据）
    输出 graph.html（交互式可视化页面）
        ↓
    前端 ECharts 渲染或嵌入 graph.html
```

**图谱可视化设计**：

- **知识点节点**：圆形，颜色按模块区分
  - 政治理论 = 棕色
  - 常识判断 = 紫色
  - 言语理解 = 蓝色
  - 数量关系 = 红色
  - 判断推理 = 绿色
  - 资料分析 = 橙色
  - 节点大小 = 关联错题数（错题越多节点越大）
- **题目节点**：灰色小节点，悬停显示题目摘要
- **边类型**：
  - `belongs_to`：题目 -> 知识点（实线）
  - `prerequisite`：知识点 -> 知识点（前置依赖，虚线）
  - `similar_to`：题目 -> 题目（LLM 推断相似题，点线）
  - `mistake_on`：用户 -> 知识点（错题关联，红色粗线，带权重）
- **God 节点**：最高错题频次知识点自动标记红色高亮 + 脉冲动画
- **Unexpected Connections**：跨模块关联边用金色高亮（如"类比推理"与"成语辨析"的隐藏关联）

### 5.3 80 分目标拆解与正确率预测

**默认配置模板**（国考副省级）：

| 模块 | 题量 | 单题分值 | 目标正确率 | 预期得分 |
|------|------|---------|-----------|---------|
| 政治理论 | 20 | 0.8 | 75% | 12.0 |
| 常识判断 | ~10 | 0.6 | 70% | 4.2 |
| 言语理解 | 30 | 0.8 | 85% | 20.4 |
| 数量关系 | ~10 | 0.6 | 60% | 3.6 |
| 判断推理 | 35 | 0.8 | 85% | 23.8 |
| 资料分析 | 20 | 1.0 | 90% | 18.0 |
| **合计** | **125** | — | — | **82.0** |

> 注：系统支持用户自定义各模块题量、分值和目标正确率，适配不同考试类型。

**动态调整算法**：

1. 取用户最近 50 次答题记录
2. 计算各模块实际正确率
3. 线性规划求解：在时间约束下，调整各模块目标正确率使总分 >= 80
4. 输出：各模块建议目标正确率 + 建议投入时间分配 + 薄弱模块优先提醒

### 5.4 原始题目与答案记录

- 每道题目独立存储，支持图片 + 文本混合
- 答题记录每次独立存储，支持同一题多次作答的历史追踪
- 支持题目导出（Markdown/PDF 格式，方便打印复习）
- 支持题目批量导入（Excel/CSV 模板）

### 5.5 每日进度自动记录

**自动记录内容**：

- 今日做题数量、正确率、总用时
- 各模块错题分布（饼图）
- 新掌握的知识点数量（首次答对某知识点的题目数）
- 学习时长（基于页面活跃时间统计）

**可视化面板**：

- 日历热力图（类似 GitHub 贡献图，颜色深浅表示学习时长）
- 周/月趋势折线图（做题量、正确率双轴）
- 各模块雷达图（当前水平 vs 目标水平，6 个维度）
- 错题数量趋势图（追踪薄弱点改善情况）

### 5.6 Karpathy Wiki 在行测中的应用

- **错题知识点页**：每个薄弱知识点有独立 Wiki 页，汇总所有相关错题、解析、关联知识点
- **模块总览页**：每个行测模块一页，列出所有知识点和掌握状态
- **学习日志页**：按日期组织的自动学习记录（类似 Karpathy 的 log.md）
- **Index 页**：行测知识总目录，按模块和知识点层级组织
- **Lint 检查**：自动发现"同一知识点多次犯错但解析矛盾"的情况，生成报告提醒用户

---

## 6. 申论模块详细设计

### 6.1 申论答案匹配与彩色标记

**用户交互流程**：

1. 上传申论题目（材料 + 问题，支持文本/图片/PDF）
2. 上传自己的答案（文本/图片）
3. 上传多个标准答案（至少 1 个，支持多个对比）
4. 系统通过 LLM 进行要点匹配分析

**AI 匹配算法**：

```
用户答案 + 标准答案 1 + 标准答案 2 + ...
        ↓
    LLM 逐点对比分析（Prompt 工程）：
    1. 将标准答案拆解为关键要点列表
    2. 将用户答案按段落/语义拆分为用户要点
    3. 逐一匹配：计算语义相似度
    4. 标记匹配结果
        ↓
    输出结构化匹配结果：
    {
      "user_points": [
        {
          "text": "用户答案第 1 段",
          "match_type": "full_hit",     // full_hit / partial_hit / miss / extra
          "match_score": 92,            // 0-100
          "color_code": "#4CAF50",      // 绿色
          "matched_standard": "标准答案要点 3",
          "comment": "准确命中了'加强基层治理'要点"
        }
      ],
      "coverage_rate": 78.5,            // 要点覆盖率
      "missing_points": ["要点 2：未提及执行主体", "要点 5：缺少具体措施"],
      "overall_score": 82
    }
```

**颜色标记方案**：

| 匹配类型 | 匹配度 | 颜色 | 说明 |
|---------|--------|------|------|
| 完全命中 | >= 80% | 绿色 `#4CAF50` | 用户答到了且表述准确 |
| 部分命中 | 50%-80% | 黄色 `#FFC107` | 答到了但表述不够完整/准确 |
| 遗漏/偏离 | < 50% | 红色 `#F44336` | 该答的没答到或答偏了 |
| 额外发挥 | N/A | 蓝色 `#2196F3` | 用户写了但标准答案中没有（可能加分也可能跑题）|

**前端展示**：

- 左右分栏布局（宽屏）/ 上下分栏（移动端）
- 左侧：用户答案，按段落渲染，每段带彩色背景
- 右侧：标准答案切换器（Tab 切换多个标准答案），显示要点列表
- 悬停交互：鼠标悬停用户答案的彩色段落，浮窗显示匹配到的标准答案要点、匹配度、AI 评语
- 总评面板：覆盖率环形图 + 遗漏要点列表 + 改进建议

**Karpathy Wiki 集成**：

- 每次匹配结果自动 Ingest 到 Wiki：
  - 创建/更新"申论答题技巧"实体页
  - 记录该题型的常见遗漏要点（如"对策题经常忘记写执行主体"）
  - log.md 追加答题记录（时间、题型、覆盖率、得分）

### 6.2 申论素材知识图谱

**素材录入流程**：

```
上传素材（文本/PDF/图片）
    ↓
OCR 提取文本（如需要）
    ↓
LLM 分析：提取主题、关键词、适用话题
    ↓
存入 essay_materials 表（含 embedding 向量）
    ↓
触发 Graphify 增量构建
    ↓
更新申论素材图谱
```

**Graphify 集成**：

```
素材文本 + 主题标签 + 适用话题 + 关键词
        ↓
    Graphify 构建申论素材图谱
        ↓
    素材节点 + 话题节点 + 关键词节点 + 关联边
        ↓
    输出 graph.json + graph.html
```

**图谱设计**：

- **素材节点**：矩形，按领域分类着色
  - 经济 = 金色
  - 生态 = 绿色
  - 文化 = 紫色
  - 社会 = 橙色
  - 政治 = 红色
  - 科技 = 蓝色
- **话题节点**：圆形，申论常见话题（乡村振兴、数字经济、基层治理、生态文明等）
- **关键词节点**：小菱形，素材中的高频关键词
- **边类型**：
  - `applies_to`：素材 -> 话题（适用话题，实线）
  - `contains`：素材 -> 关键词（包含关系）
  - `related`：话题 -> 话题（相关话题关联）
  - `semantically_similar`：素材 -> 素材（语义相似，Graphify 自动推断，虚线）
- **God 节点**：被最多话题引用的"万能素材"自动放大高亮

**素材检索功能**：

- 按话题筛选：点击话题节点，显示所有关联素材
- 语义搜索：输入自然语言查询，通过 pgvector embedding 相似度返回相关素材
- 推荐：写作文时，根据作文话题自动推荐相关素材

### 6.3 申论大作文模板管理

**模板录入**：

- 用户上传或手动创建作文模板
- 模板结构分解：
  - 开头模板（引入话题 + 提出观点）
  - 分论点模板（3-4 个分论点的论证结构）
  - 结尾模板（总结升华）
- 元数据：适用话题、作文类型（政论文/策论文/评论文）、来源

**模板 Wiki 页**：

- 每个模板有独立 Wiki 页面
- 记录模板的来源、使用次数、平均得分
- 关联到适用的素材和话题
- 支持版本历史（修改记录）

### 6.4 作文打分与 AI 改写

**AI 打分维度**：

| 维度 | 权重 | 评分标准 | 分数范围 |
|------|------|---------|---------|
| 立意/观点 | 25% | 是否切题、观点是否深刻、是否有独到见解 | 0-100 |
| 结构/逻辑 | 25% | 开头-分论点-结尾完整性、段落衔接、逻辑递进 | 0-100 |
| 论证/素材 | 25% | 论据是否充分、素材运用是否恰当、案例是否贴切 | 0-100 |
| 语言/表达 | 25% | 语言流畅度、用词准确性、句式多样性 | 0-100 |
| **总分** | **100%** | 加权平均，换算为申论大作文实际分值（35-40 分制） | — |

**打分流程**：

```
用户作文 + 作文题目
        ↓
    LLM 四维评分（Chain-of-Thought）
        ↓
    输出评分结果 + 各维度评语
        ↓
    前端展示雷达图（4 维度）
```

**AI 改写流程**：

```
用户作文 + 打分结果 + 系统模板库 + 系统素材库
        ↓
    LLM 分析薄弱环节：
    1. 结构优化建议（基于模板对比）
    2. 素材替换建议（从素材图谱推荐更贴切素材）
    3. 语言润色（保持原意，提升表达）
        ↓
    生成改写版本（用户可选一键生成）
        ↓
    原文 vs 改写文对比视图
```

**改写输出格式**：

- 对比视图（类似 Git diff）：绿色 = 新增/优化，红色 = 删除/修改
- 每处修改标注原因（如"此处素材替换为'数字经济'相关案例，更贴合题目"）
- 改写版本可以一键保存为新作文记录，原作文保留

**Karpathy Wiki 集成**：

- 每次作文打分后，更新"个人作文成长"Wiki 页
- 记录常用薄弱点（如"分论点之间缺乏递进关系"）
- 推荐针对性模板和素材（基于 Wiki 的 Query 流程）

### 6.5 申论进度记录

- 与行测进度合并展示，按日期统计
- 申论特有指标：
  - 素材积累数量（本周/本月新增）
  - 作文练习次数和平均得分趋势
  - 各题型（归纳概括/综合分析/提出对策/贯彻执行/大作文）得分雷达图
  - 要点覆盖率趋势（追踪答题能力提升）

---

## 7. 全局集成设计

### 7.1 AI 对话面板（页面内随时与我通话）

**实现方式**：

- 页面右下角悬浮**聊天按钮**（圆形，直径 56px，带消息未读角标）
- 点击展开**侧边聊天面板**（宽度 400px，占满右侧屏幕高度，移动端全屏）
- 支持**SSE 流式输出**，AI 回复逐字显示，带打字机效果
- 支持 Markdown 渲染（代码块、列表、表格）

**对话上下文设计**：

- 系统消息中注入当前页面上下文：
  ```json
  {
    "current_page": "aptitude_mistake_detail",
    "question_id": "uuid",
    "knowledge_node": "逻辑判断-加强削弱",
    "user_performance": "近10题正确率60%"
  }
  ```
- AI 可以读取当前页面的相关数据（错题内容、知识图谱节点、作文内容）
- 用户可以直接提问："这道题为什么选 C？""帮我分析一下这个知识点的薄弱情况""推荐一些乡村振兴的素材"

**与 Karpathy Wiki 的联动**：

- 用户在聊天中提出的问题和 AI 的回答，可以一键 **Ingest 到 Wiki**
- 聊天面板中支持 `/wiki` 命令直接查询 Wiki 内容
- 支持 `/graph` 命令查询知识图谱（"显示我的薄弱知识点"）

### 7.2 Graphify 全局工作流

```
用户上传任何材料（题目/素材/作文）
            ↓
    如果是图片/PDF → OCR 提取文本
            ↓
    存入 PostgreSQL（原始数据）+ 文件存储（原始文件）
            ↓
    触发 Celery 异步任务
            ↓
    Graphify 增量构建图谱：
    - 计算文件 SHA256
    - 仅处理新增/变更的文件
    - 使用 tree-sitter（代码类）或 LLM 子代理（文档类）提取实体和关系
    - Leiden 社区检测聚类
            ↓
    更新 graph.json + graph.html
            ↓
    前端知识图谱自动刷新
```

**增量更新策略**：

- 利用 Graphify 的 SHA256 缓存机制
- `--watch` 模式：后台 Celery Beat 定时任务监控数据变更，自动触发重建
- 全量重建：用户手动触发（首次使用或数据量大时）

**双图谱模式**：

| 图谱 | 数据来源 | 节点类型 | 主要边类型 |
|------|---------|---------|-----------|
| 行测知识图谱 | 行测题目 + 解析 + 知识点标签 | 知识点、题目 | belongs_to, prerequisite, similar_to, mistake_on |
| 申论素材图谱 | 申论素材 + 话题 + 关键词 | 素材、话题、关键词 | applies_to, contains, related, semantically_similar |

### 7.3 Karpathy Wiki 全局工作流

```
Schema 文档 (SCHEMA.md)
    ↓ 定义知识分类规范、页面格式、命名约定

Raw Sources (原始数据)
    ├── 行测错题记录（数据库）
    ├── 申论答题记录（数据库）
    ├── 素材文本（数据库）
    └── 聊天对话记录（内存/临时存储）

    ↓ LLM Ingest（触发时机：新增错题/答题/素材时）

Wiki Pages (Markdown 文件)
    ├── index.md (总目录：按模块和知识点层级组织的链接索引)
    ├── log.md (操作日志：按时间顺序的追加记录，只增不改)
    ├── SCHEMA.md (规范文档：定义分类约定和页面格式)
    ├── 行测/
    │   ├── 模块总览-政治理论.md
    │   ├── 模块总览-常识判断.md
    │   ├── 模块总览-言语理解.md
    │   ├── 模块总览-数量关系.md
    │   ├── 模块总览-判断推理.md
    │   ├── 模块总览-资料分析.md
    │   ├── 知识点-逻辑判断-加强削弱.md
    │   ├── 知识点-言语理解-主旨概括.md
    │   ├── 错题摘要-2026-04.md
    │   └── ...
    ├── 申论/
    │   ├── 素材目录.md
    │   ├── 话题-乡村振兴.md
    │   ├── 话题-数字经济.md
    │   ├── 作文成长记录.md
    │   ├── 答题技巧-归纳概括.md
    │   ├── 答题技巧-对策建议.md
    │   └── ...
    └── 聊天/
        └── 问答归档.md

    ↓ LLM Query（用户查询时）

用户查询 → LLM 搜索相关 Wiki 页面 → 合成回答（非直接查原始数据）
→ 好的回答可以一键 Ingest 回 Wiki

    ↓ 每周 Lint（Celery Beat 定时任务）

自动检查：
- 矛盾：同一知识点在不同页面的描述冲突
- 孤立页：没有入链的 Wiki 页面
- 过时内容：长时间未更新的知识点页
→ 生成 Lint 报告，提醒用户处理
```

**Obsidian 兼容**：

- Wiki 页面以标准 Markdown 格式存储
- 使用 Wiki 链接语法 `[[页面标题]]`
- 支持导出压缩包，用户可导入 Obsidian 本地浏览
- 文件名使用 slug 格式（中文标题转拼音或保留中文）

---

## 8. 部署方案

### 8.1 服务器要求

- **初期**：单台云服务器，2 核 4G 起步，50GB 存储
- **扩展**：当用户数 > 100 或数据量 > 10GB 时，升级至 4 核 8G，分离数据库到 RDS

### 8.2 Docker Compose 编排

```yaml
# docker-compose.yml
services:
  web:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./frontend/dist:/usr/share/nginx/html
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

  api:
    build: ./backend
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/gongkao
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    depends_on:
      - db
      - redis
      - minio

  worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/gongkao
      - REDIS_URL=redis://redis:6379
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
    depends_on:
      - db
      - redis

  scheduler:
    build: ./backend
    command: celery -A tasks beat --loglevel=info
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/gongkao
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis

  db:
    image: ankane/pgvector:latest
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=gongkao

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data

  minio:
    image: minio/minio
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
    environment:
      - MINIO_ROOT_USER=minio
      - MINIO_ROOT_PASSWORD=minio123

volumes:
  postgres_data:
  redis_data:
  minio_data:
```

### 8.3 目录结构

```
gongkao-brain/
├── frontend/                  # Vue3 前端
│   ├── src/
│   │   ├── views/             # 页面组件
│   │   │   ├── aptitude/      # 行测模块
│   │   │   ├── essay/         # 申论模块
│   │   │   ├── graph/         # 知识图谱
│   │   │   ├── progress/      # 进度面板
│   │   │   └── wiki/          # Wiki 浏览
│   │   ├── components/        # 公共组件
│   │   │   ├── ChatPanel.vue  # AI 聊天面板
│   │   │   ├── GraphViewer.vue # 知识图谱可视化
│   │   │   └── AnswerMatcher.vue # 答案匹配标记
│   │   ├── stores/            # Pinia 状态管理
│   │   └── api/               # API 接口封装
│   ├── package.json
│   └── vite.config.ts
├── backend/                   # FastAPI 后端
│   ├── app/
│   │   ├── routers/           # API 路由
│   │   │   ├── auth.py        # 认证
│   │   │   ├── aptitude.py    # 行测
│   │   │   ├── essay.py       # 申论
│   │   │   ├── graph.py       # 知识图谱
│   │   │   ├── wiki.py        # Wiki 管理
│   │   │   └── chat.py        # AI 对话
│   │   ├── models/            # SQLAlchemy 模型
│   │   ├── services/          # 业务逻辑
│   │   │   ├── ocr.py         # OCR 服务
│   │   │   ├── graphify_service.py  # Graphify 集成
│   │   │   ├── wiki_service.py      # Wiki Ingest/Query/Lint
│   │   │   └── ai_service.py        # Claude API 封装
│   │   ├── tasks.py           # Celery 异步任务
│   │   └── main.py            # FastAPI 入口
│   ├── Dockerfile
│   ├── requirements.txt
│   └── alembic/               # 数据库迁移
├── wiki/                      # Karpathy Wiki 目录 (Markdown)
│   ├── SCHEMA.md
│   ├── index.md
│   ├── log.md
│   ├── 行测/
│   └── 申论/
├── graphify/                  # Graphify 配置和输出
│   ├── config.yaml
│   ├── cache/                 # SHA256 缓存
│   ├── output/
│   │   ├── aptitude_graph.json
│   │   ├── aptitude_graph.html
│   │   ├── essay_graph.json
│   │   └── essay_graph.html
│   └── hooks/                 # Git hooks / 自动触发脚本
├── docker-compose.yml
├── .env.example               # 环境变量模板
└── README.md
```

### 8.4 环境变量

```bash
# 数据库
DATABASE_URL=postgresql://user:pass@db:5432/gongkao

# Redis
REDIS_URL=redis://redis:6379

# AI API
CLAUDE_API_KEY=sk-...
CLAUDE_MODEL=claude-sonnet-4-6

# 文件存储
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minio
MINIO_SECRET_KEY=minio123
MINIO_BUCKET=gongkao

# OCR（可选，留空使用 PaddleOCR 本地）
OCR_API_KEY=...

# Graphify
GRAPHIFY_CONFIG_PATH=./graphify/config.yaml
```

---

## 9. 项目边界与优先级

### 9.1 MVP 优先级

**P0（核心功能，第一期必须完成）**：

1. 用户注册/登录/认证系统
2. 行测错题录入（文本 + 图片 OCR）
3. 行测基础知识分类和错题标记
4. 行测知识图谱可视化（ECharts，基础节点和边）
5. AI 聊天面板（SSE 流式对话，基础上下文）

**P1（重要功能，第二期完成）**：

6. 申论答案上传和 AI 匹配分析
7. 申论答案彩色标记展示
8. 80 分目标拆解与动态调整
9. 每日进度自动记录和可视化
10. Graphify 集成（行测知识图谱自动构建）

**P2（增强功能，第三期完成）**：

11. 申论素材上传和知识图谱
12. 申论素材语义搜索和推荐
13. 作文模板管理
14. 作文 AI 打分
15. 作文 AI 改写（基于模板和素材）

**P3（高级功能，后续迭代）**：

16. Karpathy Wiki 完整 Ingest/Query/Lint 流程
17. Wiki 页面导出到 Obsidian
18. Graphify --watch 自动同步
19. 移动端适配优化
20. 多用户/社交功能（如家庭共享，非必须）

### 9.2 明确不做（范围控制）

- **不做在线刷题题库**：系统只管理用户自己上传的错题和练习，不内置题库
- **不做社交/排行榜**：纯个人学习工具，无社交功能
- **不做视频课程管理**：不管理课程视频，只管理文本/图片学习材料
- **不做实时协作**：单用户系统，暂不支持多人同时编辑
- **不做语音通话**：AI 对话仅限文字，不做语音交互

---

## 10. 风险与应对

| 风险 | 影响 | 应对策略 |
|------|------|---------|
| Graphify 增量构建性能不足 | 大数据量时构建时间过长 | 利用 SHA256 缓存 + 异步任务 + 手动全量重建 |
| OCR 准确率不足 | 题目解析错误 | 用户校正流程 + 支持多 OCR 引擎切换 |
| LLM API 费用过高 | 运营成本增加 | 本地缓存频繁查询结果 + 控制对话上下文长度 |
| Karpathy Wiki 自动 Ingest 质量不稳定 | Wiki 页面质量差 | 人工审核机制 + Lint 检查 + 一键回滚 |
| 知识图谱可视化性能（节点过多） | 前端卡顿 | 分页加载 + 社区聚类折叠 + 仅展示高权重节点 |

---

## 11. 附录

### 11.1 行测模块颜色方案

| 模块 | 主色 | 十六进制 |
|------|------|---------|
| 政治理论 | 棕色 | `#8B4513` |
| 常识判断 | 紫色 | `#9C27B0` |
| 言语理解 | 蓝色 | `#2196F3` |
| 数量关系 | 红色 | `#F44336` |
| 判断推理 | 绿色 | `#4CAF50` |
| 资料分析 | 橙色 | `#FF9800` |

### 11.2 申论答案匹配颜色方案

| 匹配类型 | 颜色 | 十六进制 |
|---------|------|---------|
| 完全命中 | 绿色 | `#4CAF50` |
| 部分命中 | 黄色 | `#FFC107` |
| 遗漏/偏离 | 红色 | `#F44336` |
| 额外发挥 | 蓝色 | `#2196F3` |

### 11.3 参考资料

- Graphify: https://github.com/safishamsi/graphify
- Karpathy Wiki Gist: https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f
