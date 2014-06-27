# cod_totaling: utf-8
import math
import operator


class WiiGestureRecognizer:
    templates = {}

    def compare_to_templates(self, points):
        points = self._compute_points(points)
        tpl_distances = {}
        for template in self.templates:
            d = 0
            for i in range(0, len(template)):
                x = points[i][0]
                y = points[i][1]
                x_tpl = template[i][0]
                y_tpl = template[i][1]
                d += math.sqrt(
                    math.pow(x - x_tpl, 2) + math.pow(y - y_tpl, 2))
            tpl_distances[template.name] = d
        tpl_distances = sorted(
            tpl_distances.iteritems(), key=operator.itemgetter(1))
        return tpl_distances[0]

    def _compute_points(self, points):
        points = self._resample(points)
        if len(points) > 0:
            points = self._rotate(points)
            points = self._scale(points)
            return points
        else:
            return points

    # points = [(1,1), (2,3), (4,4)]
    def _resample(self, points, n=64):
        d_total = 0
        sampled_points = []

        for i in range(0, len(points) - 1):
            x1 = points[i][0]
            y1 = points[i][1]
            x2 = points[i + 1][0]
            y2 = points[i + 1][1]
            d_total += math.sqrt(
                math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
        if d_total > 0:
            sampled_points[0] = points[0]
            step_size = d_total / float(n)

            d_sum = 0
            for i in range(0, len(points) - 1):
                x1 = points[i][0]
                y1 = points[i][1]
                x2 = points[i + 1][0]
                y2 = points[i + 1][1]
                d = math.sqrt(
                    math.pow(x1 - x2, 2) + math.pow(y1 - y2, 2))
                if (d + d_sum) < step_size:
                    # a points gets jumped over if its distance to
                    # the original point is lesser then the step size
                    d_sum += d
                    continue
                else:
                    d_sum = 0
                    scale_factor = step_size / d
                    delta_x = scale_factor * (x2 - x1)
                    delta_y = scale_factor * (y2 - y1)
                    sampled_point = (x1 + delta_x)
                    sampled_point = (y1 + delta_y)

                    sampled_points.append(sampled_point)

        return sampled_points

    # points = [(1,1), (2,3), (4,4)]
    def _rotate(self, points):
        # find center point of the figure
        center = []
        x_sum = y_sum = 0.0
        for point in points:
            x_sum += point.x
            y_sum += point.y
        center[0] = x_sum / len(points)
        center[1] = y_sum / len(points)

        # shift all points so that the center is at (0, 0)
        x_delta = center[0] + (center[0] * -1)
        y_delta = center[1] + (center[1] * -1)
        for i in range(0, len(points)):
            points[i] = (
                points[i][0] + x_delta, points[i][1] + y_delta)

        # find angle a between centroid and first point (in radians)
        angle = math.atan2(
            center[1] - points[0][1], center[0] - points[0][0])

        # rotate all points by the computed angle
        rotated_points = []
        for point in points:
            x = (point.x - center[0]) * math.cos(angle) - \
                (point.y - center[1]) * math.sin(angle) + center[0]
            y = (point.x - center[0]) * math.sin(angle) + \
                (point.y - center[1]) * math.cos(angle) + center[1]
            rotated_points.append((x, y))
        return rotated_points

    # points = [(1,1), (2,3), (4,4)]
    def _scale(self, points):
        # define the bounding box by computing the edges
        min_x = points[0][0]
        max_x = points[0][0]
        min_y = points[0][1]
        max_y = points[0][1]
        bb_size = 100.0
        for i in range(1, len(points)):
            x = points[i][0]
            y = points[i][1]
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y

        # scale each point so it fits into the bounding box
        scale_factor_x = (max_x - min_x) / bb_size
        scale_factor_y = (max_y - min_y) / bb_size
        scaled_points = []
        for point in points:
            x = point[0] * scale_factor_x
            y = point[1] * scale_factor_y
            scaled_points.append((x, y))

        return scaled_points

    class Template:
        def __init__(self, name, points):
            self.name = name
            self.points = points
