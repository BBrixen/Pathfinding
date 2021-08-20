from pathfinding_utils import *
from auto_maze_maker import generate_maze_for_pathfinding
import pygame


def pathfind(wid_per_tile, hei_per_tile, display, diagonals, step_by_step):
    # setting up variables
    graph, nodes, start_node, end_node = read_file_pathfinder(diagonals)

    # display for user before beginning
    display_pathfinder(nodes, display, wid_per_tile, hei_per_tile,
                       start_node, end_node)
    print('press any key to start')
    limiter = input()

    # preparing queue with first node
    start_node.update_path([(start_node.row, start_node.col)])
    queue = PriorityQueue()
    queue.push(start_node)

    # starting a* algorithm
    while not queue.is_empty():
        # limiter = input()  # this is here if a user wants to look at each step

        new_item = queue.pop()

        # checking for reaching the end
        if new_item == end_node:
            update_correct_nodes(new_item.path, nodes, graph)
            display_pathfinder(nodes, display, wid_per_tile, hei_per_tile,
                               start_node, end_node)
            print(f'path length = {len(new_item.path)}')

            print('press any key to end')
            limiter = input()
            return

        # no need to return to an already completed node, hopefully this
        # should not occur bc nodes should not be added to the queue twice,
        # but this is a safety measure
        if new_item.is_done():
            continue

        # grabbing row and col and adjacent positions
        row = new_item.row
        col = new_item.col

        # if we are displaying each step, then change the color of the current
        # node in the display
        if new_item != start_node and step_by_step:
            start_x = col * wid_per_tile
            start_y = row * hei_per_tile
            pygame.draw.rect(display, (120, 120, 120),
                             [start_x, start_y, wid_per_tile, hei_per_tile])
            pygame.display.update()

        pos = (row, col)
        adjacent = graph[pos]

        # looping though all possible squares from this current one
        for adj_row, adj_col in adjacent:
            neighbor_node = nodes[adj_row][adj_col]

            # is the neighbor has already been reached,
            # try updating this current node's best path
            if neighbor_node.is_reached():
                neighbor_best_path = neighbor_node.path[:]  # making copy
                neighbor_best_path.append((row, col))
                new_item.update_path(neighbor_best_path)

            else:
                # if the neighbor hasn't been reached, add it to the queue and
                # give it a speculative path, which will be corrected later
                speculative_path = new_item.path[:]
                # making copy to not alter og
                speculative_path.append((adj_row, adj_col))
                neighbor_node.update_path(speculative_path)

                queue.push(neighbor_node)

        # this item will not be returned to
        new_item.update_done()


def update_correct_nodes(correct_path, all_nodes, graph):
    """
    similar to a* but in reverse, this time it checks each node in the correct
    solution to see if there is a better solution. this is faster than
    optimizing each path as we go, instead we can optimize only the correct
    solution path

    this time we start at the end and loop back to the beginning only using a
    small set of correct nodes (and all its direct neighbors)
    """
    # queue the row and column tuples of the correct solution
    while len(correct_path) > 0:
        correct_path = correct_path[::-1]

        # get the correct node, and update its correct value
        row, col = correct_path[0]
        node = all_nodes[row][col]
        node.update_correct()

        pos = (row, col)
        adjacent = graph[pos]

        # loop through all neighbor nodes
        for adj_row, adj_col in adjacent:
            neighbor_node = all_nodes[adj_row][adj_col]

            # checks if the neighbor's path to this current node is better,
            # in which case the current node path will be updated to the
            # shortest path, and the queue will be updated
            if neighbor_node.is_reached():
                neighbor_best_path = neighbor_node.path[:]  # making copy
                neighbor_best_path.append((row, col))
                node.update_path(neighbor_best_path)

        # updating queue
        correct_path = node.path[:-1]


def main():
    # defines wid, height, size of squares, movement, and step by step display
    wid = 110
    hei = 60
    wid_per = hei_per = 8  # number of pixels for each box
    diagonals = False
    step_by_step = True

    # creates a maze for pathfinding using code by Christian Hill
    generate_maze_for_pathfinding(wid, hei)

    # sets up display
    wid = wid * 2 + 1
    hei = hei * 2 + 1
    display = pygame.display.set_mode((wid * wid_per, hei * hei_per))
    pygame.display.set_caption('Pathfinding')

    # begins pathfinding
    pathfind(wid_per, hei_per, display, diagonals, step_by_step)


if __name__ == '__main__':
    main()
