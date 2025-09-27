#!/usr/bin/env python3
"""
Скрипт для оптимизации 3D модели руки робота
Уменьшает количество вершин и граней для лучшей производительности
"""

import os
import sys
import argparse
from typing import List, Tuple, Dict
import numpy as np

def load_obj(filepath: str) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
    """Загружает OBJ файл и возвращает вершины и грани"""
    vertices = []
    faces = []
    
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith('v '):
                parts = line.split()
                if len(parts) >= 4:
                    x = float(parts[1])
                    y = float(parts[2])
                    z = float(parts[3])
                    vertices.append((x, y, z))
            elif line.startswith('f '):
                parts = line.split()
                if len(parts) >= 4:
                    face_vertices = []
                    for part in parts[1:]:
                        # Обрабатываем формат v/vt/vn
                        vertex_idx = part.split('/')[0]
                        if vertex_idx.isdigit():
                            face_vertices.append(int(vertex_idx) - 1)  # OBJ индексы начинаются с 1
                    
                    if len(face_vertices) >= 3:
                        # Триангулируем полигоны
                        for i in range(1, len(face_vertices) - 1):
                            faces.append((face_vertices[0], face_vertices[i], face_vertices[i + 1]))
    
    return vertices, faces

def simplify_mesh(vertices: List[Tuple[float, float, float]], 
                 faces: List[Tuple[int, int, int]], 
                 target_vertices: int = 200) -> Tuple[List[Tuple[float, float, float]], List[Tuple[int, int, int]]]:
    """
    Упрощает меш, уменьшая количество вершин до target_vertices
    Использует простой алгоритм кластеризации
    """
    if len(vertices) <= target_vertices:
        return vertices, faces
    
    # Конвертируем в numpy для удобства
    verts_array = np.array(vertices)
    
    # Простая кластеризация по расстоянию
    clusters = []
    cluster_centers = []
    used_vertices = set()
    
    # Находим границы модели
    min_coords = np.min(verts_array, axis=0)
    max_coords = np.max(verts_array, axis=0)
    size = max_coords - min_coords
    
    # Создаем сетку кластеров
    grid_size = int(np.ceil(np.power(target_vertices, 1/3)))
    step = size / grid_size
    
    for i in range(grid_size):
        for j in range(grid_size):
            for k in range(grid_size):
                center = min_coords + np.array([i, j, k]) * step + step / 2
                cluster_centers.append(center)
                clusters.append([])
    
    # Распределяем вершины по кластерам
    for idx, vertex in enumerate(verts_array):
        # Находим ближайший кластер
        distances = np.linalg.norm(cluster_centers - vertex, axis=1)
        closest_cluster = np.argmin(distances)
        clusters[closest_cluster].append(idx)
    
    # Создаем новые вершины как центры кластеров
    new_vertices = []
    vertex_mapping = {}  # старое -> новое
    
    for cluster_idx, cluster in enumerate(clusters):
        if cluster:  # Если кластер не пустой
            # Вычисляем центр кластера
            cluster_verts = verts_array[cluster]
            center = np.mean(cluster_verts, axis=0)
            new_vertex_idx = len(new_vertices)
            new_vertices.append(tuple(center))
            
            # Создаем маппинг
            for old_idx in cluster:
                vertex_mapping[old_idx] = new_vertex_idx
    
    # Создаем новые грани
    new_faces = []
    for face in faces:
        new_face = []
        for vertex_idx in face:
            if vertex_idx in vertex_mapping:
                new_face.append(vertex_mapping[vertex_idx])
        
        # Проверяем, что грань валидна (все вершины разные)
        if len(set(new_face)) == 3:
            new_faces.append(tuple(new_face))
    
    return new_vertices, new_faces

def create_hand_definition(vertices: List[Tuple[float, float, float]], 
                          faces: List[Tuple[int, int, int]]) -> str:
    """
    Создает упрощенное описание руки для визуализации
    Возвращает строку в формате, понятном load_hand_definition
    """
    lines = ["# Simplified hand definition for ROBOTY"]
    lines.append(f"# {len(vertices)} vertices, {len(faces)} faces")
    lines.append("")
    
    # Записываем вершины
    for vertex in vertices:
        lines.append(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}")
    
    lines.append("")
    
    # Создаем сегменты из граней (только рёбра)
    edges = set()
    for face in faces:
        for i in range(3):
            edge = tuple(sorted([face[i], face[(i+1)%3]]))
            edges.add(edge)
    
    # Группируем рёбра в полилинии (упрощенно)
    for edge in sorted(edges):
        lines.append(f"l {edge[0]+1} {edge[1]+1}")
    
    return "\n".join(lines)

def save_obj(vertices: List[Tuple[float, float, float]], 
             faces: List[Tuple[int, int, int]], 
             filepath: str, 
             comment: str = ""):
    """Сохраняет меш в OBJ файл"""
    with open(filepath, 'w', encoding='utf-8') as f:
        if comment:
            f.write(f"# {comment}\n")
        f.write(f"# Optimized hand model: {len(vertices)} vertices, {len(faces)} faces\n")
        f.write("o Hand_Optimized\n\n")
        
        # Записываем вершины
        for vertex in vertices:
            f.write(f"v {vertex[0]:.6f} {vertex[1]:.6f} {vertex[2]:.6f}\n")
        
        f.write("\n")
        
        # Записываем грани
        for face in faces:
            f.write(f"f {face[0]+1} {face[1]+1} {face[2]+1}\n")

def main():
    parser = argparse.ArgumentParser(description='Оптимизация 3D модели руки робота')
    parser.add_argument('input_file', help='Путь к исходному OBJ файлу')
    parser.add_argument('--output', '-o', default='hand_optimized.obj', help='Путь к выходному файлу')
    parser.add_argument('--vertices', '-v', type=int, default=200, help='Целевое количество вершин')
    parser.add_argument('--hand-def', action='store_true', help='Создать также файл hand definition')
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_file):
        print(f"Ошибка: файл {args.input_file} не найден")
        sys.exit(1)
    
    print(f"Загружаем модель из {args.input_file}...")
    vertices, faces = load_obj(args.input_file)
    print(f"Исходная модель: {len(vertices)} вершин, {len(faces)} граней")
    
    if len(vertices) <= args.vertices:
        print(f"Модель уже достаточно простая ({len(vertices)} вершин)")
        new_vertices, new_faces = vertices, faces
    else:
        print(f"Упрощаем до {args.vertices} вершин...")
        new_vertices, new_faces = simplify_mesh(vertices, faces, args.vertices)
        print(f"Упрощенная модель: {len(new_vertices)} вершин, {len(new_faces)} граней")
    
    # Сохраняем оптимизированную модель
    save_obj(new_vertices, new_faces, args.output, 
             f"Optimized from {args.input_file}")
    print(f"Сохранено в {args.output}")
    
    # Создаем hand definition если нужно
    if args.hand_def:
        hand_def_content = create_hand_definition(new_vertices, new_faces)
        hand_def_path = args.output.replace('.obj', '_hand_def.txt')
        with open(hand_def_path, 'w', encoding='utf-8') as f:
            f.write(hand_def_content)
        print(f"Hand definition сохранен в {hand_def_path}")

if __name__ == "__main__":
    main()
