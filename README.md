# astrbot-plugin-whiteList-group

AstrBot 群聊白名单插件

## 功能说明

这是一个为 AstrBot 设计的群聊白名单插件。当启用此插件时：

- **群聊中**：机器人只会回复白名单中的用户，其他用户的消息将被忽略
- **私聊中**：机器人正常回复所有消息（不受白名单限制）

## 安装方式

1. 将插件文件放入 AstrBot 的 `plugins` 目录
2. 重启 AstrBot 或重新加载插件

## 使用方式

### 命令列表

| 命令 | 说明 | 用法 |
|------|------|------|
| `/whitelist_add` | 添加用户到白名单 | `/whitelist_add <用户ID>` |
| `/whitelist_remove` | 从白名单移除用户 | `/whitelist_remove <用户ID>` |
| `/whitelist_list` | 查看当前白名单 | `/whitelist_list` |

### 使用示例

```
# 添加用户到白名单
/whitelist_add user123

# 移除用户
/whitelist_remove user123

# 查看白名单
/whitelist_list
```

## 配置文件

配置文件位置：`whitelist_config.json`

初始配置示例：
```json
{
  "whitelist": [
    "user_id_1",
    "user_id_2",
    "user_id_3"
  ]
}
```

### 获取用户ID

根据不同的 IM 平台，用户ID获取方式可能不同：

- **QQ**：通常是数字账号
- **Telegram**：数字 ID
- **其他平台**：参考 AstrBot 官方文档

## 工作原理

1. 插件启动时，自动加载 `whitelist_config.json` 中的白名单配置
2. 当有消息到达时，插件会进行预处理检查：
   - 如果是私聊消息，直接通过
   - 如果是群聊消息，检查发送者是否在白名单中
   - 如果在白名单中，允许机器人响应
   - 如果不在白名单中，消息被过滤，机器人不会响应

## 注意事项

- 白名单配置会自动保存到 JSON 文件中
- 如果白名单为空，所有群聊消息都会被处理
- 命令本身需要在白名单中的用户才能执行
- 建议只让信任的管理员执行白名单管理命令
 - 插件会在控制台输出关键操作日志（初始化、加载/保存白名单、添加/移除用户、查看白名单、卸载等），便于调试

## 开发者

- kori2

## 许可证

MIT

## 参考资源

- [AstrBot 官方文档](https://docs.astrbot.app/)
- [AstrBot 插件开发指南](https://docs.astrbot.app/dev/star/plugin-new.html)
