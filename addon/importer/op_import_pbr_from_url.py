import bpy
import requests
from pathlib import Path
import os
import re

support_web = {
    'ambientcg.com',
}


class SPIO_OT_import_pbr_from_url(bpy.types.Operator):
    bl_idname = "spio.import_pbr_from_url"
    bl_label = "Import PBR from URL"
    bl_description = "Import a PBR from a URL"

    url: bpy.props.StringProperty(name="URL", description="URL of the PBR to import")

    @classmethod
    def poll(self, context):
        return bpy.data.filepath != ''

    def execute(self, context):
        is_fit = False

        self.url = 'https://ambientcg.com/get?file=Ground054_2K-JPG.zip'
        print(self.url[len('https://'):])
        for link in support_web:
            if self.url[len('https://'):].startswith(link):
                is_fit = True
            elif self.url[len('http://'):].startswith(link):
                is_fit = True

        if not is_fit:
            self.report({'ERROR'}, "No URL specified")
            return {'CANCELLED'}

        if self.url.startswith('https://ambientcg.com'):  # https://ambientcg.com/get?file=WoodFloor051_1K-JPG.zip
            name = self.url.split('=')[1]
            print(name)
            dir = Path(bpy.data.filepath).parent.joinpath('Download_spio', 'ambientcg')
            if not os.path.exists(str(dir)):
                os.makedirs(str(dir))
            file_path = dir.joinpath(name)
            fp = self.download(self.url, str(file_path))
            if fp:
                bpy.ops.spio.import_pbr_zip(filepath=str(file_path))

        return {'FINISHED'}

    def download(self, url, file_path):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:68.0) Gecko/20100101 Firefox/68.0"
        }
        req = requests.session()
        req.trust_env = False
        r = req.get(url=url, headers=headers, verify=False)
        with open(file_path, "wb") as f:
            f.write(r.content)
            f.flush()

        return f

def register():
    bpy.utils.register_class(SPIO_OT_import_pbr_from_url)

def unregister():
    bpy.utils.unregister_class(SPIO_OT_import_pbr_from_url)
