"""Normalize absolute document paths in binary FBX metadata without changing mesh data."""
from pathlib import Path
import re,struct

def sanitize(path):
    data=bytearray(path.read_bytes())
    assert data.startswith(b'Kaydara FBX Binary  \x00\x1a\x00')
    version=struct.unpack_from('<I',data,23)[0]
    fmt='<QQQB' if version>=7500 else '<IIIB'
    header=struct.calcsize(fmt);edits=[]
    def node(at):
        end,count,plen,nlen=struct.unpack_from(fmt,data,at)
        if not end:return at+header
        pos=at+header+nlen;prop_end=pos+plen
        for _ in range(count):
            kind=chr(data[pos]);pos+=1
            if kind in 'YCFDIL':pos+={'Y':2,'C':1,'F':4,'D':8,'I':4,'L':8}[kind]
            elif kind in 'fdilbc':
                _,_,packed=struct.unpack_from('<III',data,pos);pos+=12+packed
            elif kind in 'SR':
                size=struct.unpack_from('<I',data,pos)[0];pos+=4
                value=bytes(data[pos:pos+size])
                if kind=='S' and re.match(rb'^[A-Za-z]:[\\/]',value):
                    replacement=re.split(rb'[/\\]',value)[-1]
                    data[pos:pos+size]=replacement.ljust(size,b' ');edits.append(size)
                pos+=size
            else:raise ValueError('Unknown FBX property type: '+kind)
        assert pos==prop_end
        while pos<end:
            if not any(data[pos:pos+header]):pos+=header;break
            pos=node(pos)
        assert pos==end
        return end
    offset=27
    while any(data[offset:offset+header]):offset=node(offset)
    assert len(data)==path.stat().st_size
    if edits:path.write_bytes(data)
    return len(edits)

if __name__=='__main__':
    root=Path(__file__).resolve().parents[1]/'Assets/GTA/Generated'
    print('Normalized FBX metadata fields:',sum(sanitize(p) for p in root.rglob('*.fbx')))
