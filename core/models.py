from typing import List, Dict, Union, Optional

class Palace:
    """代表九宫格中的一个宫"""
    def __init__(self, index: int):
        self.index: int = index
        self.zhi_fu: str = ""                # 八神 (e.g., "直符")  
        self.tian_pan_stars: List[str] = []  # 天盘星
        self.tian_pan_gates: List[str] = []  # 天盘门
        self.tian_pan_stems: List[str] = []  # 天盘干
        self.di_pan_stems: List[str] = []    # 地盘干
        self.di_pan_star: str = ""           # 地盘星 (故乡星)
        self.di_pan_gate: str = ""           # 地盘门 (故乡门)
        self.wuxing_color: str = ""          # e.g., '金'
        self.analysis: dict = {}             # 为未来的高级分析功能预留扩展点
        
        # 保留向后兼容的属性名 (deprecated, 建议使用新属性名)
        self.god: str = ""                   # 兼容 zhi_fu
        self.stars: List[str] = []           # 兼容 tian_pan_stars  
        self.gates: str = ""                 # 兼容 tian_pan_gates[0] if tian_pan_gates else ""
        self.heaven_stems: List[str] = []    # 兼容 tian_pan_stems
        self.earth_stems: List[str] = []     # 兼容 di_pan_stems
        self.original_star: str = ""         # 兼容 di_pan_star
        self.original_gate: str = ""         # 兼容 di_pan_gate

    def __repr__(self) -> str:
        return (
            f"--- 宫 {self.index} ---\n"
            f" 八神: {self.zhi_fu}\n"
            f" 天盘星: {', '.join(self.tian_pan_stars)}\n"
            f" 天盘门: {', '.join(self.tian_pan_gates)}\n"
            f" 天盘干: {', '.join(self.tian_pan_stems)}\n"
            f" 地盘干: {', '.join(self.di_pan_stems)}\n"
            f" 地盘星: {self.di_pan_star}\n"
            f" 地盘门: {self.di_pan_gate}\n"
        )

class ChartResult:
    """封装完整的排盘结果"""
    def __init__(self):
        self.si_zhu: Dict[str, str] = {}
        self.jieqi: str = ""
        self.ju_shu_info: Dict[str, Union[str, int]] = {}
        self.shi_chen_xun: Dict[str, str] = {}
        self.zhi_fu: str = ""
        self.zhi_shi: str = ""
        self.tian_yi: str = ""  # 天乙 (九星名)
        self.ma_xing: str = ""
        self.kong_wang: Dict[str, List[str]] = {}
        self.palaces: List[Palace] = [Palace(i) for i in range(10)] # Index 0 is unused
        # 新的结构化标注数据，每个标注携带类型信息
        self.side_annotations: Dict[str, List[Dict[str, Union[str, bool]]]] = {}
        # 马星冲动目标分析结果 - 修正为复数形式
        self.maxing_chongdong_targets: List[Dict[str, str]] = []
        # 起局时间（用于显示）
        self.qi_ju_time: str = ""
        # 反向查询索引
        self.index: dict = {}

    def _build_index(self) -> dict:
        """构建反向查询索引"""
        index = {}
        
        # 遍历每个宫（索引1-9）
        for palace_idx in range(1, 10):
            palace = self.palaces[palace_idx]
            
            # 处理八神 (zhi_fu)
            if palace.zhi_fu:
                self._add_to_index(index, 'baShen', palace.zhi_fu, palace_idx, 'zhi_fu', palace.zhi_fu)
            
            # 处理天盘星 (tian_pan_stars)
            for star_idx, star in enumerate(palace.tian_pan_stars):
                if star:
                    self._add_to_index(index, 'jiuXing', star, palace_idx, 'tian_pan_stars', star, star_idx)
            
            # 处理天盘门 (tian_pan_gates)
            for gate_idx, gate in enumerate(palace.tian_pan_gates):
                if gate:
                    self._add_to_index(index, 'baMen', gate, palace_idx, 'tian_pan_gates', gate, gate_idx)
            
            # 处理天盘干 (tian_pan_stems)
            for stem_idx, stem in enumerate(palace.tian_pan_stems):
                if stem:
                    self._add_to_index(index, 'tianGan', stem, palace_idx, 'tian_pan_stems', stem, stem_idx)
            
            # 处理地盘干 (di_pan_stems)
            for stem_idx, stem in enumerate(palace.di_pan_stems):
                if stem:
                    self._add_to_index(index, 'tianGan', stem, palace_idx, 'di_pan_stems', stem, stem_idx)
            
            # 处理地盘星 (di_pan_star)
            if palace.di_pan_star:
                self._add_to_index(index, 'jiuXing', palace.di_pan_star, palace_idx, 'di_pan_star', palace.di_pan_star)
            
            # 处理地盘门 (di_pan_gate)
            if palace.di_pan_gate:
                self._add_to_index(index, 'baMen', palace.di_pan_gate, palace_idx, 'di_pan_gate', palace.di_pan_gate)
        
        return index
    
    def _add_to_index(self, index: dict, param_type: str, param_name: str, palace_index: int, 
                     attribute_name: str, text: str, sub_index: int = None):
        """添加参数到索引"""
        if param_type not in index:
            index[param_type] = {}
        if param_name not in index[param_type]:
            index[param_type][param_name] = []
        
        # 生成唯一ID
        if sub_index is not None:
            unique_id = f"palace_{palace_index}_{attribute_name}_{sub_index}"
        else:
            unique_id = f"palace_{palace_index}_{attribute_name}"
        
        location_obj = {
            "palace_index": palace_index,
            "param_type": param_type,
            "attribute_name": attribute_name,
            "text": text,
            "id": unique_id
        }
        
        if sub_index is not None:
            location_obj["sub_index"] = sub_index
            
        index[param_type][param_name].append(location_obj)

    def __repr__(self) -> str:
        info_str = (
            f"四柱: {self.si_zhu['年']} {self.si_zhu['月']} {self.si_zhu['日']} {self.si_zhu['时']}\n"
            f"节气: {self.jieqi}\n"
            f"局数: {self.ju_shu_info['遁']}{self.ju_shu_info['局']}局\n"
            f"旬首: 甲{self.shi_chen_xun.get('zhi', '')}{self.shi_chen_xun.get('jun', '')}\n"
            f"直符: {self.zhi_fu}\n"
            f"值使: {self.zhi_shi}\n"
            f"天乙: {self.tian_yi}\n"
            f"马星: {self.ma_xing}\n"
            f"空亡: 日空({','.join(self.kong_wang.get('日空', []))}), 时空({','.join(self.kong_wang.get('时空', []))})\n"
        )
        palace_str = "".join([repr(p) for p in self.palaces if p.index != 0 and p.index != 5])
        palace_5_str = repr(self.palaces[5])
        return info_str + "\n" + palace_str + "\n" + palace_5_str


