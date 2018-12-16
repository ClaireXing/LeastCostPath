# -*- coding: utf-8 -*-

"""
/***************************************************************************
 LeastCostPath
                                 A QGIS plugin
 Find the least cost path with given cost raster and points
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2018-12-12
        copyright            : (C) 2018 by FlowMap Group@SESS.PKU
        email                : xurigong@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

__author__ = 'FlowMap Group@SESS.PKU'
__date__ = '2018-12-12'
__copyright__ = '(C) 2018 by FlowMap Group@SESS.PKU'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

from math import sqrt
import queue


def dijkstra(start_row_col, end_row_cols, block, feedback=None):
    sqrt2 = sqrt(2)

    class Grid:
        def __init__(self, matrix):
            self.map = matrix
            self.h = len(matrix)
            self.w = len(matrix[0])

        def _in_bounds(self, id):
            x, y = id
            return 0 <= x < self.h and 0 <= y < self.w

        def _passable(self, id):
            x, y = id
            return self.map[x][y] is not None

        def is_valid(self, id):
            return self._in_bounds(id) and self._passable(id)

        def neighbors(self, id):
            x, y = id
            results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1),
                       (x + 1, y - 1), (x + 1, y + 1), (x - 1, y - 1), (x - 1, y + 1)]
            results = filter(self._in_bounds, results)
            results = filter(self._passable, results)
            return results

        def _manhattan_distance(self, id1, id2):
            x1, y1 = id1
            x2, y2 = id2
            return abs(x1 - x2) + abs(y1 - y2)

        def min_manhattan(self, curr_node, end_nodes):
            return min(map(lambda node: self._manhattan_distance(curr_node, node), end_nodes))

        def simple_cost(self, cur, nex):
            cx, cy = cur
            nx, ny = nex
            currV = self.map[cx][cy]
            offsetV = self.map[nx][ny]
            if cx == nx or cy == ny:
                return (currV + offsetV) / 2
            else:
                return sqrt2 * (currV + offsetV) / 2

    grid = Grid(block)
    end_row_cols = set(end_row_cols)

    frontier = queue.PriorityQueue()
    frontier.put((0, start_row_col))
    came_from = {}
    cost_so_far = {}

    if not grid.is_valid(start_row_col):
        return None, None, None

    # update the progress bar
    total_manhattan = grid.min_manhattan(start_row_col, end_row_cols)
    min_manhattan = total_manhattan
    feedback.setProgress(100 * (1 - min_manhattan / total_manhattan))

    came_from[start_row_col] = None
    cost_so_far[start_row_col] = 0

    current_node = None
    while not frontier.empty():
        current_cost, current_node = frontier.get()

        # update the progress bar

        if feedback:
            if feedback.isCanceled():
                return None, None, None

            curr_manhattan = grid.min_manhattan(current_node, end_row_cols)
            if curr_manhattan < min_manhattan:
                min_manhattan = curr_manhattan
                feedback.setProgress(100 * (1 - min_manhattan / total_manhattan))

        if current_node in end_row_cols:
            break

        for nex in grid.neighbors(current_node):
            new_cost = cost_so_far[current_node] + grid.simple_cost(current_node, nex)
            if nex not in cost_so_far or new_cost < cost_so_far[nex]:
                cost_so_far[nex] = new_cost
                frontier.put((new_cost, nex))
                came_from[nex] = current_node

    if current_node in end_row_cols:
        end_node = current_node
        least_cost = cost_so_far[current_node]
        path = []
        costs = []
        while current_node is not None:
            path.append(current_node)
            costs.append(cost_so_far[current_node])
            current_node = came_from[current_node]

        path.reverse()
        costs.reverse()
        return path, costs, end_node
    else:
        return None, None, None
