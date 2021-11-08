## 1.The render button cannot be pressed

#### After an error is reported, the button turns grey and cannot be pressed.

At this time, you need to check whether the composite node of the composite node tree is named **Composite**

There are several solutions

1. Change the name of the current composite node (this error does not appear in the current scene)

2. Preferences > nodes > view layer passes change the default composite node name to the node name of your scene (this error will not appear again in the new file)

3. Interface > Translation > uncheck new data (this error will not appear again in new files)

#### The scene camera is not set

Just add a camera node or set up a scene camera directly

## 2.After rendering, the RSN panel is very stuck and cannot be moved

Be sure to use blender 2.92 and above

## 3.A new window pops up when rendering each frame

This problem exists in some versions of some people, which should be related to preferences and can not be reproduced for the time being.

If you have relevant steps / settings that can be reproduced, please leave a message below