"""OCR识别模块"""
from typing import Dict, Any


class OCREngine:
    """最基础的OCR识别类"""
    
    def __init__(self):
        self.name = "OCREngine"
    
    async def test_connection(self) -> Dict[str, Any]:
        """测试连接方法 - 最基础的功能"""
        return {
            "status": "success",
            "message": f"{self.name} 模块已初始化",
            "module": self.name
        }
    
    async def recognize_text(self, image_path: str) -> Dict[str, Any]:
        """文字识别方法 - 最基础的功能"""
        return {
            "image_path": image_path,
            "status": "not_implemented",
            "message": "基础功能，待实现"
        }
