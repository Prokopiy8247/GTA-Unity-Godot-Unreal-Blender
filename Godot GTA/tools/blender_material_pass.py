import bpy, bmesh
from mathutils import Vector
root = bpy.path.abspath('//').rstrip('/\\')
materials=['concrete','plaster','brick','wood','cloth','denim','shirt','uniform','skin','skin2','skin3','rubber']
for name in materials:
    mat=bpy.data.materials.get(name)
    if not mat:continue
    img=bpy.data.images.load(root+'/gta/generated/textures/'+name+'.png',check_existing=True)
    img.reload()
    img.pack()
    p=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
    tex=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'),None)
    if not tex:tex=mat.node_tree.nodes.new('ShaderNodeTexImage')
    tex.image=img
    mat.node_tree.links.new(tex.outputs['Color'],p.inputs['Base Color'])
for obj in bpy.data.objects:
    if obj.type!='MESH':continue
    bm=bmesh.new();bm.from_mesh(obj.data)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces))
    bm.to_mesh(obj.data);bm.free()
    if any(m.type=='ARMATURE' for m in obj.modifiers):continue
    uv=obj.data.uv_layers.active or obj.data.uv_layers.new(name='UVMap')
    for poly in obj.data.polygons:
        mat=obj.data.materials[poly.material_index] if len(obj.data.materials)>poly.material_index else None
        factor=.5 if mat and mat.name=='brick' else .25
        if mat and mat.name in ['rubber','wood']:factor=3
        norm=poly.normal
        axis=0
        for a in range(3):
            if abs(norm[a])>abs(norm[axis]):axis=a
        axes=[i for i in range(3) if i!=axis]
        for li in poly.loop_indices:
            co=obj.data.vertices[obj.data.loops[li].vertex_index].co
            uv.data[li].uv=(co[axes[0]]*factor,co[axes[1]]*factor)
collections=[bpy.data.collections[n] for n in sorted([c.name for c in bpy.data.collections if c.name.startswith('mc_')])]
for idx,coll in enumerate(collections):
    rootobj=bpy.data.objects.get(coll.name)
    if not rootobj:continue
    rootobj.location=(0,0,0)
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action='DESELECT')
    for obj in coll.objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=rootobj
    bpy.ops.export_scene.gltf(filepath=root+'/gta/generated/models/'+coll.name+'.glb',use_selection=True,export_animations=True,export_apply=False)
    rootobj.location=(idx%8* 60,idx//8* 80,0)
bpy.context.view_layer.update()
bpy.ops.wm.save_as_mainfile(filepath=root+'/GodotGTA.blend')
print('Textured, corrected normals, re-exported and organized',len(collections),'assets')
