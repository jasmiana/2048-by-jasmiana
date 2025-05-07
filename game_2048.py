import tkinter as tk
import random
import colors as c
from tkinter import messagebox

class Game2048:
    def __init__(self, master):
        self.master = master
        self.master.title("jasmiana's 2048")
        self.master.geometry("400x600")
        self.master.resizable(0, 0)
        self.master.config(bg=c.GRID_COLOR)
        
        self.main_frame = tk.Frame(self.master, bg=c.GRID_COLOR)
        self.main_frame.pack(pady=20)
        
        self.score_frame = tk.Frame(self.master, bg=c.GRID_COLOR)
        self.score_frame.pack()
        
        self.score_label = tk.Label(
            self.score_frame, 
            text="分数", 
            font=("Microsoft Yahei", 18, "bold"),
            bg=c.GRID_COLOR,
            fg=c.CELL_NUMBER_COLORS[8]
        )
        self.score_label.grid(row=0, column=0, padx=5)
        
        self.score_value = tk.Label(
            self.score_frame, 
            text="0", 
            font=("Microsoft Yahei", 18, "bold"),
            bg=c.GRID_COLOR,
            fg=c.CELL_NUMBER_COLORS[16]
        )
        self.score_value.grid(row=0, column=1, padx=5)
        
        self.button_frame = tk.Frame(self.master, bg=c.GRID_COLOR)
        self.button_frame.pack(pady=10)
        
        self.new_game_button = tk.Button(
            self.button_frame,
            text="新游戏",
            font=("Microsoft Yahei", 12),
            command=self.new_game
        )
        self.new_game_button.grid(row=0, column=0, padx=5)
        
        self.undo_button = tk.Button(
            self.button_frame,
            text="撤回",
            font=("Microsoft Yahei", 12),
            command=self.undo_move,
            state=tk.DISABLED
        )
        self.undo_button.grid(row=0, column=1, padx=5)
        
        self.instruction_label = tk.Label(
            self.master,
            text="使用方向键或WASD控制移动",
            font=("Microsoft Yahei", 10),
            bg=c.GRID_COLOR,
            fg=c.CELL_NUMBER_COLORS[8]
        )
        self.instruction_label.pack(pady=5)
        
        self.cells = []
        for i in range(4):
            row = []
            for j in range(4):
                cell_frame = tk.Frame(
                    self.main_frame,
                    bg=c.EMPTY_CELL_COLOR,
                    width=80,
                    height=80
                )
                cell_frame.grid(row=i, column=j, padx=5, pady=5)
                cell_frame.grid_propagate(False)
                cell_number = tk.Label(
                    cell_frame,
                    bg=c.EMPTY_CELL_COLOR,
                    font=("Microsoft Yahei", 24, "bold"),
                    justify="center",
                    width=80,
                    height=80
                )
                cell_number.place(relx=0.5, rely=0.5, anchor="center")
                row.append(cell_number)
            self.cells.append(row)
            
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.history = []
        
        self.master.bind("<Left>", lambda event: self.move("left"))
        self.master.bind("<Right>", lambda event: self.move("right"))
        self.master.bind("<Up>", lambda event: self.move("up"))
        self.master.bind("<Down>", lambda event: self.move("down"))
        
        self.master.bind("<a>", lambda event: self.move("left"))
        self.master.bind("<d>", lambda event: self.move("right"))
        self.master.bind("<w>", lambda event: self.move("up"))
        self.master.bind("<s>", lambda event: self.move("down"))

        self.end_flag = False

        self.new_game()
    
    def new_game(self):
        """开始新的游戏"""
        # Reset
        self.grid = [[0 for _ in range(4)] for _ in range(4)]
        self.score = 0
        self.score_value.config(text="0")
        self.history = []
        self.undo_button.config(state=tk.DISABLED)
        
        # Generate 2 random tiles
        self.generate_new_tile()
        self.generate_new_tile()
        
        self.update_display()
    
    def undo_move(self):
        """撤回上一步操作"""
        if self.history:
            last_state = self.history.pop()
            self.grid = last_state["grid"]
            self.score = last_state["score"]
            self.score_value.config(text=str(self.score))
            self.update_display()
            
            if not self.history:
                self.undo_button.config(state=tk.DISABLED)
        
    def generate_new_tile(self):
        """在空位置随机生成一个新的数字（2或4）"""
        empty_cells = []
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    empty_cells.append((i, j))
        
        if empty_cells:
            i, j = random.choice(empty_cells)
            self.grid[i][j] = 2 if random.random() < 0.9 else 4
            return True
        return False
    
    def update_display(self):
        """更新界面显示"""
        for i in range(4):
            for j in range(4):
                value = self.grid[i][j]
                if value == 0:
                    self.cells[i][j].config(
                        text="",
                        bg=c.EMPTY_CELL_COLOR
                    )
                else:
                    self.cells[i][j].config(bg=c.CELL_COLORS.get(value, c.CELL_COLORS[8192]))
                    font_size = 24
                    if value > 512:
                        font_size = 18
                    if value > 1024:
                        font_size = 16
                    
                    self.cells[i][j].config(
                        text=str(value),
                        fg=c.CELL_NUMBER_COLORS.get(value, c.CELL_NUMBER_COLORS[8192]),
                        font=("Microsoft Yahei", font_size, "bold")
                    )
    
    def animate_move(self, from_pos, to_pos):
        """平滑移动动画"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        cell = self.cells[from_x][from_y]
        
        original_color = cell.cget("bg")
        
        def move_animation(step):
            if step < 10:
                x_offset = (to_x - from_x) * step / 10
                y_offset = (to_y - from_y) * step / 10
                
                cell.place(x=cell.winfo_x() + x_offset, y=cell.winfo_y() + y_offset)
                self.master.after(50, move_animation, step + 1)
            else:
                self.update_display()
        
        move_animation(0)
    
    def combine_animation(self, pos):
        """合成动画"""
        x, y = pos
        cell = self.cells[x][y]
        
        def enlarge():
            # Color after combining
            cell.config(bg=c.CELL_COLORS[2048])
            cell.place(relwidth=1.2, relheight=1.2)
            self.master.after(100, shrink)

        def shrink():
            # Restore original size
            cell.place(relwidth=1, relheight=1)
            self.update_display()

        enlarge()
    
    def stack(self, grid=None):
        """将所有非零元素向移动方向堆叠"""
        if grid is None:
            grid = self.grid
            
        new_grid = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            position = 0
            for j in range(4):
                if grid[i][j] != 0:
                    new_grid[i][position] = grid[i][j]
                    if position != j:
                        self.moved = True
                    position += 1
        return new_grid

    def combine(self, grid=None, simulate=False):
        if grid is None:
            grid = self.grid

        for i in range(4):
            for j in range(3):
                if grid[i][j] != 0 and grid[i][j] == grid[i][j + 1]:
                    if not simulate:
                        self.score += grid[i][j]
                        self.score_value.config(text=str(self.score))
                    grid[i][j] *= 2
                    grid[i][j + 1] = 0
                    self.moved = True
        return grid

    def reverse(self, grid=None):
        """翻转网格（用于向右移动）"""
        if grid is None:
            grid = self.grid
            
        new_grid = []
        for i in range(4):
            new_grid.append([])
            for j in range(4):
                new_grid[i].append(grid[i][3-j])
        return new_grid
    
    def transpose(self, grid=None):
        """转置网格（用于上下移动）"""
        if grid is None:
            grid = self.grid
            
        new_grid = [[0 for _ in range(4)] for _ in range(4)]
        for i in range(4):
            for j in range(4):
                new_grid[i][j] = grid[j][i]
        return new_grid

    def move_left(self, grid=None, simulate=False):
        if grid is None:
            grid = self.grid

        grid = self.stack(grid)
        grid = self.combine(grid, simulate=simulate)
        grid = self.stack(grid)
        return grid

    def move_right(self, grid=None, simulate=False):
        if grid is None:
            grid = self.grid

        grid = self.reverse(grid)
        grid = self.move_left(grid, simulate=simulate)
        grid = self.reverse(grid)
        return grid

    def move_up(self, grid=None, simulate=False):
        if grid is None:
            grid = self.grid

        grid = self.transpose(grid)
        grid = self.move_left(grid, simulate=simulate)
        grid = self.transpose(grid)
        return grid

    def move_down(self, grid=None, simulate=False):
        if grid is None:
            grid = self.grid

        grid = self.transpose(grid)
        grid = self.move_right(grid, simulate=simulate)
        grid = self.transpose(grid)
        return grid

    def can_move(self, direction=None):
        """检查是否还能移动"""
        # Empty -> Could move
        has_empty = False
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 0:
                    has_empty = True
        
        # Adjacent, same number
        has_same_neighbors = False
        # Check horizontally
        for i in range(4):
            for j in range(3):
                if self.grid[i][j] == self.grid[i][j+1] and self.grid[i][j] != 0:
                    has_same_neighbors = True
        
        # Check vertically
        for i in range(3):
            for j in range(4):
                if self.grid[i][j] == self.grid[i+1][j] and self.grid[i][j] != 0:
                    has_same_neighbors = True
        
        # Movable through specific direction
        if direction:
            # Copy a grid for testing
            test_grid = [row[:] for row in self.grid]
            
            if direction == "left":
                new_grid = self.move_left(test_grid)
            elif direction == "right":
                new_grid = self.move_right(test_grid)
            elif direction == "up":
                new_grid = self.move_up(test_grid)
            elif direction == "down":
                new_grid = self.move_down(test_grid)
                
            # Changes occurred -> Could move
            return new_grid != self.grid
            
        return has_empty or has_same_neighbors
    
    def check_win(self):
        """检查是否胜利"""
        for i in range(4):
            for j in range(4):
                if self.grid[i][j] == 2048:
                    return True
        return False
    
    '''
    def animate_move(self, from_pos, to_pos):
        """平滑移动动画"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        cell = self.cells[from_x][from_y]
        
        # 动画函数
        def move_animation(step):
            if step < 10:
                # 计算移动的偏移量
                x_offset = (to_x - from_x) * step / 10
                y_offset = (to_y - from_y) * step / 10
                
                # 更新位置
                cell.place(x=cell.winfo_x() + x_offset, y=cell.winfo_y() + y_offset)
                self.master.after(50, move_animation, step + 1)
            else:
                # 动画结束后更新格子
                self.update_display()
        
        move_animation(0)
    '''
    
    def move(self, direction):
        """根据方向移动方块"""
        self.moved = False
        
        if not self.can_move(direction):
            return
            
        # Save current state for undo
        self.history.append({
            "grid": [row[:] for row in self.grid],
            "score": self.score
        })
        self.undo_button.config(state=tk.NORMAL)
            
        if direction == "left":
            self.grid = self.move_left()
        elif direction == "right":
            self.grid = self.move_right()
        elif direction == "up":
            self.grid = self.move_up()
        elif direction == "down":
            self.grid = self.move_down()
        
        if self.moved:
            self.generate_new_tile()
            self.update_display()

            if self.check_win() and self.end_flag == False:
                self.end_flag = True
                self.update_display()
                answer = messagebox.showinfo("恭喜！", "你赢了！\n要继续游戏吗？")
                if not answer:
                    self.master.quit()
            
            elif not self.can_move():
                self.update_display()
                messagebox.showinfo("游戏结束", f"游戏结束！最终分数：{self.score}")


if __name__ == "__main__":
    root = tk.Tk()
    game = Game2048(root)
    root.mainloop() 
