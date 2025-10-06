import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
import sys
import math
from functools import partial
from itertools import islice
from dataclasses import dataclass, field
from typing import Any

from hw2_solution import PriorityQueueUpdatable

# https://docs.python.org/3/library/queue.html#queue.PriorityQueue
@dataclass(order=True)
class PItem:
    dist: int
    node: Any=field(compare=False)

    # Make the PItem hashable
    # https://docs.python.org/3/glossary.html#term-hashable
    def __hash__(self):
        return hash(self.node)

def euclidean_heurist_dist(node, goal, scale=1):
    x_n, y_n = node
    x_g, y_g = goal
    return scale*math.sqrt((x_n-x_g)**2 + (y_n - y_g)**2)

def backtrace_path(node2parent, start, goal):
    c = goal
    r_path = [c]
    parent = node2parent.get(c, None)
    while parent != start:
        r_path.append(parent)
        c = parent
        parent = node2parent.get(c, None) # Keep getting the parent until you reach the start
        #print(parent)
    r_path.append(start)
    return reversed(r_path) # Reverses the path

def astar(graph, heuristic_dist_fn, start, goal, debug=False, debugf=sys.stdout):
    """
    edgecost: cost of traversing each edge
    
    Returns success and node2parent
    
    success: True if goal is found otherwise False
    node2parent: A dictionary that contains the nearest parent for node 
    """
    seen = set([start]) # Set for seen nodes.
    # Frontier is the boundary between seen and unseen
    frontier = PriorityQueueUpdatable() # Frontier of unvisited nodes as a Priority Queue
    node2parent = {start : None} # Keep track of nearest parent for each node (requires node to be hashable)
    hfn = heuristic_dist_fn # make the name shorter
    node2dist = {start: 0  } # Keep track of cost to arrive at each node
    search_order = []
    frontier.put(PItem(0 + hfn(start, goal), start)) #   <------------- Different from dijkstra
    
    if debug: debugf.write("goal = "  + str(goal) + '\n')
    i = 0
    while not frontier.empty():          # Creating loop to visit each node
        dist_m = frontier.get() # Get the smallest addition to the frontier
        if debug: debugf.write("%d) Q = " % i + str(list(frontier.queue)) + '\n')
        if debug: debugf.write("%d) node = " % i + str(dist_m) + '\n')
        #if debug: print("dists = " , [node2dist[n.node] for n in frontier.queue])
        m = dist_m.node
        m_dist = node2dist[m]
        search_order.append(m)
        if goal is not None and m == goal:
            return True, search_order, node2parent, node2dist
        elif m.idx == goal.idx:
            assert False

        for neighbor, edge_cost in graph.get(m, []):
            old_dist = node2dist.get(neighbor, float("inf"))
            new_dist = edge_cost +  m_dist 
            if neighbor not in seen:
                seen.add(neighbor)
                frontier.put(PItem(new_dist +  hfn(neighbor, goal), neighbor)) # <------------- Different from dijkstra
                node2parent[neighbor] = m
                node2dist[neighbor] = new_dist
            elif new_dist < old_dist:
                node2parent[neighbor] = m
                node2dist[neighbor] = new_dist
                # ideally you would update the dist of this item in the priority queue
                # as well. But python priority queue does not support fast updates
                # ------------- Different from dijkstra --------------------
                old_item = PItem(old_dist + hfn(neighbor, goal), neighbor)
                if old_item in frontier:
                    frontier.replace(
                        old_item, 
                        PItem(new_dist + hfn(neighbor, goal), neighbor))
        i += 1
    if goal is not None:
        return False, search_order, node2parent, node2dist
    else:
        return True, search_order, node2parent, node2dist

# Skip these utilities for the class

def batched(iterable, n):
    "Batch data into tuples of length n. The last batch may be shorter."
    # batched('ABCDEFG', 3) --> ABC DEF G
    if n < 1:
        raise ValueError('n must be at least one')
    it = iter(iterable)
    while batch := tuple(islice(it, n)):
        yield batch

def draw_path(self, path, visited='*'):
    new_maze_lines = [list(l) for l in self.maze_lines]
    for (r, c) in path:
        new_maze_lines[r][c] = visited
        print('\n'.join([''.join(l) for l in new_maze_lines]))
        print('\n\n\n')

