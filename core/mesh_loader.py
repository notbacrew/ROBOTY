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