class Case:
    """案例数据模型 - 包含排盘结果和用户标注"""
    def __init__(self, title: str, chart_result: ChartResult):
        self.title: str = title
        self.chart_result: ChartResult = chart_result
        # 标注数据存储 - 支持一个参数多个标注（保留用于向后兼容）
        # 键: 唯一的参数ID (e.g., "palace_7_heaven_stem_0")
        # 值: 标注对象的列表 (e.g., [{"text": "用神", "shape": "circle", "color": "#FF0000"}, {"text": "丈夫", "shape": "square", "color": "#00FF00"}])
        self.annotations: Dict[str, List[Dict[str, str]]] = {}
        
        # 新的图层化标注系统
        self.annotation_layers: List[Dict[str, Union[str, bool, Dict[str, List[Dict[str, str]]]]]] = []
        self.active_layer_index: int = -1
        
        # 初始化默认图层
        self._initialize_default_layer()
        
    def _initialize_default_layer(self):
        """初始化默认图层"""
        if not self.annotation_layers:
            default_layer = {
                "name": "默认图层",
                "is_visible": True,
                "annotations": {}
            }
            self.annotation_layers.append(default_layer)
            self.active_layer_index = 0
            
    def get_active_layer(self) -> Optional[Dict]:
        """获取当前激活的图层"""
        if 0 <= self.active_layer_index < len(self.annotation_layers):
            return self.annotation_layers[self.active_layer_index]
        return None
        
    def get_active_annotations(self) -> Dict[str, List[Dict[str, str]]]:
        """获取当前激活图层的标注"""
        active_layer = self.get_active_layer()
        if active_layer:
            return active_layer.get("annotations", {})
        return {}
        
    def get_all_visible_annotations(self) -> Dict[str, List[Dict[str, str]]]:
        """获取所有可见图层的标注合并结果"""
        merged_annotations = {}
        
        for layer in self.annotation_layers:
            if layer.get("is_visible", False):
                layer_annotations = layer.get("annotations", {})
                for param_id, annotations_list in layer_annotations.items():
                    if param_id not in merged_annotations:
                        merged_annotations[param_id] = []
                    merged_annotations[param_id].extend(annotations_list)
                    
        return merged_annotations
        
    def add_layer(self, name: str = "新图层") -> int:
        """添加新图层，返回图层索引"""
        new_layer = {
            "name": name,
            "is_visible": True,
            "annotations": {}
        }
        self.annotation_layers.append(new_layer)
        new_index = len(self.annotation_layers) - 1
        self.active_layer_index = new_index
        return new_index
        
    def remove_layer(self, layer_index: int) -> bool:
        """删除指定图层"""
        if 0 <= layer_index < len(self.annotation_layers) and len(self.annotation_layers) > 1:
            self.annotation_layers.pop(layer_index)
            
            # 调整激活图层索引
            if self.active_layer_index >= len(self.annotation_layers):
                self.active_layer_index = len(self.annotation_layers) - 1
            elif self.active_layer_index > layer_index:
                self.active_layer_index -= 1
                
            return True
        return False
        
    def rename_layer(self, layer_index: int, new_name: str) -> bool:
        """重命名图层"""
        if 0 <= layer_index < len(self.annotation_layers):
            self.annotation_layers[layer_index]["name"] = new_name
            return True
        return False
        
    def set_layer_visibility(self, layer_index: int, visible: bool) -> bool:
        """设置图层可见性"""
        if 0 <= layer_index < len(self.annotation_layers):
            self.annotation_layers[layer_index]["is_visible"] = visible
            return True
        return False
        
    def set_active_layer(self, layer_index: int) -> bool:
        """设置激活图层"""
        if 0 <= layer_index < len(self.annotation_layers):
            self.active_layer_index = layer_index
            return True
        return False
        
    def add_annotation(self, param_id: str, text: str, shape: str = "circle", color: str = "#FF0000") -> None:
        """添加标注到当前激活图层的标注列表"""
        active_layer = self.get_active_layer()
        if not active_layer:
            return
            
        annotations = active_layer["annotations"]
        if param_id not in annotations:
            annotations[param_id] = []
        
        annotation = {
            "text": text,
            "shape": shape,
            "color": color
        }
        annotations[param_id].append(annotation)
        
    def remove_annotation(self, param_id: str, annotation_index: int = None) -> None:
        """删除标注 - 可以删除指定索引的标注或全部标注"""
        active_layer = self.get_active_layer()
        if not active_layer:
            return
            
        annotations = active_layer["annotations"]
        if param_id not in annotations:
            return
            
        if annotation_index is None:
            # 删除该参数的所有标注
            del annotations[param_id]
        else:
            # 删除指定索引的标注
            if 0 <= annotation_index < len(annotations[param_id]):
                annotations[param_id].pop(annotation_index)
                # 如果列表为空，删除整个键
                if not annotations[param_id]:
                    del annotations[param_id]
                    
    def update_annotation(self, param_id: str, annotation_index: int, text: str, shape: str = "circle", color: str = "#FF0000") -> None:
        """更新指定索引的标注"""
        active_layer = self.get_active_layer()
        if not active_layer:
            return
            
        annotations = active_layer["annotations"]
        if param_id in annotations and 0 <= annotation_index < len(annotations[param_id]):
            annotations[param_id][annotation_index] = {
                "text": text,
                "shape": shape,
                "color": color
            }
            
    def has_annotation(self, param_id: str) -> bool:
        """检查参数是否有标注（检查所有可见图层）"""
        visible_annotations = self.get_all_visible_annotations()
        return param_id in visible_annotations and len(visible_annotations[param_id]) > 0
        
    def get_annotations(self, param_id: str) -> List[Dict[str, str]]:
        """获取参数的所有标注（从所有可见图层）"""
        visible_annotations = self.get_all_visible_annotations()
        return visible_annotations.get(param_id, [])
        
    def get_annotation_texts(self, param_id: str) -> List[str]:
        """获取参数的所有标注文本"""
        annotations = self.get_annotations(param_id)
        return [annotation["text"] for annotation in annotations]
        
    def get_annotation_count(self, param_id: str) -> int:
        """获取参数的标注数量"""
        return len(self.get_annotations(param_id))
        
    def get_all_annotation_count(self) -> int:
        """获取所有标注的总数量"""
        total = 0
        visible_annotations = self.get_all_visible_annotations()
        for annotations_list in visible_annotations.values():
            total += len(annotations_list)
        return total