def init_plots(self, reinit=False):
    if self.fig is None or reinit:
        self.fig, self.ax = plt.subplots()

def plot_maze(self):
    self.init_plots()
    replace = { ' ' : 1, '+': 0}
    maze_mat = np.array([[replace[c] for c in line]
                          for line in self.maze_lines])
    return [self.ax.imshow(maze_mat, cmap='gray')]

def plot_step(self, i_node):
    i, (r, c) = i_node
    return [self.ax.text(c, r, '%d' % (i+1))]

def plot_path(self, path):
    self.plot_maze()
    return [self.plot_step((i, (r,c)))
            for i, (r, c) in enumerate(path)]

def animate_search_path(maze, search_path, node2dist):
    maze.init_plots()
    return animation.FuncAnimation(maze.fig, maze.plot_step, frames=[(node2dist[n], n)
                                                                      for n in search_path],
                                  init_func=maze.plot_maze, blit=True, repeat=False)

class Maze:
    def __init__(self, maze_str, freepath=' '):
        self.maze_lines = [l for l in maze_str.split("\n")
                           if len(l)]
        self.FREEPATH = freepath
        self.fig = None
        
    def get(self, node, default):
        (r, c) = node
        m_row = self.maze_lines[r]
        nbrs = []
        if c-1 >= 0 and m_row[c-1] == self.FREEPATH: 
            nbrs.append((r, c-1))
        if c+1 < len(m_row) and m_row[c+1] == self.FREEPATH: 
            nbrs.append((r, c+1))
        if r-1 >= 0 and self.maze_lines[r-1][c] == self.FREEPATH: 
            nbrs.append((r-1, c))
        if r+1 < len(self.maze_lines) and self.maze_lines[r+1][c] == self.FREEPATH: 
            nbrs.append((r+1, c))
        return nbrs if len(nbrs) else default
    init_plots = init_plots
    plot_maze = plot_maze
    plot_step = plot_step
    plot_path = plot_path
    animate_search_path = animate_search_path

    def get(self, node, default):
        (r, c) = node
        rmax = len(self.maze_lines)
        cmax = len(self.maze_lines[0])
        m_row = self.maze_lines[r]
        possible_nbrs = [
            ((r, c-1), 1),
            ((r, c+1), 1),
            ((r-1, c), 1),
            ((r+1, c), 1),
            ((r-1, c-1), math.sqrt(2)),
            ((r-1, c+1), math.sqrt(2)),
            ((r+1, c-1), math.sqrt(2)),
            ((r+1, c+1), math.sqrt(2))
        ]
        free_nbrs = []
        for (ri, ci), dist in possible_nbrs:
            if (ri >= 0 and ci >= 0 and ri < rmax and ci < cmax
                   and self.maze_lines[ri][ci] == self.FREEPATH):
                free_nbrs.append(((ri, ci), dist))
        return free_nbrs if len(free_nbrs) else default
    
    def _plot_path(self, path, char='+', color='c'):
        return [self.ax.text(c-0.5, r+0.5, char, color=color)
               for (r, c) in path]
    
    def plot_path(self, path, **kw):
        self.plot_maze()
        return self._plot_path(path, **kw)
    
    def animate(self, path, batch_size=200):
        self.init_plots()
        anim = animation.FuncAnimation(
                self.fig, self._plot_path, 
                frames=batched(search_path, batch_size),
                init_func=self.plot_maze, blit=True, repeat=False,
                save_count=5000
                )
        return anim

maze_str = \
"""
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                                      +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                   +                  +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+                  +                                      +
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
if __name__ == '__main__':
    start_pos, goal_pos = (35, 9), (5, 50)
    maze = Maze(maze_str)
    debugf=open('log.txt', 'w')
    success, search_path, node2parent, node2dist = astar(
        maze, partial(euclidean_heurist_dist, scale=1),
        start_pos, goal_pos, debug=True, debugf=debugf)
    debugf.close()

    #print(success, search_path)
    assert success
    anim = maze.animate(search_path)
    anim.save(filename='astar-anim.gif', writer='pillow')
    path = backtrace_path(node2parent, start_pos, goal_pos)
    #maze.init_plots(reinit=True)
    path_plot = maze.plot_path(path, color='r') # Draws the traced shortest path
    plt.savefig('astar-maze.pdf')
