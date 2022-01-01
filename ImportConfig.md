You can add file name matching rules to the configto avoid the configuration pop-up selection menu and speed up the import

Take `M_IamMaterial.blend` as an example, the user wants to have a configuration that can recognize this kind of blend file starting with M_ and import all its materials

The following are the steps to implement this custom configuration
1. New config
2. Set the extension to`blend`
3. Set the matching rule to prefix
4. Set the match value to`M_`
5. Set the operator type to`Append Materials`