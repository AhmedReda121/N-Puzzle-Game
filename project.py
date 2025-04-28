import tkinter as tk
import tkinter.messagebox
import random
import heapq

class NPuzzle:
    def __init__(self, master, size=3, shuffle_moves=100):
        self.master = master
        self.size = size
        self.shuffle_moves = shuffle_moves
        self.tiles = []
        self.buttons = []
        self.moves = 0

        # Configure root window
        master.title("N-Puzzle (8-Puzzle) with A*")
        master.geometry("600x700")
        master.configure(bg="#1e1e2e")

        # Title label
        title = tk.Label(
            master,
            text="8-Puzzle Challenge",
            font=("Helvetica", 24, "bold"),
            bg="#1e1e2e",
            fg="#ffffff"
        )
        title.pack(pady=(20, 0))

        # Frame for puzzle tiles
        self.frame = tk.Frame(master, bg="#28293d")
        self.frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Control panel
        ctrl = tk.Frame(master, bg="#1e1e2e")
        ctrl.pack(pady=(0, 20))

        self.move_label = tk.Label(
            ctrl,
            text=f"Moves: {self.moves}",
            font=("Helvetica", 16),
            bg="#1e1e2e",
            fg="#ffffff"
        )
        self.move_label.grid(row=0, column=0, padx=15)

        btn_style = {
            "font": ("Helvetica", 14, "bold"),
            "width": 10,
            "height": 2,
            "bg": "#ff7597",
            "fg": "#ffffff",
            "activebackground": "#ff4564",
            "bd": 0,
            "relief": "flat"
        }
        tk.Button(ctrl, text="Shuffle", command=self.shuffle, **btn_style).grid(row=0, column=1, padx=5)
        tk.Button(ctrl, text="Reset", command=self.reset, **btn_style).grid(row=0, column=2, padx=5)
        tk.Button(ctrl, text="Solve", command=self.solve, **btn_style).grid(row=0, column=3, padx=5)

        self.reset()

    def update_move_label(self):
        self.move_label.config(text=f"Moves: {self.moves}")

    def reset(self):
        self.tiles = list(range(1, self.size*self.size)) + [0]
        self.moves = 0
        self.update_move_label()
        self.draw()

    def shuffle(self):
        for _ in range(self.shuffle_moves):
            zero_idx = self.tiles.index(0)
            z_r, z_c = divmod(zero_idx, self.size)
            neighbors = [
                (r, c)
                for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]
                for r, c in [(z_r+dr, z_c+dc)]
                if 0 <= r < self.size and 0 <= c < self.size
            ]
            if neighbors:
                r, c = random.choice(neighbors)
                ni = r*self.size + c
                self.tiles[zero_idx], self.tiles[ni] = self.tiles[ni], self.tiles[zero_idx]
        self.moves = 0
        self.update_move_label()
        self.draw()

    def draw(self):
        for btn in self.buttons:
            btn.destroy()
        self.buttons = []

        for i, val in enumerate(self.tiles):
            r, c = divmod(i, self.size)
            text = str(val) if val != 0 else ""
            color = "#4d5bce" if val != 0 else "#28293d"
            btn = tk.Button(
                self.frame,
                text=text,
                font=("Helvetica", 26, "bold"),
                bd=0,
                relief="flat",
                highlightthickness=0,
                width=4,
                height=2,
                bg=color,
                fg="#ffffff",
                activebackground="#6c5ce7",
                command=lambda idx=i: self.on_tile_click(idx)
            )
            btn.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self.buttons.append(btn)

        # Make grid cells expand evenly
        for i in range(self.size):
            self.frame.grid_rowconfigure(i, weight=1)
            self.frame.grid_columnconfigure(i, weight=1)

    def on_tile_click(self, index):
        zero_idx = self.tiles.index(0)
        if self.can_swap(zero_idx, index):
            self.tiles[zero_idx], self.tiles[index] = self.tiles[index], self.tiles[zero_idx]
            self.moves += 1
            self.update_move_label()
            self.draw()
            if self.is_solved():
                tk.messagebox.showinfo("Solved!", f"Solved in {self.moves} moves.")

    def can_swap(self, z, i):
        zr, zc = divmod(z, self.size)
        ir, ic = divmod(i, self.size)
        return abs(zr - ir) + abs(zc - ic) == 1

    def is_solved(self):
        return self.tiles == list(range(1, self.size*self.size)) + [0]

    def solve(self):
        start = tuple(self.tiles)
        goal = tuple(list(range(1, self.size*self.size)) + [0])
        path = self.a_star(start, goal)
        if not path:
            tk.messagebox.showwarning("No solution", "No solution found.")
            return
        self.moves = 0
        self.update_move_label()
        self.animate_solution(path[1:])

    def heuristic(self, state):
        dist = 0
        for idx, val in enumerate(state):
            if val != 0:
                r1, c1 = divmod(idx, self.size)
                r2, c2 = divmod(val-1, self.size)
                dist += abs(r1-r2) + abs(c1-c2)
        return dist

    def a_star(self, start, goal):
        frontier = [(self.heuristic(start), 0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            _, cost, current = heapq.heappop(frontier)
            if current == goal:
                break
            zero_idx = current.index(0)
            zr, zc = divmod(zero_idx, self.size)
            for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
                r, c = zr+dr, zc+dc
                if 0 <= r < self.size and 0 <= c < self.size:
                    ni = r*self.size + c
                    new_state = list(current)
                    new_state[zero_idx], new_state[ni] = new_state[ni], new_state[zero_idx]
                    new_tuple = tuple(new_state)
                    new_cost = cost_so_far[current] + 1
                    if new_tuple not in cost_so_far or new_cost < cost_so_far[new_tuple]:
                        cost_so_far[new_tuple] = new_cost
                        heapq.heappush(frontier, (new_cost + self.heuristic(new_tuple), new_cost, new_tuple))
                        came_from[new_tuple] = current
        if goal not in came_from:
            return None
        path, node = [], goal
        while node:
            path.append(node)
            node = came_from[node]
        path.reverse()
        return path

    def animate_solution(self, states):
        if not states:
            tk.messagebox.showinfo("Solved!", f"Autosolve completed in {self.moves} moves.")
            return
        next_state = states.pop(0)
        self.tiles = list(next_state)
        self.moves += 1
        self.update_move_label()
        self.draw()
        self.master.after(200, lambda: self.animate_solution(states))

if __name__ == '__main__':
    root = tk.Tk()
    app = NPuzzle(root, size=3, shuffle_moves=50)
    root.mainloop()