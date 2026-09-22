"""재귀적 백트래킹(DFS) 방식의 미로 생성기.

grid[row][col] == 1 -> 벽, 0 -> 통로
cols, rows는 홀수를 사용해야 격자가 깔끔하게 맞물린다.
"""
import random


class MazeGenerator:
    def __init__(self, cols: int, rows: int):
        self.cols = cols if cols % 2 == 1 else cols + 1
        self.rows = rows if rows % 2 == 1 else rows + 1
        self.grid = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

    def generate(self):
        start = (1, 1)
        self.grid[start[1]][start[0]] = 0
        stack = [start]

        while stack:
            x, y = stack[-1]
            neighbors = self._unvisited_neighbors(x, y)

            if not neighbors:
                stack.pop()
                continue

            nx, ny = random.choice(neighbors)
            # 현재 칸과 이웃 칸 사이의 벽을 허문다
            wall_x, wall_y = (x + nx) // 2, (y + ny) // 2
            self.grid[wall_y][wall_x] = 0
            self.grid[ny][nx] = 0
            stack.append((nx, ny))

        return self.grid

    def _unvisited_neighbors(self, x: int, y: int):
        candidates = [(x, y - 2), (x, y + 2), (x - 2, y), (x + 2, y)]
        result = []
        for nx, ny in candidates:
            if 0 < nx < self.cols - 1 and 0 < ny < self.rows - 1:
                if self.grid[ny][nx] == 1:
                    result.append((nx, ny))
        return result
