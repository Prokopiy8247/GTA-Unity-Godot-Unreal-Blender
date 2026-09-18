import math,random,struct,zlib
from pathlib import Path
random.seed(817)
out=Path("gta/generated/textures");out.mkdir(parents=True,exist_ok=True)
def png(path,w,h,rows):
    def chunk(k,v):return struct.pack(">I",len(v))+k+v+struct.pack(">I",zlib.crc32(k+v)&0xffffffff)
    data=b"".join(b"\0"+bytes(r) for r in rows)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",struct.pack(">IIBBBBB",w,h,8,2,0,0,0))+chunk(b"IDAT",zlib.compress(data,7))+chunk(b"IEND",b""))
colors={"concrete":(.43,.42,.38),"plaster":(.66,.63,.54),"brick":(.29,.13,.082),"wood":(.22,.105,.037),"cloth":(.075,.1,.115),"denim":(.042,.085,.135),"shirt":(.36,.31,.21),"uniform":(.024,.047,.087),"skin":(.48,.285,.17),"skin2":(.22,.115,.071),"skin3":(.72,.48,.31),"rubber":(.014,.017,.021)}
for name,color in colors.items():
    rows=[]
    for y in range(256):
        row=[]
        for x in range(256):
            n=random.uniform(-.06,.06)
            value=1+n
            if name=="brick":
                mortar=y%32<2 or ((x+(64 if (y//32)%2 else 0))%128)<2
                value=.47 if mortar else .85+.22*math.sin((x//128+y//32)*24)+n
            elif name=="wood":value=.87+.12*math.sin(x*.28+math.sin(y*.03)*3)+n
            elif name in ["cloth","denim","shirt","uniform"]:
                value=.97+.018*((x+y)%3)+n*.25
            elif name in ["concrete","plaster"]:
                value=.93+.04*math.sin(x*.1)*math.sin(y*.1)+n
                if random.random()<.009:value*=.65
            elif name.startswith("skin"):value=1+random.uniform(-.023,.023)
            elif name=="rubber":value=.65 if x%18<2 else 1+n
            row.extend(int(min(255,max(0,(c*value)**(1/2.2)*255))) for c in color)
        rows.append(row)
    png(out/(name+".png"),256,256,rows)
print("Created 12 original procedural PBR base-color textures")
