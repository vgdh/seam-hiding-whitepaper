import io
import math
import numpy as np
from typing import List


class Line:
    def __init__(self, xy1: tuple, xy2: tuple):
        self.x1 = xy1[0]
        self.y1 = xy1[1]
        self.x2 = xy2[0]
        self.y2 = xy2[1]
        self._length = None

    def length(self):
        if self._length is None:
            self._length = math.hypot(self.x2 - self.x1, self.y2 - self.y1)
        return self._length

    def __str__(self):
        return f'X1:{self.x1} Y1:{self.y1} X2:{self.x2} Y2:{self.y2}'


class Parameter:
    def __init__(self, name, value):
        self.name = name
        self.value = value


class Gcode:
    def __init__(self, command: str, parameters: List = None, comment: str = None):
        self.command = command
        self.parameters = parameters
        self.comment = comment

    def __str__(self):
        string = self.command
        for st in self.parameters:
            string += f' {st.name}{st.value}'
        if self.comment is not None:
            string += f" ;{self.comment}"
        return string


def create_points_on_circle(cx, cy, r, n, angle_shift):
    points = []
    f = math.radians(90)
    g = math.radians(-90)
    for i in range(n):
        angle = i * 2 * math.pi / n + math.radians(angle_shift)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))
    return points


def create_lines(points):
    start_point = None
    lines = []
    for point in points:
        if start_point is None:
            start_point = point
            continue
        lines.append(Line(start_point, point))
        start_point = point

    lines.append(Line(points[-1], points[0]))
    return lines


def filament_length_calculate(line_width, line_height, line_length, filament_diameter=1.75):
    filament_section = math.pi * (filament_diameter / 2) ** 2
    line_volume = line_width * line_height * line_length
    filament_length = line_volume / filament_section
    return filament_length


def gcode_create_line(line, z_height, line_height, width, speed, comment=None):
    filament_length = filament_length_calculate(width, line_height, line.length())
    gcode = Gcode("G1", [
        Parameter("X", line.x2),
        Parameter("Y", line.y2),
        Parameter("Z", z_height),
        Parameter("E", filament_length),
        Parameter("F", speed * 60),
    ])
    if comment is not None:
        gcode.comment = comment
    return gcode


def gcode_create_slope(lines, z_start, z_step, line_height_step, speed, line_width):
    gcodes = []
    for x in range(len(lines)):
        nozzle_height = z_start + z_step * (x + 1)
        if line_height_step > 0:
            line_height = line_height_step * (x + 1)
        else:
            line_height = abs(line_height_step * len(lines)) + line_height_step * (x + 1)
        if line_height < 0:
            raise Exception()
        gcode = gcode_create_line(lines[x], nozzle_height, line_height, line_width, speed, "slope")
        gcodes.append(gcode)

    return gcodes


def gcode_create_lines(lines, z_height, line_height, line_width, speed):
    gcodes = []
    for line in lines:
        gcode = gcode_create_line(line, z_height, line_height, line_width, speed, "straight")
        gcodes.append(gcode)
    return gcodes


def create_layer(lines, seam_length, current_z, layer_height, line_width, speed, travel_speed=200):
    gcodes = []
    gcodes.append(Gcode("G1", [Parameter("E", -0.5)], "retract"))

    gcode = Gcode("G1", [
        Parameter("X", lines[0].x1),
        Parameter("Y", lines[0].y1),
        Parameter("F", travel_speed * 60),
    ])
    gcodes.append(gcode)

    gcode = Gcode("G1", [
        Parameter("Z", current_z),
        Parameter("F", travel_speed * 60),
    ])
    gcodes.append(gcode)

    gcodes.append(Gcode("G1", [Parameter("E", 0.5)], "unretract"))

    end_seam_line = None
    seam_length_complete = 0
    for line in lines:
        seam_length_complete += line.length()
        if seam_length_complete >= seam_length:
            end_seam_line = line
            break

    end_seam_line_index = lines.index(end_seam_line)

    goal_z = current_z + layer_height
    slop_lines = lines[:end_seam_line_index + 1]
    z_step = (goal_z - current_z) / len(slop_lines)
    slope = gcode_create_slope(slop_lines, current_z, z_step, z_step, speed, line_width)

    no_slope_lines = lines[end_seam_line_index + 1:]
    no_slope = gcode_create_lines(no_slope_lines, goal_z, layer_height, line_width, speed)

    finish_seam = gcode_create_slope(slop_lines, goal_z, 0, z_step * -1, speed, line_width)

    gcodes.extend(slope)
    gcodes.extend(no_slope)
    gcodes.extend(finish_seam)
    # gcodes.append(Gcode("G1", [Parameter("Z", goal_z + 0.3)], "go up a little before next thing"))

    return gcodes


def main():
    gcodes = ["START_PRINT BED_TEMP=80 EXTRUDER_TEMP=240", "M83", "M106 S40"]
    # gcodes = ["G28","M83"]

    layer_height = 0.3
    line_width = 0.8
    seam_length_external = 60
    seam_length_internal = 60
    speed_first_layer = 20
    speed_internal = 50
    speed_external = 50

    lines_in_ring = 4
    lines_list = []
    for x in range(lines_in_ring):
        points = create_points_on_circle(90, 90, 20 + line_width * x, 200, angle_shift=-90)
        lines_list.append(create_lines(points))

    # first layer
    for x in range(lines_in_ring):
        first_layer = create_layer(lines_list[x], 0, 0, 0.3, line_width, speed_first_layer)
        gcodes.extend(first_layer)

    gcodes.append("M106 S128")
    # other layers
    figure_height = 10
    for layer_level in np.arange(layer_height, figure_height, layer_height):
        for x in range(lines_in_ring - 1):
            layer_internal = create_layer(lines_list[x], seam_length_internal, layer_level, layer_height, line_width,
                                          speed_internal)
            gcodes.extend(layer_internal)
        layer_external = create_layer(lines_list[-1], seam_length_external, layer_level, layer_height, line_width,
                                      speed_external)
        gcodes.extend(layer_external)

    gcodes.append("END_PRINT")
    with open('output.gcode', 'w') as f:
        # loop through the list and write each item to the file
        for item in gcodes:
            f.write(str(item) + '\n')


if __name__ == '__main__':
    main()
