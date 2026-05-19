import json
from pathlib import Path
from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("astrbot_plugin_whiteList_gruop", "kori2", "群聊白名单插件 - 在群聊里只和白名单中的人说话", "1.3.0")
class WhiteListPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.whitelist = set()
        self.config_file = Path(context.plugin_dir) / "whitelist_config.json"

    async def initialize(self):
        """插件初始化，加载白名单配置"""
        self._load_whitelist()
        logger.info(f"白名单插件已初始化，当前白名单: {self.whitelist}")

    def _load_whitelist(self):
        """从配置文件加载白名单"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.whitelist = set(data.get('whitelist', []))
            except Exception as e:
                logger.error(f"加载白名单配置失败: {e}")
                self.whitelist = set()
        else:
            # 创建默认配置文件
            self._save_whitelist()

    def _save_whitelist(self):
        """保存白名单到配置文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'whitelist': list(self.whitelist)}, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存白名单配置失败: {e}")

    @filter.command("whitelist_add")
    async def whitelist_add(self, event: AstrMessageEvent):
        """添加用户到白名单"""
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("用法: /whitelist_add <用户ID>")
            return
        
        user_id = parts[1]
        self.whitelist.add(user_id)
        self._save_whitelist()
        yield event.plain_result(f"✓ 已将用户 {user_id} 添加到白名单")

    @filter.command("whitelist_remove")
    async def whitelist_remove(self, event: AstrMessageEvent):
        """从白名单移除用户"""
        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("用法: /whitelist_remove <用户ID>")
            return
        
        user_id = parts[1]
        self.whitelist.discard(user_id)
        self._save_whitelist()
        yield event.plain_result(f"✓ 已将用户 {user_id} 从白名单移除")

    @filter.command("whitelist_list")
    async def whitelist_list(self, event: AstrMessageEvent):
        """查看当前白名单"""
        if not self.whitelist:
            yield event.plain_result("白名单为空")
        else:
            whitelist_str = "\n".join(self.whitelist)
            yield event.plain_result(f"当前白名单:\n{whitelist_str}")

    @filter.message_preprocessor()
    async def message_check(self, event: AstrMessageEvent):
        """消息预处理：检查白名单"""
        # 如果是私聊，直接通过
        if not event.is_group_chat():
            return
        
        # 如果白名单为空，允许所有消息通过
        if not self.whitelist:
            return
        
        # 获取发送者ID
        sender_id = event.get_sender_id()
        
        # 如果发送者在白名单中，允许通过
        if sender_id in self.whitelist:
            return
        
        # 如果发送者不在白名单中，阻止消息
        logger.debug(f"用户 {sender_id} 不在白名单中，消息已被过滤")
        event.stop_propagation()

    async def terminate(self):
        """插件销毁"""
        logger.info("白名单插件已卸载")
