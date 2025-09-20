"""
Тесты для модуля проверки коллизий.
"""
import unittest
from core.collision import (
    interpolate_position, calculate_distance, get_time_range,
    check_collisions_detailed, check_collisions, check_static_obstacles,
    get_collision_summary, CollisionInfo
)


class TestCollisionUtils(unittest.TestCase):
    """Тесты для вспомогательных функций"""
    
    def test_calculate_distance(self):
        """Тест вычисления расстояния между точками"""
        # Тест одинаковых точек
        self.assertEqual(calculate_distance((0, 0, 0), (0, 0, 0)), 0.0)
        
        # Тест простого расстояния
        self.assertAlmostEqual(calculate_distance((0, 0, 0), (3, 4, 0)), 5.0, places=5)
        
        # Тест 3D расстояния
        self.assertAlmostEqual(calculate_distance((0, 0, 0), (1, 1, 1)), 1.732, places=3)
    
    def test_interpolate_position(self):
        """Тест интерполяции позиции"""
        trajectory = [
            {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
            {"t": 1.0, "x": 1.0, "y": 1.0, "z": 1.0},
            {"t": 2.0, "x": 2.0, "y": 2.0, "z": 2.0}
        ]
        
        # Тест точного совпадения с waypoint
        pos = interpolate_position(trajectory, 1.0)
        self.assertEqual(pos, (1.0, 1.0, 1.0))
        
        # Тест интерполяции между waypoints
        pos = interpolate_position(trajectory, 0.5)
        self.assertEqual(pos, (0.5, 0.5, 0.5))
        
        # Тест времени до первого waypoint
        pos = interpolate_position(trajectory, -0.5)
        self.assertEqual(pos, (0.0, 0.0, 0.0))
        
        # Тест времени после последнего waypoint
        pos = interpolate_position(trajectory, 3.0)
        self.assertEqual(pos, (2.0, 2.0, 2.0))
    
    def test_get_time_range(self):
        """Тест определения временного диапазона"""
        plan = {
            "robots": [
                {
                    "trajectory": [
                        {"t": 0.0, "x": 0, "y": 0, "z": 0},
                        {"t": 2.0, "x": 1, "y": 1, "z": 1}
                    ]
                },
                {
                    "trajectory": [
                        {"t": 1.0, "x": 0, "y": 0, "z": 0},
                        {"t": 3.0, "x": 2, "y": 2, "z": 2}
                    ]
                }
            ]
        }
        
        start_time, end_time = get_time_range(plan)
        self.assertEqual(start_time, 0.0)
        self.assertEqual(end_time, 3.0)
    
    def test_get_time_range_empty(self):
        """Тест определения временного диапазона для пустого плана"""
        plan = {"robots": []}
        
        start_time, end_time = get_time_range(plan)
        self.assertEqual(start_time, float('inf'))
        self.assertEqual(end_time, 0.0)


class TestCollisionDetection(unittest.TestCase):
    """Тесты для детекции коллизий"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.plan_no_collision = {
            "robots": [
                {
                    "id": 1,
                    "trajectory": [
                        {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
                        {"t": 1.0, "x": 1.0, "y": 0.0, "z": 0.0},
                        {"t": 2.0, "x": 2.0, "y": 0.0, "z": 0.0}
                    ],
                    "tool_clearance": 0.1
                },
                {
                    "id": 2,
                    "trajectory": [
                        {"t": 0.0, "x": 0.0, "y": 2.0, "z": 0.0},
                        {"t": 1.0, "x": 1.0, "y": 2.0, "z": 0.0},
                        {"t": 2.0, "x": 2.0, "y": 2.0, "z": 0.0}
                    ],
                    "tool_clearance": 0.1
                }
            ],
            "safe_dist": 0.5
        }
        
        self.plan_with_collision = {
            "robots": [
                {
                    "id": 1,
                    "trajectory": [
                        {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
                        {"t": 1.0, "x": 1.0, "y": 0.0, "z": 0.0}
                    ],
                    "tool_clearance": 0.1
                },
                {
                    "id": 2,
                    "trajectory": [
                        {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
                        {"t": 1.0, "x": 0.0, "y": 1.0, "z": 0.0}
                    ],
                    "tool_clearance": 0.1
                }
            ],
            "safe_dist": 0.5
        }
    
    def test_no_collisions(self):
        """Тест отсутствия коллизий"""
        collisions = check_collisions_detailed(self.plan_no_collision)
        self.assertEqual(len(collisions), 0)
        
        has_collisions = check_collisions(self.plan_no_collision)
        self.assertFalse(has_collisions)
    
    def test_collisions_detected(self):
        """Тест обнаружения коллизий"""
        collisions = check_collisions_detailed(self.plan_with_collision)
        self.assertGreater(len(collisions), 0)
        
        has_collisions = check_collisions(self.plan_with_collision)
        self.assertTrue(has_collisions)
        
        # Проверяем структуру информации о коллизии
        collision = collisions[0]
        self.assertIsInstance(collision, CollisionInfo)
        self.assertIn(collision.robot1_id, [1, 2])
        self.assertIn(collision.robot2_id, [1, 2])
        self.assertGreaterEqual(collision.time, 0)
        self.assertLess(collision.distance, collision.min_required_distance)
    
    def test_single_robot(self):
        """Тест плана с одним роботом"""
        single_robot_plan = {
            "robots": [self.plan_no_collision["robots"][0]],
            "safe_dist": 0.5
        }
        
        collisions = check_collisions_detailed(single_robot_plan)
        self.assertEqual(len(collisions), 0)
    
    def test_empty_plan(self):
        """Тест пустого плана"""
        empty_plan = {"robots": [], "safe_dist": 0.5}
        
        collisions = check_collisions_detailed(empty_plan)
        self.assertEqual(len(collisions), 0)


class TestStaticObstacles(unittest.TestCase):
    """Тесты для статических препятствий"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.plan = {
            "robots": [
                {
                    "id": 1,
                    "trajectory": [
                        {"t": 0.0, "x": 0.0, "y": 0.0, "z": 0.0},
                        {"t": 1.0, "x": 0.3, "y": 0.0, "z": 0.0}  # Ближе к препятствию
                    ],
                    "tool_clearance": 0.1
                }
            ]
        }
        
        self.sphere_obstacle = {
            "type": "sphere",
            "position": (0.2, 0.0, 0.0),  # Ближе к траектории робота
            "size": 0.1  # Меньший радиус
        }
        
        self.box_obstacle = {
            "type": "box",
            "position": (0.2, 0.0, 0.0),  # Ближе к траектории робота
            "size": (0.2, 0.2, 0.2)  # Меньший размер
        }
    
    def test_sphere_obstacle_collision(self):
        """Тест коллизии со сферическим препятствием"""
        obstacles = [self.sphere_obstacle]
        collisions = check_static_obstacles(self.plan, obstacles)
        
        self.assertGreater(len(collisions), 0)
        
        collision = collisions[0]
        self.assertEqual(collision.robot1_id, 1)
        self.assertEqual(collision.robot2_id, -1)  # -1 для препятствий
    
    def test_sphere_obstacle_no_collision(self):
        """Тест отсутствия коллизии со сферическим препятствием"""
        # Препятствие далеко от траектории
        far_obstacle = {
            "type": "sphere",
            "position": (10.0, 10.0, 10.0),
            "size": 0.5
        }
        
        obstacles = [far_obstacle]
        collisions = check_static_obstacles(self.plan, obstacles)
        
        self.assertEqual(len(collisions), 0)
    
    def test_box_obstacle_collision(self):
        """Тест коллизии с прямоугольным препятствием"""
        obstacles = [self.box_obstacle]
        collisions = check_static_obstacles(self.plan, obstacles)
        
        self.assertGreater(len(collisions), 0)
    
    def test_multiple_obstacles(self):
        """Тест множественных препятствий"""
        obstacles = [self.sphere_obstacle, self.box_obstacle]
        collisions = check_static_obstacles(self.plan, obstacles)
        
        self.assertGreater(len(collisions), 0)


