"""Remove private absolute source paths from non-functional FBX provenance fields.
Only string payloads change; byte count, node offsets and geometry stay identical.
Run after re-exporting Blender FBX files, before publishing.
"""
from pathlib import Path
import struct

root = Path(__file__).resolve().parent.parent
changed = 0
for path in sorted((root / 'SourceAssets/BlenderExports').glob('*.fbx')):
    original = path.read_bytes()
    data = bytearray(original)
    marker = b'Original|ApplicationNativeFile'
    start = data.find(marker)
    if start < 0:
        raise RuntimeError('Missing expected Blender provenance field: ' + path.name)
    pos = start + len(marker)
    # In the Properties70/P record: property type, subtype, flags, value.
    for index in range(4):
        if data[pos:pos+1] != b'S':
            raise RuntimeError('Unexpected FBX metadata layout: ' + path.name)
        size = struct.unpack_from('<I', data, pos+1)[0]
        value_start = pos + 5
        if index == 3:
            value = bytes(data[value_start:value_start+size])
            if b':' in value or value.startswith(b'/'):
                portable = value.replace(b'\\', b'/').rsplit(b'/',1)[-1]
                data[value_start:value_start+size] = portable.ljust(size, b' ')
        pos = value_start + size
    if data != original:
        assert len(data) == len(original)
        path.write_bytes(data)
        changed += 1
print('FBX provenance paths sanitized:', changed)
