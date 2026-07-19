"""SealBench synthetic seal generator (Blender >= 3.6).

Procedurally renders bolt seals and cable seals on a trailer-door-style plane
with domain randomization (materials, lighting, camera pose, backgrounds), and
writes YOLO-format labels from projected bounding boxes.

Run headless:
    blender -b -P synthetic/generate_seals.py -- --out data/synthetic --n 500

Notes
-----
- This is a v0.1 generator: bolt + cable seals only (they dominate high-value
  freight). Plastic strap seals are a good first contribution (curve + flat
  extrude).
- For background realism, drop HDRI files (.hdr/.exr, e.g. from polyhaven.com,
  CC0) into synthetic/hdri/ — the script cycles through them; without HDRIs it
  falls back to randomized sky lighting.
"""

import argparse
import math
import random
import sys
from pathlib import Path

import bpy
from mathutils import Vector

CLASS_BOLT = 0
CLASS_CABLE = 1

SEAL_COLORS = [
    (0.85, 0.1, 0.1), (0.95, 0.55, 0.05), (0.95, 0.85, 0.1),
    (0.1, 0.45, 0.85), (0.1, 0.7, 0.3), (0.9, 0.9, 0.9), (0.15, 0.15, 0.15),
]
DOOR_COLORS = [
    (0.9, 0.9, 0.9), (0.75, 0.75, 0.78), (0.55, 0.58, 0.6),
    (0.72, 0.68, 0.6), (0.35, 0.38, 0.42), (0.6, 0.1, 0.1), (0.1, 0.25, 0.5),
]


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.lights, bpy.data.cameras):
        for item in list(block):
            if item.users == 0:
                block.remove(item)


def make_material(name, rgb, metallic=0.0, rough=0.5):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = rough
    return mat


def make_door():
    """Trailer-door plane with hasp block."""
    bpy.ops.mesh.primitive_plane_add(size=2.0, rotation=(math.pi / 2, 0, 0))
    door = bpy.context.object
    door.name = "door"
    door.data.materials.append(
        make_material("door_mat", random.choice(DOOR_COLORS), rough=random.uniform(0.4, 0.9))
    )
    # vertical lock rod
    bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1.9, location=(0.15, -0.021, 0))
    rod = bpy.context.object
    rod.rotation_euler = (math.pi / 2, 0, 0)
    rod.data.materials.append(make_material("rod_mat", (0.6, 0.6, 0.62), metallic=1.0, rough=0.35))
    # hasp block near handle height
    bpy.ops.mesh.primitive_cube_add(size=0.09, location=(0.15, -0.05, -0.15))
    hasp = bpy.context.object
    hasp.data.materials.append(make_material("hasp_mat", (0.5, 0.5, 0.52), metallic=1.0, rough=0.4))
    return Vector((0.15, -0.08, -0.22))  # seal anchor point below hasp


def make_bolt_seal(anchor):
    parts = []
    color = random.choice(SEAL_COLORS)
    # pin
    bpy.ops.mesh.primitive_cylinder_add(radius=0.006, depth=0.07, location=anchor)
    pin = bpy.context.object
    pin.data.materials.append(make_material("pin", (0.7, 0.7, 0.72), metallic=1.0, rough=0.3))
    parts.append(pin)
    # head (colored plastic cap)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.016, depth=0.02, location=anchor + Vector((0, 0, 0.045))
    )
    head = bpy.context.object
    head.data.materials.append(make_material("head", color, rough=random.uniform(0.2, 0.6)))
    parts.append(head)
    # locking bushing
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.014, depth=0.025, location=anchor + Vector((0, 0, -0.04))
    )
    bush = bpy.context.object
    bush.data.materials.append(make_material("bush", color, rough=random.uniform(0.2, 0.6)))
    parts.append(bush)
    return parts, CLASS_BOLT


