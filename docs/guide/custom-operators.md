# Custom Operators

Custom operators are useful when the built-in presets are not enough and you want Super IO to call a specific Blender operator.

## Operator ID

Most Blender buttons can reveal their Python operator:

1. Hover an operator button in Blender.
2. Right-click and copy the Python command.
3. Paste it into Super IO's custom operator field.
4. Remove arguments and parentheses if needed, leaving the operator ID.

For example, a copied command like `bpy.ops.wm.obj_import()` becomes `wm.obj_import`.

## Execution Context

Super IO can call an operator in different execution modes:

- `EXEC_DEFAULT` runs the operator directly and is best for repeatable presets.
- `INVOKE_DEFAULT` lets Blender show the operator's normal popup when the operator supports it.

When importing a file, Super IO passes the file path to the operator through the `filepath` argument. Operators that do not accept `filepath` are not suitable for direct file import configs.

## Properties

Custom configs can define extra operator properties. Use them for small, stable options such as booleans, strings, numbers, or Blender import/export flags.
