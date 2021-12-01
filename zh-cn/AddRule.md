你可以为配置添加文件名匹配规则来避免配置弹出选择菜单，加快导入

以 `M_特殊材质.blend` 为例子, 用户希望有一个配置能识别此种以M_开头的blend文件，导入其所有材质

以下是实现该自定义配置的步骤
1. 新建配置
2. 设置扩展名为`blend`
3. 设置匹配规则为前缀
4. 设置匹配值为`M_`
5. 设置操作符类型为`Append Materials`