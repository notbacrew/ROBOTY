import math

def distance(p1, p2):
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

def check_collision(waypoints, tool_clearance, safe_dist):
    for t in range(max(len(wp) for wp in waypoints)):
        positions = []
        for wp in waypoints:
            if t < len(wp):
                positions.append(wp[t]['pos'])
        for i in range(len(positions)):
            for j in range(i + 1, len(positions)):
                d = distance(positions[i], positions[j])
                if d < safe_dist:
                    return False
    return True

# Unit-test
def test_check_collision():
    wp = [
        [{'pos': (0,0,0)}, {'pos': (100,0,0)}],
        [{'pos': (0,100,0)}, {'pos': (100,100,0)}]
    ]
    assert check_collision(wp, 50, 50) == True
    wp2 = [
        [{'pos': (0,0,0)}, {'pos': (10,0,0)}],
        [{'pos': (0,10,0)}, {'pos': (10,10,0)}]
    ]
    assert check_collision(wp2, 50, 5) == False
    print("Collision tests passed.")

if __name__ == "__main__":
    test_check_collision()
