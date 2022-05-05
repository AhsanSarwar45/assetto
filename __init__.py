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
import typing


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

        collections = ["Guide Meshes", "Meshes"]

        for collection_name in collections:
            collection = bpy.data.collections.new(collection_name)
            bpy.context.scene.collection.children.link(collection)
        # bpy.ops.outliner.item_rename()

        return {"FINISHED"}


def set_active_collection(collection_name: str):
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[collection_name]


def delete_collection(collection_name: str, delete_objects: bool = True):
    collection = bpy.data.collections.get(collection_name)

    if collection:
        if delete_objects:
            obs = [obj for obj in collection.objects if obj.users == 1]
            while obs:
                bpy.data.objects.remove(obs.pop())

        bpy.data.collections.remove(collection)


def initialize_collection(collection_name: str, delete_existing: bool = True):
    if delete_existing:
        delete_collection(collection_name)

    collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)

    set_active_collection(collection_name)


class SetupBlueprintsOperator(bpy.types.Operator):
    bl_idname = "assetto.setup_blueprints"
    bl_label = "Setup Blueprints"
    bl_description = "Sets up the blueprints"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        if context.scene.blueprint_path == "":
            self.report({"ERROR"}, "Please select a blueprint file")
        # If not image file
        elif not context.scene.blueprint_path.endswith(tuple(bpy.path.extensions_image)):
            self.report({"ERROR"}, "Please select an image file")
        else:
            initialize_collection("Blueprints")

            blueprints = []

            if context.scene.should_add_front_blueprint:
                blueprints.append({"name": "Front", "rotation": (1.5708, 0, 0), "scale": (1, 1, 1)})
            if context.scene.should_add_back_blueprint:
                blueprints.append({"name": "Back", "rotation": (-1.5708, -3.1416, 0), "scale": (1, 1, 1)})
            if context.scene.should_add_left_blueprint:
                blueprints.append({"name": "Left", "rotation": (1.5708, 0, 1.5708), "scale": (1, 1, 1)})
            if context.scene.should_add_right_blueprint:
                blueprints.append({"name": "Right", "rotation": (-1.5708, 3.1416, 1.5708), "scale": (1, 1, 1)})
            if context.scene.should_add_top_blueprint:
                blueprints.append({"name": "Top", "rotation": (0, 0, 1.5708), "scale": (1, 1, 1)})
            if context.scene.should_add_bottom_blueprint:
                blueprints.append({"name": "Bottom", "rotation": (3.1416, 0, 0), "scale": (1, 1, 1)})

            # bpy.ops.object.empty_add(type="IMAGE", radius=1, align="VIEW")
            for blueprint in blueprints:
                bpy.ops.object.load_background_image(filepath=context.scene.blueprint_path, view_align=False)
                bpy.context.active_object.rotation_euler = Euler(blueprint["rotation"], "XYZ")
                bpy.context.active_object.name = "Blueprint" + blueprint["name"]
                bpy.context.active_object.show_empty_image_perspective = context.scene.show_blueprints_in_perspective
                bpy.context.active_object.show_empty_image_orthographic = context.scene.show_blueprints_in_orthographic
                bpy.context.space_data.shading.show_backface_culling = True

            bpy.types.Scene.blueprints = blueprints
            # bpy.ops.object.
        # bpy.ops.outliner.item_rename()

        return {"FINISHED"}


class AlignBlueprintsOperator(bpy.types.Operator):
    bl_idname = "assetto.align_blueprints"
    bl_label = "Align Blueprints"
    bl_description = "Aligns the blueprints based on the position of the alignment planes"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        return {"FINISHED"}


class AddBlueprintAlignmentPlanesOperator(bpy.types.Operator):
    bl_idname = "assetto.add_blueprint_alignment_planes"
    bl_label = "Add Alignment Planes"
    bl_description = "Adds alignments planes for the blueprints"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):

        initialize_collection("Blueprint Alignment Planes")

        for blueprint in bpy.types.Scene.blueprints:
            bpy.ops.object.empty_add(
                type="IMAGE", align="WORLD", location=(0, 0, 0), scale=(1, 1, 1), rotation=blueprint["rotation"]
            )
            bpy.context.active_object.name = "AlignmentPlane" + blueprint["name"]

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
    bl_idname = "ASSETTO_PT_Blueprint"
    bl_parent_id = ASSETTO_PT_Root.bl_idname
    bl_label = "Blueprint"

    def draw(self, context):
        layout = self.layout
        column = layout.column()
        column.prop(context.scene, "blueprint_path")

        column.label(text="Angles")

        row = column.row(align=True)

        row.prop(context.scene, "should_add_front_blueprint", toggle=True)
        row.prop(context.scene, "should_add_back_blueprint", toggle=True)
        row.prop(context.scene, "should_add_left_blueprint", toggle=True)
        row.prop(context.scene, "should_add_right_blueprint", toggle=True)
        row.prop(context.scene, "should_add_top_blueprint", toggle=True)
        row.prop(context.scene, "should_add_bottom_blueprint", toggle=True)

        row = column.row()
        row.label(text="Show In")

        row_column = row.column(align=True)
        row_column.prop(context.scene, "show_blueprints_in_orthographic")
        row_column.prop(context.scene, "show_blueprints_in_perspective")

        column.operator(SetupBlueprintsOperator.bl_idname, text=SetupBlueprintsOperator.bl_label)


class ASSETTO_PT_BlueprintAlignment(AssettoPanel, bpy.types.Panel):
    bl_idname = "ASSETTO_PT_BlueprintAlignment"
    bl_parent_id = ASSETTO_PT_Blueprint.bl_idname
    bl_label = "Alignment"

    def draw(self, context):
        layout = self.layout
        column = layout.column()

        column.operator(
            AddBlueprintAlignmentPlanesOperator.bl_idname, text=AddBlueprintAlignmentPlanesOperator.bl_label
        )
        column.operator(AlignBlueprintsOperator.bl_idname, text=AlignBlueprintsOperator.bl_label)


from bpy.utils import register_class, unregister_class

classes = [
    SetupWorkspaceOperator,
    SetupBlueprintsOperator,
    AlignBlueprintsOperator,
    AddBlueprintAlignmentPlanesOperator,
    ASSETTO_PT_Root,
    ASSETTO_PT_Blueprint,
    ASSETTO_PT_BlueprintAlignment,
]


def register():
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.blueprints = []
    bpy.types.Scene.blueprint_path = bpy.props.StringProperty(
        name="Blueprint Path", default="", description="Select blueprint", subtype="FILE_PATH"
    )
    bpy.types.Scene.show_blueprints_in_perspective = bpy.props.BoolProperty(name="Perspective", default=False)
    bpy.types.Scene.show_blueprints_in_orthographic = bpy.props.BoolProperty(name="Orthographic", default=True)

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
