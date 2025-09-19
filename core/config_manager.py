"""
配置管理器 - 负责应用程序配置的持久化存储
Project: QMW-CoreApp (Qi Men Workbench - Core Application)
Task ID: FEAT-20250901-020-Comprehensive (全面首选项系统)
"""

from PySide6.QtCore import QSettings
from ui.config import DisplayConfig
from typing import Any, Dict
import os
import json


class ConfigManager:
    """
    配置管理器 - 使用QSettings对应用程序的所有配置进行本地持久化读写
    
    功能：
    1. 使用QSettings进行跨平台配置存储
    2. 管理显示配置(DisplayConfig)
    3. 管理通用配置(主题、语言、启动行为)
    4. 管理数据配置(默认工作区路径等)
    5. 提供安全的默认值
    """
    
    def __init__(self):
        """初始化配置管理器"""
        # 设置组织和应用程序名称，QSettings会自动选择合适的存储位置
        # Windows: 注册表
        # macOS/Linux: .ini文件
        self.settings = QSettings("QiMenWorkbench", "QiMenCore")
        
    def load_config(self) -> DisplayConfig:
        """
        从持久化存储中读取所有配置项，构建并返回DisplayConfig对象
        [保持向后兼容性的别名方法]
        
        Returns:
            DisplayConfig: 配置对象，如果某项不存在则使用默认值
        """
        return self.load_display_config()
        
    def load_display_config(self) -> DisplayConfig:
        """
        从持久化存储中读取盘面显示配置，构建并返回DisplayConfig对象
        
        Returns:
            DisplayConfig: 配置对象，如果某项不存在则使用默认值
        """
        # 创建默认配置作为基准
        default_config = DisplayConfig()
        
        try:
            # 样式设置
            use_wuxing_colors = self.settings.value(
                "display/use_wuxing_colors", 
                default_config.use_wuxing_colors, 
                type=bool
            )
            
            show_zhi_fu_shi_bold = self.settings.value(
                "display/show_zhi_fu_shi_bold", 
                default_config.show_zhi_fu_shi_bold, 
                type=bool
            )
            
            auto_yue_ling_chong_kong = self.settings.value(
                "display/auto_yue_ling_chong_kong", 
                default_config.auto_yue_ling_chong_kong, 
                type=bool
            )
            
            auto_maxing_chong_mu_kong = self.settings.value(
                "display/auto_maxing_chong_mu_kong", 
                default_config.auto_maxing_chong_mu_kong, 
                type=bool
            )
            
            # 参数显示控制
            show_ri_kong = self.settings.value(
                "display/show_ri_kong", 
                default_config.show_ri_kong, 
                type=bool
            )
            
            show_shi_kong = self.settings.value(
                "display/show_shi_kong", 
                default_config.show_shi_kong, 
                type=bool
            )
            
            show_liu_ji = self.settings.value(
                "display/show_liu_ji", 
                default_config.show_liu_ji, 
                type=bool
            )
            
            show_ru_mu = self.settings.value(
                "display/show_ru_mu", 
                default_config.show_ru_mu, 
                type=bool
            )
            
            show_ma_xing = self.settings.value(
                "display/show_ma_xing", 
                default_config.show_ma_xing, 
                type=bool
            )
            
            show_yue_ling = self.settings.value(
                "display/show_yue_ling", 
                default_config.show_yue_ling, 
                type=bool
            )
            
            show_di_pan_gate = self.settings.value(
                "display/show_di_pan_gate", 
                default_config.show_di_pan_gate, 
                type=bool
            )
            
            show_di_pan_star = self.settings.value(
                "display/show_di_pan_star", 
                default_config.show_di_pan_star, 
                type=bool
            )
            
            # 参数状态角标配置（新增）
            show_parameter_states = self.settings.value(
                "display/show_parameter_states", 
                default_config.show_parameter_states, 
                type=bool
            )
            
            show_tiangan_changsheng = self.settings.value(
                "display/show_tiangan_changsheng", 
                default_config.show_tiangan_changsheng, 
                type=bool
            )
            
            show_bamen_wangxiang = self.settings.value(
                "display/show_bamen_wangxiang", 
                default_config.show_bamen_wangxiang, 
                type=bool
            )
            
            show_jiuxing_wangxiang = self.settings.value(
                "display/show_jiuxing_wangxiang", 
                default_config.show_jiuxing_wangxiang, 
                type=bool
            )
            
            show_bashen_wangxiang = self.settings.value(
                "display/show_bashen_wangxiang", 
                default_config.show_bashen_wangxiang, 
                type=bool
            )
            
            # 数值配置
            annotation_background_alpha = self.settings.value(
                "display/annotation_background_alpha", 
                default_config.annotation_background_alpha, 
                type=int
            )
            
            selected_border_width = self.settings.value(
                "display/selected_border_width", 
                default_config.selected_border_width, 
                type=int
            )
            
            annotation_circle_radius = self.settings.value(
                "display/annotation_circle_radius", 
                default_config.annotation_circle_radius, 
                type=int
            )
            
            # 加载五行颜色配置 (新增)
            wuxing_colors_str = self.settings.value(
                "display/wuxing_colors",
                json.dumps(default_config.wuxing_colors)
            )
            try:
                wuxing_colors = json.loads(wuxing_colors_str) if isinstance(wuxing_colors_str, str) else default_config.wuxing_colors
                # 确保包含所有五行
                for wuxing in ["金", "木", "水", "火", "土"]:
                    if wuxing not in wuxing_colors:
                        wuxing_colors[wuxing] = default_config.wuxing_colors[wuxing]
            except (json.JSONDecodeError, TypeError):
                wuxing_colors = default_config.wuxing_colors
            
            # 构建配置对象
            config = DisplayConfig(
                use_wuxing_colors=use_wuxing_colors,
                show_zhi_fu_shi_bold=show_zhi_fu_shi_bold,
                auto_yue_ling_chong_kong=auto_yue_ling_chong_kong,
                auto_maxing_chong_mu_kong=auto_maxing_chong_mu_kong,
                show_ri_kong=show_ri_kong,
                show_shi_kong=show_shi_kong,
                show_liu_ji=show_liu_ji,
                show_ru_mu=show_ru_mu,
                show_ma_xing=show_ma_xing,
                show_yue_ling=show_yue_ling,
                show_di_pan_gate=show_di_pan_gate,
                show_di_pan_star=show_di_pan_star,
                show_parameter_states=show_parameter_states,  # 新增
                show_tiangan_changsheng=show_tiangan_changsheng,  # 新增
                show_bamen_wangxiang=show_bamen_wangxiang,  # 新增
                show_jiuxing_wangxiang=show_jiuxing_wangxiang,  # 新增
                show_bashen_wangxiang=show_bashen_wangxiang,  # 新增
                wuxing_colors=wuxing_colors,  # 新增
                annotation_background_alpha=annotation_background_alpha,
                selected_border_width=selected_border_width,
                annotation_circle_radius=annotation_circle_radius
            )
            
            return config
            
        except Exception as e:
            # 如果读取配置时出现任何错误，返回默认配置
            print(f"Warning: Failed to load config, using defaults: {e}")
            return default_config
    
    def save_config(self, config: DisplayConfig) -> bool:
        """
        接收DisplayConfig对象，将其所有属性写入持久化存储
        [保持向后兼容性的别名方法]
        
        Args:
            config: 要保存的配置对象
            
        Returns:
            bool: 保存是否成功
        """
        return self.save_display_config(config)
        
    def save_display_config(self, config: DisplayConfig) -> bool:
        """
        接收DisplayConfig对象，将其所有属性写入持久化存储
        
        Args:
            config: 要保存的配置对象
            
        Returns:
            bool: 保存是否成功
        """
        try:
            # 样式设置
            self.settings.setValue("display/use_wuxing_colors", config.use_wuxing_colors)
            self.settings.setValue("display/show_zhi_fu_shi_bold", config.show_zhi_fu_shi_bold)
            self.settings.setValue("display/auto_yue_ling_chong_kong", config.auto_yue_ling_chong_kong)
            self.settings.setValue("display/auto_maxing_chong_mu_kong", config.auto_maxing_chong_mu_kong)
            
            # 参数显示控制
            self.settings.setValue("display/show_ri_kong", config.show_ri_kong)
            self.settings.setValue("display/show_shi_kong", config.show_shi_kong)
            self.settings.setValue("display/show_liu_ji", config.show_liu_ji)
            self.settings.setValue("display/show_ru_mu", config.show_ru_mu)
            self.settings.setValue("display/show_ma_xing", config.show_ma_xing)
            self.settings.setValue("display/show_yue_ling", config.show_yue_ling)
            self.settings.setValue("display/show_di_pan_gate", config.show_di_pan_gate)
            self.settings.setValue("display/show_di_pan_star", config.show_di_pan_star)
            
            # 参数状态角标配置（新增）
            self.settings.setValue("display/show_parameter_states", config.show_parameter_states)
            self.settings.setValue("display/show_tiangan_changsheng", config.show_tiangan_changsheng)
            self.settings.setValue("display/show_bamen_wangxiang", config.show_bamen_wangxiang)
            self.settings.setValue("display/show_jiuxing_wangxiang", config.show_jiuxing_wangxiang)
            self.settings.setValue("display/show_bashen_wangxiang", config.show_bashen_wangxiang)
            
            # 数值配置
            self.settings.setValue("display/annotation_background_alpha", config.annotation_background_alpha)
            self.settings.setValue("display/selected_border_width", config.selected_border_width)
            self.settings.setValue("display/annotation_circle_radius", config.annotation_circle_radius)
            
            # 保存五行颜色配置 (新增)
            self.settings.setValue("display/wuxing_colors", json.dumps(config.wuxing_colors))
            
            # 确保配置写入磁盘
            self.settings.sync()
            
            return True
            
        except Exception as e:
            print(f"Error: Failed to save config: {e}")
            return False
    
    def reset_to_defaults(self) -> DisplayConfig:
        """
        重置所有配置为默认值
        
        Returns:
            DisplayConfig: 默认配置对象
        """
        default_config = DisplayConfig()
        self.save_config(default_config)
        return default_config
    
    def get_config_info(self) -> Dict[str, Any]:
        """
        获取配置存储的基本信息（用于调试）
        
        Returns:
            Dict: 包含配置文件路径等信息的字典
        """
        return {
            "organization": self.settings.organizationName(),
            "application": self.settings.applicationName(),
            "format": self.settings.format(),
            "scope": self.settings.scope(),
            "filename": self.settings.fileName() if hasattr(self.settings, 'fileName') else "Registry"
        }
    
    def load_general_config(self) -> Dict[str, Any]:
        """
        加载通用配置(主题、语言、启动行为等)
        
        Returns:
            Dict: 通用配置字典
        """
        try:
            config = {
                "theme": self.settings.value("general/theme", "light", type=str),
                "language": self.settings.value("general/language", "zh_CN", type=str),
                "auto_load_last_workspace": self.settings.value(
                    "general/auto_load_last_workspace", True, type=bool
                ),
                "last_workspace_path": self.settings.value(
                    "general/last_workspace_path", "", type=str
                )
            }
            return config
        except Exception as e:
            print(f"Warning: Failed to load general config, using defaults: {e}")
            return {
                "theme": "light",
                "language": "zh_CN", 
                "auto_load_last_workspace": True,
                "last_workspace_path": ""
            }
    
    def save_general_config(self, config: Dict[str, Any]) -> bool:
        """
        保存通用配置
        
        Args:
            config: 通用配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            self.settings.setValue("general/theme", config.get("theme", "light"))
            self.settings.setValue("general/language", config.get("language", "zh_CN"))
            self.settings.setValue("general/auto_load_last_workspace", 
                                 config.get("auto_load_last_workspace", True))
            self.settings.setValue("general/last_workspace_path", 
                                 config.get("last_workspace_path", ""))
            
            self.settings.sync()
            return True
            
        except Exception as e:
            print(f"Error: Failed to save general config: {e}")
            return False
    
    def load_data_config(self) -> Dict[str, Any]:
        """
        加载数据配置(默认工作区路径、缓存设置等)
        
        Returns:
            Dict: 数据配置字典
        """
        try:
            config = {
                "default_workspace_path": self.settings.value(
                    "data/default_workspace_path", "", type=str
                ),
                "auto_save_interval": self.settings.value(
                    "data/auto_save_interval", 300, type=int  # 5分钟
                ),
                "max_recent_files": self.settings.value(
                    "data/max_recent_files", 10, type=int
                ),
                "cache_enabled": self.settings.value(
                    "data/cache_enabled", True, type=bool
                )
            }
            return config
        except Exception as e:
            print(f"Warning: Failed to load data config, using defaults: {e}")
            return {
                "default_workspace_path": "",
                "auto_save_interval": 300,
                "max_recent_files": 10,
                "cache_enabled": True
            }
    
    def save_data_config(self, config: Dict[str, Any]) -> bool:
        """
        保存数据配置
        
        Args:
            config: 数据配置字典
            
        Returns:
            bool: 保存是否成功
        """
        try:
            self.settings.setValue("data/default_workspace_path", 
                                 config.get("default_workspace_path", ""))
            self.settings.setValue("data/auto_save_interval", 
                                 config.get("auto_save_interval", 300))
            self.settings.setValue("data/max_recent_files", 
                                 config.get("max_recent_files", 10))
            self.settings.setValue("data/cache_enabled", 
                                 config.get("cache_enabled", True))
            
            self.settings.sync()
            return True
            
        except Exception as e:
            print(f"Error: Failed to save data config: {e}")
            return False
    
    def get_config_file_path(self) -> str:
        """
        获取配置文件的路径（用于"打开配置文件夹"功能）
        
        Returns:
            str: 配置文件路径或配置存储位置描述
        """
        if hasattr(self.settings, 'fileName'):
            return self.settings.fileName()
        else:
            # Windows注册表情况
            return f"Registry: {self.settings.organizationName()}/{self.settings.applicationName()}"
    
    def clear_all_configs(self) -> bool:
        """
        清除所有配置（慎用）
        
        Returns:
            bool: 清除是否成功
        """
        try:
            self.settings.clear()
            self.settings.sync()
            return True
        except Exception as e:
            print(f"Error: Failed to clear configs: {e}")
            return False
