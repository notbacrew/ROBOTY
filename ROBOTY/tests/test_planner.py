"""
Тесты для модуля планирования траекторий.
"""
import unittest
import math
from core.planner import (
    check_kinematics, trapezoidal_velocity_profile, 
    generate_trajectory_waypoints, plan_robot_trajectory,
    calculate_makespan, run_planner_algorithm
)
from core.parser_txt import RobotConfig, Operation, ScenarioTxt


class TestKinematics(unittest.TestCase):
    """Тесты для проверки кинематики"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.robot = RobotConfig(
            base_xyz=(0, 0, 0),
            joint_limits=[(-180, 180), (-90, 90), (-90, 90), (-180, 180), (-90, 90), (-90, 90)],
            vmax=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            amax=[2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            tool_clearance=0.1
        )
    
    def test_reachable_point(self):
        """Тест достижимой точки"""
        # Точка в пределах досягаемости
        point = (1.0, 1.0, 1.0)
        self.assertTrue(check_kinematics(self.robot, point))
    
    def test_unreachable_point(self):
        """Тест недостижимой точки"""
        # Точка слишком далеко
        point = (1000.0, 1000.0, 1000.0)
        self.assertFalse(check_kinematics(self.robot, point))
    
    def test_base_position(self):
        """Тест позиции базы робота"""
        point = (0.0, 0.0, 0.0)
        self.assertTrue(check_kinematics(self.robot, point))


class TestVelocityProfile(unittest.TestCase):
    """Тесты для трапецеидального профиля скорости"""
    
    def test_triangular_profile(self):
        """Тест треугольного профиля (недостаточно расстояния для vmax)"""
        distance = 1.0
        vmax = 2.0
        amax = 1.0
        
        t_accel, t_const, t_total = trapezoidal_velocity_profile(distance, vmax, amax)
        
        self.assertGreater(t_accel, 0)
        self.assertEqual(t_const, 0.0)
        self.assertGreater(t_total, 0)
        self.assertAlmostEqual(t_total, 2 * t_accel, places=5)
    
    def test_trapezoidal_profile(self):
        """Тест трапецеидального профиля"""
        distance = 10.0
        vmax = 2.0
        amax = 1.0
        
        t_accel, t_const, t_total = trapezoidal_velocity_profile(distance, vmax, amax)
        
        self.assertGreater(t_accel, 0)
        self.assertGreater(t_const, 0)
        self.assertGreater(t_total, 0)
        self.assertAlmostEqual(t_total, 2 * t_accel + t_const, places=5)
    
    def test_zero_distance(self):
        """Тест нулевого расстояния"""
        distance = 0.0
        vmax = 2.0
        amax = 1.0
        
        t_accel, t_const, t_total = trapezoidal_velocity_profile(distance, vmax, amax)
        
        self.assertEqual(t_accel, 0.0)
        self.assertEqual(t_const, 0.0)
        self.assertEqual(t_total, 0.0)


class TestTrajectoryGeneration(unittest.TestCase):
    """Тесты для генерации траекторий"""
    
    def test_same_points(self):
        """Тест одинаковых начальной и конечной точек"""
        start = (0, 0, 0)
        end = (0, 0, 0)
        vmax = 1.0
        amax = 2.0
        t_start = 0.0
        
        waypoints = generate_trajectory_waypoints(start, end, vmax, amax, t_start)
        
        self.assertEqual(len(waypoints), 1)
        self.assertEqual(waypoints[0], (0.0, 0.0, 0.0, 0.0))
    
    def test_normal_trajectory(self):
        """Тест нормальной траектории"""
        start = (0, 0, 0)
        end = (1, 1, 1)
        vmax = 1.0
        amax = 2.0
        t_start = 0.0
        
        waypoints = generate_trajectory_waypoints(start, end, vmax, amax, t_start, num_points=5)
        
        self.assertEqual(len(waypoints), 6)  # 5 интервалов + 1 начальная точка
        
        # Проверяем начальную точку
        self.assertEqual(waypoints[0], (0.0, 0.0, 0.0, 0.0))
        
        # Проверяем конечную точку
        last_wp = waypoints[-1]
        self.assertAlmostEqual(last_wp[1], 1.0, places=3)
        self.assertAlmostEqual(last_wp[2], 1.0, places=3)
        self.assertAlmostEqual(last_wp[3], 1.0, places=3)
        self.assertGreater(last_wp[0], 0.0)


class TestRobotTrajectoryPlanning(unittest.TestCase):
    """Тесты для планирования траектории робота"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.robot = RobotConfig(
            base_xyz=(0, 0, 0),
            joint_limits=[(-180, 180), (-90, 90), (-90, 90), (-180, 180), (-90, 90), (-90, 90)],
            vmax=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            amax=[2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            tool_clearance=0.1
        )
        
        self.operations = [
            Operation(pick_xyz=(1, 1, 0), place_xyz=(2, 2, 1), t_hold=0.5),
            Operation(pick_xyz=(3, 1, 0), place_xyz=(4, 2, 1), t_hold=1.0)
        ]
    
    def test_empty_operations(self):
        """Тест пустого списка операций"""
        waypoints = plan_robot_trajectory(self.robot, [], t0=0.0)
        
        self.assertEqual(len(waypoints), 1)
        self.assertEqual(waypoints[0], (0.0, 0.0, 0.0, 0.0))
    
    def test_single_operation(self):
        """Тест одной операции"""
        operations = [self.operations[0]]
        waypoints = plan_robot_trajectory(self.robot, operations, t0=0.0)
        
        self.assertGreater(len(waypoints), 2)
        
        # Проверяем, что траектория начинается в базе
        self.assertEqual(waypoints[0][1:], (0.0, 0.0, 0.0))
        
        # Проверяем, что траектория заканчивается в place
        last_wp = waypoints[-1]
        self.assertAlmostEqual(last_wp[1], 2.0, places=1)
        self.assertAlmostEqual(last_wp[2], 2.0, places=1)
        self.assertAlmostEqual(last_wp[3], 1.0, places=1)
    
    def test_multiple_operations(self):
        """Тест нескольких операций"""
        waypoints = plan_robot_trajectory(self.robot, self.operations, t0=0.0)
        
        self.assertGreater(len(waypoints), 4)
        
        # Проверяем, что время увеличивается
        times = [wp[0] for wp in waypoints]
        self.assertEqual(times, sorted(times))