class TestCollisionSummary(unittest.TestCase):
    """Тесты для сводки по коллизиям"""
    
    def test_empty_collisions(self):
        """Тест пустого списка коллизий"""
        summary = get_collision_summary([])
        
        self.assertEqual(summary["total_collisions"], 0)
        self.assertEqual(summary["robot_collisions"], 0)
        self.assertEqual(summary["obstacle_collisions"], 0)
        self.assertIsNone(summary["time_range"])
        self.assertEqual(summary["affected_robots"], [])
    
    def test_robot_collisions_summary(self):
        """Тест сводки по коллизиям роботов"""
        collisions = [
            CollisionInfo(1, 2, 1.0, (0, 0, 0), (0, 0, 0), 0.1, 0.5),
            CollisionInfo(1, 3, 2.0, (1, 1, 1), (1, 1, 1), 0.2, 0.5)
        ]
        
        summary = get_collision_summary(collisions)
        
        self.assertEqual(summary["total_collisions"], 2)
        self.assertEqual(summary["robot_collisions"], 2)
        self.assertEqual(summary["obstacle_collisions"], 0)
        self.assertEqual(summary["time_range"], (1.0, 2.0))
        self.assertEqual(set(summary["affected_robots"]), {1, 2, 3})
    
    def test_mixed_collisions_summary(self):
        """Тест сводки по смешанным коллизиям"""
        collisions = [
            CollisionInfo(1, 2, 1.0, (0, 0, 0), (0, 0, 0), 0.1, 0.5),  # робот-робот
            CollisionInfo(1, -1, 2.0, (1, 1, 1), (1, 1, 1), 0.2, 0.5)  # робот-препятствие
        ]
        
        summary = get_collision_summary(collisions)
        
        self.assertEqual(summary["total_collisions"], 2)
        self.assertEqual(summary["robot_collisions"], 1)
        self.assertEqual(summary["obstacle_collisions"], 1)
        self.assertEqual(summary["time_range"], (1.0, 2.0))
        self.assertEqual(summary["affected_robots"], [1, 2])


if __name__ == '__main__':
    unittest.main()
