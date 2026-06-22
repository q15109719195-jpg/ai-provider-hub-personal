# Project State

## 已完成
- 阶段1：项目骨架 + Provider CRUD
- 阶段2：api_key Fernet 加密存储
- 阶段3：Provider Adapter（OpenAI兼容 + Anthropic）+ Smart Router
- 阶段4：Failover 自动切换 + CC-Switch 接口

## 数据库
表：providers
字段：id, name, website, signup_url, api_docs, api_key(加密), enabled, created_at

## API 接口
GET /                服务状态
GET /router          路由规则
GET /api/providers   Provider 列表
POST /api/providers           新增 Provider
GET /api/providers/{id}       查询 Provider
PUT /api/providers/{id}       修改 Provider
DELETE /api/providers/{id}    删除 Provider
POST /api/chat                发送对话（含 Failover）
GET /api/cc-switch/providers  CC-Switch Provider 列表
GET /api/cc-switch/router      CC-Switch 路由配置

## 未完成
- 阶段5：Provider Discovery + Registration Assistant
- 阶段6：Streamlit Web UI + CC-Switch 完整集成
