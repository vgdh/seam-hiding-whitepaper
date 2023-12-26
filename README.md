# Hide the Seam Completely
The whitepaper describes how to completely eliminate the visible seam.

(I have also already written some basic post processors for slicers. Enjoy! [repository](https://github.com/vgdh/seam-slope-postprocessor))

## Explanation
Every closed loop will eventually have a visible seam. However, if there is no specific point where the line ends, there is no seam, right?
1. Begin the line with a height of 0 and gradually increase the height of the nozzle and the line over some length until it reaches the full height of the line.
2. Move through the loop until reaching the end of the line, but continue extruding the filament due to the initial zero line height. Systematically reduce the line's height while maintaining the same nozzle height until reaching the end of the starting slope.
3. Move on to the next perimeter or infill.

That's it. The algorithm is remarkably simple, though the result is astonishingly good. 
It is not an easy task to post-process already existing GCODE files, but if it works at the slicer level, it will work very well.

## The python code
The repository includes an [example](https://github.com/vgdh/seam-hiding-whitepaper/blob/main/main.py) demonstrating a basic implementation of the algorithm for printing a ring. This implementation allows specifying parameters such as the number of lines in the ring, layer height, line width, speed, etc.

Also there is an [example](https://github.com/vgdh/seam-hiding-whitepaper/blob/main/nozzle%200.4%20line%200.3x0.8.gcode) of gcode file for 0.4 nozzle line 0.3x0.6 layer height 0.3

## Photos of the Seam Details on the Printed Example.
The first layer (the top on the first photo) was printed without the algorithm to get better adhesion.
![botom 2](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/a429c68b-1711-44fb-9c97-4f046763b9d3)
![botom 3](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/f1ebe624-44af-4e7e-a7a7-aa55142d8ca1)
![photo_1_2023-12-20_16-13-32](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/e4982fe6-1fb4-4d81-90e3-9ea5f6d95e3b)

In the photo below you can see there is no gap between the lines.
![top 1](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/fbca6b12-d2ec-416c-ae08-4e37baf869fd)
![side 1](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/dd3a2900-39af-4baa-b638-91ef0328c86e)
![botom 1](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/a96b0b4b-1658-4c4a-a8d8-b70bbde8845e)
![center 1](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/2989402c-cd03-430e-9bf3-4ee902ee383f)
![top 2](https://github.com/vgdh/seam-hiding-whitepaper/assets/15322782/bdfca30b-73c2-4045-b297-a6454080ec01)
