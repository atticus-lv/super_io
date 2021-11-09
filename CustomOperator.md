### Operator Type

+ Default: Default Import of build-in importer

+ Blender Files: Import all type of data from the pasted blend files

+ Addon: Custom Operator

### Custom Operator

Custom operators allow you to select an existing operator and pass parameters to it.

1. Hover the mouse over an import operator button, right-click and copy the python command or `Ctrl C` to get such
   as `bpy.ops.xxxx()`

2. Paste it on the operator ID, it will automatically remove the head and tail, and correct it to `xxx`. For
   non-standard formats, please manually remove the brackets and contents

3. Select the execution environment , If you select `INVOKE_DEFAULT`, then start execution from the invoke function of
   this operator. For most imported plugins, the execution environment will pop up a selection popup window.<br> If you
   select `EXEC_DEFAULT` (default), start from this operation The execute function of the operator starts to execute

4. No matter which option is executed, when this operator is called in the import file, the parameter
   of `filepath = file path` will be passed in. If the specified operator does not use filepath as the parameter to
   identify the file path, Then the operator fails to call.<br> Subsequent updates may use special character identifiers
   for parameter substitution to meet the needs of different naming conventions.

5. The user can add custom parameters by pressing the + button. Currently, strings and floating point are supported. ,
   Parameter identification of integer type