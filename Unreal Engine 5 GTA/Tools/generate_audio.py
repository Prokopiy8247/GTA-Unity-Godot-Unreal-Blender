from pathlib import Path
import math,random,wave,struct
root=Path('SourceAssets/Audio');root.mkdir(parents=True,exist_ok=True)
random.seed(77);rate=24000
def sound(name,duration,fn):
    n=int(rate*duration);last=0;samples=[]
    for i in range(n):
        t=i/rate;v=fn(t,random.uniform(-1,1));v=max(-.98,min(.98,v));samples.append(int(v*32767))
    with wave.open(str(root/(name+'.wav')),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
sound('Shot',.5,lambda t,n:(n*.8+math.sin(t*470)*.3)*math.exp(-t*22))
sound('Explosion',2,lambda t,n:(n*.6+math.sin(t*170)*.4)*math.exp(-t*3))
sound('Impact',.5,lambda t,n:(n*.6+math.sin(t*420)*.3)*math.exp(-t*13))
sound('Footstep',.16,lambda t,n:(n*.35+math.sin(t*520)*.2)*math.exp(-t*40))
sound('Reload',.8,lambda t,n:n*.28*(math.exp(-abs(t-.1)*90)+math.exp(-abs(t-.45)*80)+math.exp(-abs(t-.65)*65)))
sound('Engine',2,lambda t,n:(math.sin(2*math.pi*60*t)*.25+math.sin(2*math.pi*120*t)*.18+math.sin(2*math.pi*180*t)*.07+n*.04))
sound('Rotor',2,lambda t,n:(n*.22+math.sin(t*2*math.pi*75)*.18)*(.3+.7*abs(math.sin(t*2*math.pi*12))))
sound('Siren',4,lambda t,n:math.sin(2*math.pi*(650*t-200/(2*math.pi*.5)*math.cos(2*math.pi*.5*t)))*.32)
sound('Horn',.7,lambda t,n:(math.sin(2*math.pi*340*t)+math.sin(2*math.pi*425*t))*.21*min(1,t*40)*min(1,(.7-t)*30))
sound('Rain',4,lambda t,n:n*.13)
sound('City',4,lambda t,n:n*.02+math.sin(t*math.pi*80)*.015+math.sin(t*math.pi*112)*.01)
sound('Ocean',6,lambda t,n:n*.1*(.55+.45*math.sin(t*math.pi/3)))
