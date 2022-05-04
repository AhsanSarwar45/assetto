# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Assetto",
    "author": "Ahsan Sarwar",
    "description": "",
    "blender": (2, 80, 0),
    "version": (0, 0, 1),
    "location": "",
    "warning": "",
    "category": "Generic",
}

from . import auto_load

auto_load.init()


def register():
    auto_load.register()


def unregister():
    auto_load.unregister()


import bpy
from mathutils import Euler


class SetupWorkspaceOperator(bpy.types.Operator):
    bl_idname = "assetto.setup_workspace"
    bl_label = "Setup Workspace"
    bl_description = "Sets up the workspace"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete(use_global=False, confirm=False)

        # Delete all collections
        for c in context.scene.collection.children:
            bpy.data.collections.remove(c, do_unlink=True)

        collections = ["Blueprints", "Guide Meshes", "Meshes"]

        for collection_name in collections:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        # bpy.ops.outliner.item_rename()

        return {"FINISHED"}


class SetupBlueprintsOperator(bpy.types.Operator):
    bl_idname = "assetto.setup_blueprints"
    bl_label = "Setup Blueprints"
    bl_description = "Sets up the blueprints"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        # If not image file
        if not context.scene.blueprint_path.endswith(tuple(bpy.path.extensions_image)):
            self.report({"ERROR"}, "Please select an image file")
        elif context.scene.blueprint_path == "":
            self.report({"ERROR"}, "Please select a blueprint file")
        else:
            if bpy.data.collections.get("Blueprints"):
                reference_collection = bpy.data.collections["Blueprints"]
            else:
                reference_collection = bpy.data.collections.new("Blueprints")
                bpy.context.scene.collection.children.link(reference_collection)

            bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[
                "Blueprints"
            ]

            blueprints = [
                {"name": "BlueprintFront", "rotation": (1.5708, 0, 0)},
                {"name": "BlueprintLeft", "rotation": (1.5708, 0, 0)},
                {"name": "BlueprintRight", "rotation": (1.5708, 0, 0)},
                {"name": "BlueprintTop", "rotation": (1.5708, 0, 0)},
                {"name": "BlueprintBack", "rotation": (1.5708, 0, 0)},
            ]

            # bpy.ops.object.empty_add(type="IMAGE", radius=1, align="VIEW")
            bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
            bpy.context.active_object.rotation_euler = Euler((1.5708, 0, 0), "XYZ")
            bpy.context.active_object.name = "BlueprintFront"

            bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
            bpy.context.active_object.rotation_euler = Euler((-1.5708, -1.5708, 0), "XYZ")

            bpy.ops.transform.rotate(value=-1.5708, orient_axis="Y")
            bpy.ops.transform.rotate(value=-1.5708, orient_axis="X")
            bpy.context.active_object.name = "BlueprintLeft"

            bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
            bpy.ops.transform.rotate(value=-1.5708, orient_axis="Y")
            bpy.ops.transform.rotate(value=-1.5708, orient_axis="X")
            bpy.ops.transform.resize(value=(-1, 1, 1))
            bpy.context.active_object.name = "BlueprintRight"

            bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
            bpy.context.active_object.name = "BlueprintTop"

            bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
            bpy.ops.transform.rotate(value=-1.5708, orient_axis="X")
            bpy.ops.transform.rotate(value=-3.1416, orient_axis="Z")
            bpy.context.active_object.name = "BlueprintBack"

            if context.scene.should_add_blueprint_alignment_planes:
                reference_collection = bpy.data.collections.new("Blueprint Alignment Planes")
                bpy.context.scene.collection.children.link(reference_collection)
                bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[
                    "Blueprint Alignment Planes"
                ]

                bpy.ops.mesh.primitive_plane_add(enter_editmode=False)
                bpy.context.active_object.name = "AlignmentPlaneTop"

            # bpy.ops.object.
        # bpy.ops.outliner.item_rename()

        return {"FINISHED"}


class AssettoPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Assetto"


class ASSETTO_PT_Root(AssettoPanel, bpy.types.Panel):
    bl_idname = "ASSETTO_PT_Root"
    bl_label = "Assetto"

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.operator(SetupWorkspaceOperator.bl_idname, text=SetupWorkspaceOperator.bl_label)

    # column.label("Reference Image")


class ASSETTO_PT_Blueprint(AssettoPanel, bpy.types.Panel):
    bl_parent_id = ASSETTO_PT_Root.bl_idname
    bl_label = "Blueprint"

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.prop(context.scene, "blueprint_path")

        row = column.row(align=True)
        row.prop(context.scene, "should_add_front_blueprint", toggle=True)
        row.prop(context.scene, "should_add_back_blueprint", toggle=True)
        row.prop(context.scene, "should_add_left_blueprint", toggle=True)
        row.prop(context.scene, "should_add_right_blueprint", toggle=True)
        row.prop(context.scene, "should_add_top_blueprint", toggle=True)
        row.prop(context.scene, "should_add_bottom_blueprint", toggle=True)

        column.prop(context.scene, "should_add_blueprint_alignment_planes")

        column.operator(SetupBlueprintsOperator.bl_idname, text=SetupBlueprintsOperator.bl_label)


from bpy.utils import register_class, unregister_class

classes = [SetupWorkspaceOperator, SetupBlueprintsOperator, ASSETTO_PT_Root, ASSETTO_PT_Blueprint]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.blueprint_path = bpy.props.StringProperty(
        name="Blueprint Path", default="", description="Select blueprint", subtype="FILE_PATH"
    )
    bpy.types.Scene.should_add_blueprint_alignment_planes = bpy.props.BoolProperty(
        name="Add Alignment Planes", default=True
    )
    bpy.types.Scene.should_add_front_blueprint = bpy.props.BoolProperty(name="Front", default=True)
    bpy.types.Scene.should_add_back_blueprint = bpy.props.BoolProperty(name="Back", default=True)
    bpy.types.Scene.should_add_left_blueprint = bpy.props.BoolProperty(name="Left", default=True)
    bpy.types.Scene.should_add_right_blueprint = bpy.props.BoolProperty(name="Right", default=False)
    bpy.types.Scene.should_add_top_blueprint = bpy.props.BoolProperty(name="Top", default=True)
    bpy.types.Scene.should_add_bottom_blueprint = bpy.props.BoolProperty(name="Bottom", default=False)


def unregister():
    for cls in classes:
        unregister_class(cls)
    del bpy.types.Scene.blueprint_path


if __name__ == "__main__":
    register()
