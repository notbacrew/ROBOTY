"""
Тесты для модуля парсинга JSON и TXT файлов.
"""
import unittest
import tempfile
import os
import json
from core.parser import parse_input, Robot, Operation, Scenario
from core.parser_txt import parse_txt_input, RobotConfig, Operation as TxtOperation, ScenarioTxt


class TestJsonParser(unittest.TestCase):
    """Тесты для парсера JSON файлов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.valid_json_data = {
            "robots": [
                {
                    "id": 1,
                    "base_xyz": [0, 0, 0],
                    "joint_limits": [[-180, 180], [-90, 90], [-90, 90], [-180, 180], [-90, 90], [-90, 90]],
                    "vmax": [1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
                    "amax": [2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
                    "tool_clearance": 0.1
                }
            ],
            "safe_dist": 0.5,
            "operations": [
                {
                    "id": 1,
                    "pick_xyz": [1, 2, 0],
                    "place_xyz": [2, 3, 1],
                    "t_hold": 1.0
                }
            ]
        }
    
    def test_valid_json_parsing(self):
        """Тест парсинга корректного JSON файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_json_data, f)
            temp_path = f.name
        
        try:
            scenario = parse_input(temp_path)
            
            self.assertIsInstance(scenario, Scenario)
            self.assertEqual(len(scenario.robots), 1)
            self.assertEqual(len(scenario.operations), 1)
            self.assertEqual(scenario.safe_dist, 0.5)
            
            robot = scenario.robots[0]
            self.assertEqual(robot.id, 1)
            self.assertEqual(robot.base_xyz, (0, 0, 0))
            self.assertEqual(robot.tool_clearance, 0.1)
            
            operation = scenario.operations[0]
            self.assertEqual(operation.id, 1)
            self.assertEqual(operation.pick_xyz, (1, 2, 0))
            self.assertEqual(operation.place_xyz, (2, 3, 1))
            self.assertEqual(operation.t_hold, 1.0)
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_json_format(self):
        """Тест обработки некорректного JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_file(self):
        """Тест обработки отсутствующего файла"""
        with self.assertRaises(FileNotFoundError):
            parse_input("nonexistent_file.json")
    
    def test_missing_robots_section(self):
        """Тест обработки отсутствующей секции robots"""
        invalid_data = {"operations": [], "safe_dist": 0.5}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_missing_operations_section(self):
        """Тест обработки отсутствующей секции operations"""
        invalid_data = {"robots": [], "safe_dist": 0.5}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(invalid_data, f)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_input(temp_path)
        finally:
            os.unlink(temp_path)


class TestTxtParser(unittest.TestCase):
    """Тесты для парсера TXT файлов"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.valid_txt_content = """2 3
0.0 0.0 0.0
1.0 1.0 0.0
-180 180 1.0 2.0
-90 90 1.0 2.0
-90 90 1.0 2.0
-180 180 1.0 2.0
-90 90 1.0 2.0
-90 90 1.0 2.0
0.1 0.5
1.0 2.0 0.0 2.0 3.0 1.0 1.0
0.5 1.5 0.0 1.5 2.5 0.5 0.5
2.0 1.0 0.0 3.0 2.0 1.0 1.5"""
    
    def test_valid_txt_parsing(self):
        """Тест парсинга корректного TXT файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.valid_txt_content)
            temp_path = f.name
        
        try:
            scenario = parse_txt_input(temp_path)
            
            self.assertIsInstance(scenario, ScenarioTxt)
            self.assertEqual(len(scenario.robots), 2)
            self.assertEqual(len(scenario.operations), 3)
            self.assertEqual(scenario.safe_dist, 0.5)
            
            # Проверяем первого робота
            robot1 = scenario.robots[0]
            self.assertEqual(robot1.base_xyz, (0.0, 0.0, 0.0))
            self.assertEqual(robot1.tool_clearance, 0.1)
            
            # Проверяем первую операцию
            operation1 = scenario.operations[0]
            self.assertEqual(operation1.pick_xyz, (1.0, 2.0, 0.0))
            self.assertEqual(operation1.place_xyz, (2.0, 3.0, 1.0))
            self.assertEqual(operation1.t_hold, 1.0)
            
        finally:
            os.unlink(temp_path)
    
    def test_invalid_txt_format(self):
        """Тест обработки некорректного TXT файла"""
        invalid_content = "invalid format"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(invalid_content)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_txt_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_empty_file(self):
        """Тест обработки пустого файла"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_txt_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_insufficient_lines(self):
        """Тест обработки файла с недостаточным количеством строк"""
        insufficient_content = "2 3\n0.0 0.0 0.0"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(insufficient_content)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_txt_input(temp_path)
        finally:
            os.unlink(temp_path)
    
    def test_negative_values(self):
        """Тест обработки отрицательных значений"""
        negative_content = """1 1
0.0 0.0 0.0
-180 180 1.0 2.0
-90 90 1.0 2.0
-90 90 1.0 2.0
-180 180 1.0 2.0
-90 90 1.0 2.0
-90 90 1.0 2.0
-0.1 0.5
1.0 2.0 0.0 2.0 3.0 1.0 1.0"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(negative_content)
            temp_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                parse_txt_input(temp_path)
        finally:
            os.unlink(temp_path)


if __name__ == '__main__':
    unittest.main()
