# Project State

## 已完成
- 阶段1：项目骨架 + Provider CRUD（SQLite，明文存储）
- 阶段2：api_key Fernet 加密存储

## 数据库
表：providers
字段：id, name, website, signup_url, api_docs, api_key(加密), enabled, created_at

## 未完成
- 阶段3：Provider Adapter + Smart Router
- 阶段4：Failover + FastAPI 完整接口
- 阶段5：Provider Discovery + Registration Assistant
- 阶段6：Web UI + CC-Switch