def make_cable_seal(anchor):
    parts = []
    color = random.choice(SEAL_COLORS)
    # cable as a randomized bezier loop through the anchor
    curve = bpy.data.curves.new("cable", type="CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = random.uniform(0.0015, 0.0035)
    spline = curve.splines.new("BEZIER")
    n_pts = 5
    spline.bezier_points.add(n_pts - 1)
    for i, bp in enumerate(spline.bezier_points):
        t = i / (n_pts - 1)
        jitter = Vector((random.uniform(-0.02, 0.02), random.uniform(-0.02, 0.0), 0))
        bp.co = anchor + Vector((0.08 * math.sin(t * math.pi * 2), -0.02, 0.09 * (t - 0.5))) + jitter
        bp.handle_left_type = bp.handle_right_type = "AUTO"
    cable = bpy.data.objects.new("cable_obj", curve)
    bpy.context.collection.objects.link(cable)
    cable.data.materials.append(make_material("cable_mat", (0.75, 0.75, 0.78), metallic=1.0, rough=0.4))
    parts.append(cable)
    # lock body
    bpy.ops.mesh.primitive_cube_add(size=0.03, location=anchor + Vector((0, -0.03, 0)))
    body = bpy.context.object
    body.scale = (1.0, 0.7, 1.3)
    body.data.materials.append(make_material("body_mat", color, metallic=0.6, rough=0.4))
    parts.append(body)
    return parts, CLASS_CABLE


def place_camera_light():
    dist = random.uniform(0.5, 3.0)
    yaw = math.radians(random.uniform(-60, 60))
    pitch = math.radians(random.uniform(-10, 25))
    cam_loc = Vector(
        (
            dist * math.sin(yaw),
            -dist * math.cos(yaw) * math.cos(pitch),
            dist * math.sin(pitch) - 0.1,
        )
    )
    bpy.ops.object.camera_add(location=cam_loc)
    cam = bpy.context.object
    look = Vector((0.15, 0, -0.2)) - cam_loc
    cam.rotation_euler = look.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam

    kind = random.choice(["SUN", "POINT", "AREA"])
    bpy.ops.object.light_add(
        type=kind,
        location=(random.uniform(-2, 2), random.uniform(-3, -1), random.uniform(0.5, 3)),
    )
    light = bpy.context.object
    light.data.energy = {
        "SUN": random.uniform(1, 6),
        "POINT": random.uniform(50, 400),
        "AREA": random.uniform(50, 300),
    }[kind]
    # night-scene chance: dim world, strong point light (headlight/flashlight look)
    if random.random() < 0.2:
        light.data.energy *= 3
        bpy.context.scene.world.node_tree.nodes["Background"].inputs[1].default_value = 0.02


def setup_world(hdri_paths):
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    bpy.context.scene.world = world
    bg = world.node_tree.nodes["Background"]
    if hdri_paths and random.random() < 0.8:
        env = world.node_tree.nodes.new("ShaderNodeTexEnvironment")
        env.image = bpy.data.images.load(str(random.choice(hdri_paths)))
        world.node_tree.links.new(env.outputs["Color"], bg.inputs["Color"])
        bg.inputs[1].default_value = random.uniform(0.3, 1.5)
    else:
        bg.inputs[0].default_value = (*[random.uniform(0.2, 0.9)] * 3, 1.0)
        bg.inputs[1].default_value = random.uniform(0.2, 1.2)


def yolo_bbox(objs, cam, scene):
    """Project objects' bounding-box corners to normalized YOLO xywh."""
    from bpy_extras.object_utils import world_to_camera_view

    xs, ys = [], []
    depsgraph = bpy.context.evaluated_depsgraph_get()
    for obj in objs:
        eval_obj = obj.evaluated_get(depsgraph)
        for corner in eval_obj.bound_box:
            world_co = eval_obj.matrix_world @ Vector(corner)
            co = world_to_camera_view(scene, cam, world_co)
            xs.append(co.x)
            ys.append(1.0 - co.y)
    x0, x1 = max(0.0, min(xs)), min(1.0, max(xs))
    y0, y1 = max(0.0, min(ys)), min(1.0, max(ys))
    if x1 <= x0 or y1 <= y0:
        return None  # off-frame
    return ((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0)


def main():
    argv = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/synthetic")
    ap.add_argument("--n", type=int, default=100)
    ap.add_argument("--res", type=int, default=960)
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args(argv)

    random.seed(args.seed)
    out = Path(args.out)
    (out / "images").mkdir(parents=True, exist_ok=True)
    (out / "labels").mkdir(parents=True, exist_ok=True)
    hdri_paths = sorted(Path(__file__).parent.glob("hdri/*.[eh]*dr*"))

    scene = bpy.context.scene
    scene.render.engine = "CYCLES"
    scene.cycles.samples = 64
    scene.render.resolution_x = scene.render.resolution_y = args.res

    for i in range(args.n):
        clean_scene()
        setup_world(hdri_paths)
        anchor = make_door()
        maker = random.choice([make_bolt_seal, make_cable_seal])
        negative = random.random() < 0.15  # 15% no-seal negatives
        label_lines = []
        if not negative:
            parts, cls = maker(anchor)
        place_camera_light()
        scene.render.filepath = str(out / "images" / f"syn_{i:05d}.png")
        bpy.ops.render.render(write_still=True)
        if not negative:
            box = yolo_bbox(parts, scene.camera, scene)
            if box:
                label_lines.append(f"{cls} " + " ".join(f"{v:.6f}" for v in box))
        (out / "labels" / f"syn_{i:05d}.txt").write_text("\n".join(label_lines))
        print(f"[{i + 1}/{args.n}] rendered {'negative' if negative else 'seal'}")


if __name__ == "__main__":
    main()
