# Custom Config

Custom configs let you route a copied file to a specific Blender operator with specific properties.

## Add A Config

Open the Super IO preferences and add a custom import/export item. A config usually contains:

- Name and prompt text shown in Super IO menus.
- File extension, such as `obj`, `blend`, or `png`.
- IO type: import or export.
- Operator type or custom operator ID.
- Optional properties passed to the Blender operator.
- Optional match rules for filename prefix, suffix, or other supported rules.

<div class="spio-shot">
  <img src="/media/img/cn/0.png" alt="Custom config fields">
</div>

## Import And Export Config JSON

Super IO can export custom configs to JSON and import them again later.

In Super IO 2.x, this JSON format is versioned. The extension also keeps a persistent JSON configuration file outside Blender preferences, which makes future migrations easier.

<div class="spio-shot">
  <img src="/media/img/cn/2.png" alt="Config import and export buttons">
</div>

## Search And Match

The config list can be filtered by name, extension, rule, color tag, and IO type.

<div class="spio-shot">
  <img src="/media/img/cn/3.png" alt="Config search filters">
</div>

## Example: Blend Material Import

For a file named `M_IamMaterial.blend`, you can make a preset that recognizes material blend files:

1. Add a new config.
2. Set the extension to `blend`.
3. Set the match rule to prefix.
4. Set the match value to `M_`.
5. Set the operator type to append materials.

Now files starting with `M_` can use the material import preset without asking you to choose from every blend import option.
