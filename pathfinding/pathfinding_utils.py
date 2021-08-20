import heapq
import pygame
import random

"""----------------------Pathfinder Utils------------------------------------"""


def read_file_pathfinder(diagonals):
    """
        creates a 2d array of PathNodes and a graph of all positions and their
        links. It also returns the start and end nodes after updating each node
        with its distance to the end
    """
    file_name = 'maze.txt'
    graph = {}
    nodes = []

    with open(file_name) as file:
        lines = file.readlines()
        for row in range(len(lines)):
            line = lines[row].strip('\n')
            node_row = []

            for col in range(len(line)):
                character = line[col]

                if character == '#':
                    node_row.append(None)
                    continue

                # updating start and end node positions
                pos = (row, col)
                node_row.append(PathNode(row, col))

                # adds paths to the graph
                graph = add_adj_to_graph(graph, pos, lines, diagonals)

            nodes.append(node_row)

        wid = len(nodes[0])
        hei = len(nodes)

        while True:
            start_col = end_col = random.randint(0, wid-1)
            start_row = end_row = random.randint(0, hei-1)
            if lines[start_row][start_col] == ' ':
                break

        min_dist = min(wid, hei)/2
        cur_dist = 0
        while cur_dist < min_dist:
            start_col = random.randint(0, wid-1)
            start_row = random.randint(0, hei-1)
            if lines[start_row][start_col] == '#':
                continue
            cur_dist = abs(start_row - end_row) + abs(start_col - end_col)

        for line in nodes:
            for node in line:
                if node is not None:
                    node.update_dist_to_end((end_row, end_col))

    return graph, nodes, nodes[start_row][start_col], nodes[end_row][end_col]


def add_adj_to_graph(graph, pos, lines, diagonals):
    # creates change vectors for all directions, and then loops through all
    # those directions to see if any of them actually work. If they do,
    # they are added to the valid moves of the current position in the graph
    adjacent = []
    valid_moves = [' ', 'E']
    # finding all the paths that this current position can take

    up_vec = (-1, 0)
    down_vec = (1, 0)
    left_vec = (0, -1)
    right_vec = (0, 1)

    up_right = (-1, 1)
    down_right = (1, 1)
    up_left = (-1, -1)
    down_left = (1, -1)

    if diagonals:
        all_directions = [up_vec, down_vec, left_vec, right_vec,
                          up_right, down_right, up_left, down_left]
    else:
        all_directions = [up_vec, down_vec, left_vec, right_vec]

    for direction in all_directions:
        new_row, new_col, valid = dir_works(valid_moves, pos, direction, lines)
        if valid:
            adjacent.append((new_row, new_col))

    # adding all links to graph
    graph[pos] = adjacent
    return graph


def dir_works(valid_moves, pos_vec, change_vec, lines):
    # checks if the change_vec works for the current position
    row, col = pos_vec
    row_change, col_change = change_vec

    new_row = row + row_change
    new_col = col + col_change

    try:
        tester = lines[new_row][new_col]
        valid = tester in valid_moves
        return new_row, new_col, valid
    except IndexError:
        return None, None, False


def display_pathfinder(nodes, display, wid_per_tile, hei_per_tile,
                       start_node, end_node):
    # used to display the final maze at the beginning and end
    display.fill((0, 0, 0))
    y = 0
    for row in nodes:
        x = 0
        for node in row:
            color = (255, 255, 255)
            if node == end_node or node == start_node:
                color = (0, 0, 255)
            elif node is None:
                color = (0, 0, 0)
            elif node.is_correct():
                color = (0, 255, 0)
            elif node.is_reached():
                color = (120, 120, 120)

            pygame.draw.rect(display, color, [x, y, wid_per_tile, hei_per_tile])

            x += wid_per_tile
        y += hei_per_tile

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()

    pygame.display.update()


"""---------------------------Queue------------------------------------------"""


class PriorityQueue:
    """
        Priority Queue ranks nodes by their distance and then their current
        length. This is slightly different than the typical a* approach with
        adds the heuristic distance with the current cost, instead it separates
        heuristic distance and current cost into 2 different categories.
        Distance is given priority in sorting
    """
    def __init__(self):
        self._vals = []
        self._count = 0

    def push(self, item):
        dist, path_len = item.cost()
        prioritized_item = (dist, path_len, self._count, item)
        self._count -= 1
        heapq.heappush(self._vals, prioritized_item)

    def pop(self):
        best_item = heapq.heappop(self._vals)
        dist, path_len, count, item = best_item
        return item

    def is_empty(self):
        return not self._vals


"""----------------------Builder Utils---------------------------------------"""


def write_file_auto(maze_str):
    # writes to the file for pathfinder.py to use
    maze_str = maze_str.replace('-', '#')
    maze_str = maze_str.replace('|', '#')
    maze_str = maze_str.replace('+', '#')

    file_name = 'maze.txt'
    with open(file_name, 'w') as file:
        file.write(maze_str)


"""---------------------------Nodes---------------------------------------"""


class PathNode:
    """
        row, col for position
        _done marks this node to not be used in loops through the algorithm
        path gives the shortest (at the moment) path to the node
            if this node is determined to be a correct node in the path, another
             algorithm will run through it to check if there is better path
             (this is not done for every node to save computing time)
        _dist_to_end is the heuristic distance from this node to the end node
        _correct marks the node as one of the correct nodes in the solution
    """
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self._done = False
        self.path = None
        self._dist_to_end = None
        self._correct = False

    def update_dist_to_end(self, end_pos):
        # heuristic distance is defined by difference in row + difference in col
        end_row, end_col = end_pos
        self._dist_to_end = abs(self.row - end_row) + abs(self.col - end_col)

    def update_path(self, new_path):
        if self.path is None or len(new_path) < len(self.path):
            self.path = new_path

    def is_done(self):
        return self._done

    def update_done(self):
        self._done = True

    def is_reached(self):
        return self.path is not None

    def cost(self):
        assert self._dist_to_end is not None and self.path is not None
        return self._dist_to_end, len(self.path)

    def is_correct(self):
        return self._correct

    def update_correct(self):
        self._correct = True

