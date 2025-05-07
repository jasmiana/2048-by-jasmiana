import tkinter as tk
import time
import copy
from game_2048 import Game2048


class AI2048:
    def __init__(self, game):
        self.game = game
        self.directions = ["up", "right", "down", "left"]

        self.control_frame = tk.Frame(self.game.master, bg=self.game.master.cget('bg'))
        self.control_frame.pack(pady=5)

        self.start_button = tk.Button(
            self.control_frame,
            text="启动AI",
            font=("Microsoft Yahei", 12),
            command=self.start_ai
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.stop_button = tk.Button(
            self.control_frame,
            text="停止AI",
            font=("Microsoft Yahei", 12),
            command=self.stop_ai,
            state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5)

        self.is_running = False
        self.move_delay = 20  # Move delay (ms)

        # Weights
        self.weight_matrix = [
            [2 ** 3, 2 ** 2, 2 ** 1, 2 ** 0],
            [2 ** 4, 2 ** 5, 2 ** 6, 2 ** 7],
            [2 ** 11, 2 ** 10, 2 ** 9, 2 ** 8],
            [2 ** 12, 2 ** 13, 2 ** 14, 2 ** 15],
        ]

    def evaluate_position(self, grid):
        """评估当前局面分数 - 这是AI用来选择最佳移动的评分，不是游戏分数"""
        score = 0
        empty_cells = 0
        max_tile = 0
        merges = 0

        # Positional Weight
        for i in range(4):
            for j in range(4):
                if grid[i][j] == 0:
                    empty_cells += 1
                else:
                    # 基础位置得分
                    score += grid[i][j] * self.weight_matrix[i][j]
                    max_tile = max(max_tile, grid[i][j])

        # Check possible merges
        for i in range(4):
            for j in range(3):
                # Merge horizontally
                if grid[i][j] != 0 and grid[i][j] == grid[i][j + 1]:
                    merges += 1
                # Merge vertically
                if grid[j][i] != 0 and grid[j][i] == grid[j + 1][i]:
                    merges += 1

        # Smoothness Score: Variance of adjacent numbers
        smoothness = 0
        for i in range(4):
            for j in range(4):
                if grid[i][j] != 0:
                    # Right Check
                    if j < 3 and grid[i][j + 1] != 0:
                        smoothness -= abs(grid[i][j] - grid[i][j + 1])
                    # Bottom Check
                    if i < 3 and grid[i + 1][j] != 0:
                        smoothness -= abs(grid[i][j] - grid[i + 1][j])

        monotonicity = 0
        # Check Monotonicity for Each Row
        for i in range(4):
            current_row = [x if x != 0 else float('-inf') for x in grid[i]]
            if all(current_row[j] >= current_row[j + 1] for j in range(3)):
                monotonicity += sum(x for x in current_row if x != float('-inf'))

        # Check Monotonicity for Each Column
        for j in range(4):
            current_col = [grid[i][j] if grid[i][j] != 0 else float('-inf') for i in range(4)]
            if all(current_col[i] >= current_col[i + 1] for i in range(3)):
                monotonicity += sum(x for x in current_col if x != float('-inf'))

        # Overall Evaluation Score
        final_score = (
                score * 1.0 +
                empty_cells * 2000.0 +
                merges * 800.0 +
                smoothness * 100.0 +
                monotonicity * 2.0 +
                (max_tile ** 2) * 1.0
        )

        return final_score

    def simulate_move(self, grid, direction):
        new_grid = [row[:] for row in grid]
        if direction == "left":
            new_grid = self.game.move_left(new_grid, simulate=True)
        elif direction == "right":
            new_grid = self.game.move_right(new_grid, simulate=True)
        elif direction == "up":
            new_grid = self.game.move_up(new_grid, simulate=True)
        else:
            new_grid = self.game.move_down(new_grid, simulate=True)

        return new_grid, new_grid != grid

    def get_empty_cells(self, grid):
        """获取空格子的位置"""
        empty_cells = []
        for i in range(4):
            for j in range(4):
                if grid[i][j] == 0:
                    empty_cells.append((i, j))
        return empty_cells

    def expectimax(self, grid, depth, is_max):
        """使用Expectimax算法进行搜索"""
        if depth == 0:
            return self.evaluate_position(grid)

        if is_max:
            max_score = float('-inf')
            for direction in self.directions:
                new_grid, moved = self.simulate_move(grid, direction)
                if moved:
                    score = self.expectimax(new_grid, depth - 1, False)
                    max_score = max(max_score, score)
            return max_score if max_score != float('-inf') else self.evaluate_position(grid)
        else:
            empty_cells = self.get_empty_cells(grid)
            if not empty_cells:
                return self.evaluate_position(grid)

            avg_score = 0
            possibilities = len(empty_cells)

            for i, j in empty_cells:
                grid_with_2 = [row[:] for row in grid]
                grid_with_4 = [row[:] for row in grid]
                grid_with_2[i][j] = 2
                grid_with_4[i][j] = 4

                score = (0.9 * self.expectimax(grid_with_2, depth - 1, True) +
                         0.1 * self.expectimax(grid_with_4, depth - 1, True))
                avg_score += score / possibilities

            return avg_score

    def alpha_beta(self, grid, depth, is_max, alpha=float('-inf'), beta=float('inf')):
        """使用Expectimax算法和Alpha-Beta剪枝进行搜索"""
        if depth == 0 or not self.get_empty_cells(grid):
            return self.evaluate_position(grid)

        if is_max:
            max_score = float('-inf')
            for direction in self.directions:
                new_grid, moved = self.simulate_move(grid, direction)
                if moved:
                    score = self.alpha_beta(new_grid, depth - 1, False, alpha, beta)
                    max_score = max(max_score, score)
                    alpha = max(alpha, score)
                    if beta <= alpha:
                        break
            return max_score if max_score != float('-inf') else self.evaluate_position(grid)
        else:
            avg_score = 0
            empty_cells = self.get_empty_cells(grid)
            possibilities = len(empty_cells)

            for i, j in empty_cells:
                grid_with_2 = [row[:] for row in grid]
                grid_with_4 = [row[:] for row in grid]
                grid_with_2[i][j] = 2
                grid_with_4[i][j] = 4

                score = (0.9 * self.alpha_beta(grid_with_2, depth - 1, True, alpha, beta) +
                        0.1 * self.alpha_beta(grid_with_4, depth - 1, True, alpha, beta))
                avg_score += score / possibilities

                beta = min(beta, avg_score)
                if beta <= alpha:
                    break

            return avg_score

    def get_best_move(self):
        """获取最佳移动方向"""
        best_score = float('-inf')
        best_direction = None

        # Evaluate every possible direction
        for direction in self.directions:
            new_grid, moved = self.simulate_move(self.game.grid, direction)
            if moved:
                # Evaluate by expectimax
                score = self.expectimax(new_grid, depth=3, is_max=False)
                if score > best_score:
                    best_score = score
                    best_direction = direction

        return best_direction

    def make_move(self):
        """执行一步AI移动"""
        if not self.is_running:
            return

        direction = self.get_best_move()

        if direction:
            self.game.move(direction)

            if not self.game.can_move():
                self.stop_ai()
                return

            self.game.master.after(self.move_delay, self.make_move)

    def start_ai(self):
        """启动AI"""
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.make_move()

    def stop_ai(self):
        """停止AI"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)


def main():
    root = tk.Tk()
    game = Game2048(root)
    ai = AI2048(game)
    root.mainloop()


if __name__ == "__main__":
    main()