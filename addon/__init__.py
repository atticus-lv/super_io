from . import addon_updater, asset_helper, importer


def register():
    addon_updater.register()
    asset_helper.register()
    importer.register()


def unregister():
    addon_updater.unregister()
    asset_helper.unregister()
    importer.unregister()
