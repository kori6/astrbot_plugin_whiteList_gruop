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
        plugin_dir = getattr(context, "plugin_dir", None)
        if plugin_dir:
            self.config_file = Path(plugin_dir) / "whitelist_config.json"
        else:
            self.config_file = Path(__file__).resolve().parent / "whitelist_config.json"

    async def initialize(self):
        """插件初始化，加载白名单配置"""
        self._load_whitelist()
        logger.info(f"白名单插件已初始化，当前白名单: {self.whitelist}")
        print(f"[WhiteListPlugin] 已初始化，当前白名单: {self.whitelist}")

    def _load_whitelist(self):
        """从配置文件加载白名单"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.whitelist = set(data.get('whitelist', []))
                    logger.info(f"已从配置文件加载白名单: {self.config_file}")
                    print(f"[WhiteListPlugin] 从{self.config_file}加载白名单: {self.whitelist}")
            except Exception as e:
                logger.error(f"加载白名单配置失败: {e}")
                print(f"[WhiteListPlugin] 加载白名单失败: {e}")
                self.whitelist = set()
        else:
            # 创建默认配置文件
            logger.info(f"白名单配置文件不存在，创建默认配置: {self.config_file}")
            print(f"[WhiteListPlugin] 配置文件不存在，创建默认配置: {self.config_file}")
            self._save_whitelist()

    def _save_whitelist(self):
        """保存白名单到配置文件"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump({'whitelist': list(self.whitelist)}, f, ensure_ascii=False, indent=2)
            logger.info(f"白名单已保存到: {self.config_file}")
            print(f"[WhiteListPlugin] 白名单已保存到 {self.config_file}，内容: {self.whitelist}")
        except Exception as e:
            logger.error(f"保存白名单配置失败: {e}")
            print(f"[WhiteListPlugin] 保存白名单失败: {e}")

    def _is_group_command_sender_whitelisted(self, event: AstrMessageEvent) -> bool:
        """仅允许群聊中的白名单用户执行命令，私聊正常处理。"""
        if getattr(event, "is_group_chat", None) is not None:
            if not event.is_group_chat():
                logger.debug("命令来自私聊，允许执行")
                print("[WhiteListPlugin] 命令来自私聊，允许执行")
                return True

        # 兼容没有 is_group_chat() 的事件类型，比如 AiocqhttpMessageEvent
        group_id = getattr(event, "group_id", None)
        if not group_id:
            group_id = getattr(getattr(event, "message_obj", None), "group_id", None)
        if not group_id:
            return True

        sender_id = event.get_sender_id()
        in_whitelist = sender_id in self.whitelist
        logger.debug(f"检查用户 {sender_id} 是否在白名单: {in_whitelist}")
        print(f"[WhiteListPlugin] 检查用户 {sender_id} 是否在白名单: {in_whitelist}")
        return in_whitelist

    @filter.command("whitelist_add")
    async def whitelist_add(self, event: AstrMessageEvent):
        """添加用户到白名单"""
        if not self._is_group_command_sender_whitelisted(event):
            yield event.plain_result("你不在白名单中，无法使用此命令")
            return

        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("用法: /whitelist_add <用户ID>")
            return
        
        user_id = parts[1]
        sender = event.get_sender_id()
        logger.info(f"用户 {sender} 请求添加 {user_id} 到白名单")
        print(f"[WhiteListPlugin] 用户 {sender} 请求添加 {user_id} 到白名单")
        self.whitelist.add(user_id)
        self._save_whitelist()
        logger.info(f"已添加用户 {user_id} 到白名单")
        print(f"[WhiteListPlugin] 已添加用户 {user_id} 到白名单，当前白名单: {self.whitelist}")
        yield event.plain_result(f"✓ 已将用户 {user_id} 添加到白名单")

    @filter.command("whitelist_remove")
    async def whitelist_remove(self, event: AstrMessageEvent):
        """从白名单移除用户"""
        if not self._is_group_command_sender_whitelisted(event):
            yield event.plain_result("你不在白名单中，无法使用此命令")
            return

        parts = event.message_str.strip().split()
        if len(parts) < 2:
            yield event.plain_result("用法: /whitelist_remove <用户ID>")
            return
        
        user_id = parts[1]
        sender = event.get_sender_id()
        logger.info(f"用户 {sender} 请求从白名单移除 {user_id}")
        print(f"[WhiteListPlugin] 用户 {sender} 请求从白名单移除 {user_id}")
        self.whitelist.discard(user_id)
        self._save_whitelist()
        logger.info(f"已将用户 {user_id} 从白名单移除")
        print(f"[WhiteListPlugin] 已移除用户 {user_id}，当前白名单: {self.whitelist}")
        yield event.plain_result(f"✓ 已将用户 {user_id} 从白名单移除")

    @filter.command("whitelist_list")
    async def whitelist_list(self, event: AstrMessageEvent):
        """查看当前白名单"""
        if not self._is_group_command_sender_whitelisted(event):
            yield event.plain_result("你不在白名单中，无法使用此命令")
            return

        sender = event.get_sender_id()
        logger.info(f"用户 {sender} 请求查看白名单")
        print(f"[WhiteListPlugin] 用户 {sender} 请求查看白名单")
        if not self.whitelist:
            yield event.plain_result("白名单为空")
            print("[WhiteListPlugin] 白名单为空")
        else:
            whitelist_str = "\n".join(self.whitelist)
            yield event.plain_result(f"当前白名单:\n{whitelist_str}")
            print(f"[WhiteListPlugin] 当前白名单:\n{whitelist_str}")

    @filter.message_preprocessor()
    async def message_check(self, event: AstrMessageEvent):
        """消息预处理：群聊中仅允许白名单用户的消息通过，其他消息停止传播。"""
        # 优先判定是否为群聊，私聊直接放行
        try:
            if not event.is_group_chat():
                return
        except Exception:
            # 某些平台事件可能没有 is_group_chat 方法，尝试检查 group_id
            group_id = getattr(event, "group_id", None) or getattr(getattr(event, "message_obj", None), "group_id", None)
            if not group_id:
                return

        # 如果白名单为空，则允许所有消息通过（保持向后兼容）
        if not self.whitelist:
            return

        sender_id = event.get_sender_id()
        if sender_id in self.whitelist:
            return

        logger.info(f"阻止来自非白名单用户 {sender_id} 的群消息: {getattr(event, 'message_str', '')}")
        print(f"[WhiteListPlugin] 阻止来自非白名单用户 {sender_id} 的群消息")
        # 停止事件继续传播，防止机器人回应
        try:
            event.stop_propagation()
        except Exception:
            # 如果没有 stop_propagation，尝试返回停止结果（兼容性处理）
            try:
                return MessageEventResult.STOP
            except Exception:
                return

    async def terminate(self):
        """插件销毁"""
        logger.info("白名单插件已卸载")
        print("[WhiteListPlugin] 插件已卸载")