class TestMakespanCalculation(unittest.TestCase):
    """Тесты для вычисления makespan"""
    
    def test_empty_trajectories(self):
        """Тест пустых траекторий"""
        makespan = calculate_makespan([])
        self.assertEqual(makespan, 0.0)
    
    def test_single_trajectory(self):
        """Тест одной траектории"""
        trajectory = [(0.0, 0, 0, 0), (1.0, 1, 1, 1), (2.0, 2, 2, 2)]
        makespan = calculate_makespan([trajectory])
        self.assertEqual(makespan, 2.0)
    
    def test_multiple_trajectories(self):
        """Тест нескольких траекторий"""
        trajectory1 = [(0.0, 0, 0, 0), (1.0, 1, 1, 1)]
        trajectory2 = [(0.0, 0, 0, 0), (1.5, 1, 1, 1), (3.0, 2, 2, 2)]
        makespan = calculate_makespan([trajectory1, trajectory2])
        self.assertEqual(makespan, 3.0)


class TestPlannerAlgorithm(unittest.TestCase):
    """Тесты для основного алгоритма планировщика"""
    
    def setUp(self):
        """Настройка тестовых данных"""
        self.robot1 = RobotConfig(
            base_xyz=(0, 0, 0),
            joint_limits=[(-180, 180), (-90, 90), (-90, 90), (-180, 180), (-90, 90), (-90, 90)],
            vmax=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            amax=[2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            tool_clearance=0.1
        )
        
        self.robot2 = RobotConfig(
            base_xyz=(1, 1, 0),
            joint_limits=[(-180, 180), (-90, 90), (-90, 90), (-180, 180), (-90, 90), (-90, 90)],
            vmax=[1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
            amax=[2.0, 2.0, 2.0, 2.0, 2.0, 2.0],
            tool_clearance=0.1
        )
        
        self.operations = [
            Operation(pick_xyz=(1, 1, 0), place_xyz=(2, 2, 1), t_hold=0.5),
            Operation(pick_xyz=(3, 1, 0), place_xyz=(4, 2, 1), t_hold=1.0)
        ]
        
        self.scenario = ScenarioTxt(
            robots=[self.robot1, self.robot2],
            safe_dist=0.5,
            operations=self.operations
        )
    
    def test_planner_algorithm(self):
        """Тест основного алгоритма планировщика"""
        plan = run_planner_algorithm(self.scenario)
        
        self.assertIsInstance(plan, dict)
        self.assertIn("robots", plan)
        self.assertIn("makespan", plan)
        self.assertIn("safe_dist", plan)
        
        self.assertEqual(len(plan["robots"]), 2)
        self.assertGreater(plan["makespan"], 0.0)
        self.assertEqual(plan["safe_dist"], 0.5)
        
        # Проверяем структуру роботов
        for robot_plan in plan["robots"]:
            self.assertIn("id", robot_plan)
            self.assertIn("trajectory", robot_plan)
            self.assertIn("base_xyz", robot_plan)
            self.assertIn("tool_clearance", robot_plan)
            
            # Проверяем траекторию
            trajectory = robot_plan["trajectory"]
            self.assertIsInstance(trajectory, list)
            self.assertGreater(len(trajectory), 0)
            
            # Проверяем структуру waypoints
            for wp in trajectory:
                self.assertIn("t", wp)
                self.assertIn("x", wp)
                self.assertIn("y", wp)
                self.assertIn("z", wp)


if __name__ == '__main__':
    unittest.main()
