import os
import logging
from typing import List, Tuple, Optional


logger = logging.getLogger("ROBOTY.mesh_loader")


def load_obj(filepath: str, scale: float = 1.0) -> Optional[Tuple[List[float], List[float], List[float], List[int], List[int], List[int]]]:
    """
    Простейший загрузчик OBJ (только v и f с треугольниками),
    возвращает вершины (x,y,z) и индексы (i,j,k) для Mesh3d.
    """
    try:
        if not os.path.isfile(filepath):
            logger.warning(f"OBJ файл не найден: {filepath}")
            return None
        vertices: List[Tuple[float, float, float]] = []
        faces: List[Tuple[int, int, int]] = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('v '):
                    parts = line.split()
                    if len(parts) >= 4:
                        x = float(parts[1]) * scale
                        y = float(parts[2]) * scale
                        z = float(parts[3]) * scale
                        vertices.append((x, y, z))
                elif line.startswith('f '):
                    parts = line.split()
                    idxs = []
                    for p in parts[1:]:
                        # f v / vt / vn
                        s = p.split('/')
                        if s[0]:
                            idx = int(s[0])
                            if idx < 0:
                                idx = len(vertices) + 1 + idx
                            idxs.append(idx - 1)
                    # Триангулируем полигоны >3
                    for i in range(1, len(idxs) - 1):
                        faces.append((idxs[0], idxs[i], idxs[i + 1]))
        if not vertices or not faces:
            logger.warning(f"OBJ пуст или невалиден: {filepath}")
            return None
        xs = [v[0] for v in vertices]
        ys = [v[1] for v in vertices]
        zs = [v[2] for v in vertices]
        is_ = [f[0] for f in faces]
        js_ = [f[1] for f in faces]
        ks_ = [f[2] for f in faces]
        logger.info(f"OBJ загружен: {filepath}, вершин={len(vertices)}, треугольников={len(faces)}")
        return xs, ys, zs, is_, js_, ks_
    except Exception as e:
        logger.error(f"Ошибка чтения OBJ {filepath}: {e}")
        return None



def load_hand_definition(filepath: str, scale: float = 1.0) -> Optional[dict]:
    """
    Загружает упрощённое описание руки из произвольного текстового файла
    (подобного OBJ), где присутствуют:
      - v x y z — вершины
      - l i j k ... — полилинии (индексы вершин)
      - p i j k ... — набор точек (например, шарниры)

    Возвращает словарь:
      { 'vertices': [(x,y,z), ...], 'segments': [ (i1, i2), ... ], 'points': [i, ...] }
    Индексы конвертируются в пары сегментов по соседним вершинам линии.
    Масштаб применяется к координатам.
    """
    try:
        if not os.path.isfile(filepath):
            logger.warning(f"Файл определения руки не найден: {filepath}")
            return None
        vertices: List[Tuple[float, float, float]] = []
        polylines: List[List[int]] = []
        points: List[int] = []
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for raw in f:
                line = raw.strip()
                if not line or line.startswith('#'):
                    continue
                if line.startswith('v '):
                    parts = line.split()
                    if len(parts) >= 4:
                        x = float(parts[1]) * scale
                        y = float(parts[2]) * scale
                        z = float(parts[3]) * scale
                        vertices.append((x, y, z))
                elif line.startswith('l '):
                    parts = line.split()
                    idxs: List[int] = []
                    for p in parts[1:]:
                        # поддержка v/vt формы: берём первую часть
                        s = p.split('/')
                        if s[0]:
                            idx = int(s[0])
                            if idx < 0:
                                idx = len(vertices) + 1 + idx
                            idxs.append(idx - 1)
                    if len(idxs) >= 2:
                        polylines.append(idxs)
                elif line.startswith('p '):
                    parts = line.split()
                    for p in parts[1:]:
                        if p.isdigit() or (p.startswith('-') and p[1:].isdigit()):
                            idx = int(p)
                            if idx < 0:
                                idx = len(vertices) + 1 + idx
                            points.append(idx - 1)
        # Строим сегменты
        segments: List[Tuple[int, int]] = []
        for poly in polylines:
            for a, b in zip(poly[:-1], poly[1:]):
                segments.append((a, b))
        logger.info(f"Hand definition загружен: {filepath}, вершин={len(vertices)}, сегментов={len(segments)}, точек={len(points)}")
        return { 'vertices': vertices, 'segments': segments, 'points': points }
    except Exception as e:
        logger.error(f"Ошибка чтения hand definition {filepath}: {e}")
        return None
