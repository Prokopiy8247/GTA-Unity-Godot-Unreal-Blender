import wave, math, random, struct
from pathlib import Path
random.seed(817)
out=Path('gta/generated/audio');out.mkdir(parents=True,exist_ok=True)
rate=22050
def save(name,duration,fn,loop=False):
    count=int(duration*rate)
    last=0.
    samples=[]
    for i in range(count):
        t=i/rate
        value=fn(t,i/count)
        fade=min(1,i/180,(count-i)/350) if not loop else 1
        samples.append(struct.pack('<h',int(max(-1,min(1,value*fade))*.68*32767)))
    with wave.open(str(out/(name+'.wav')),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(b''.join(samples))
    if loop:
        (out/(name+'.wav.import')).write_text('[remap]\nimporter="wav"\ntype="AudioStreamWAV"\n\n[deps]\nsource_file="res://gta/generated/audio/'+name+'.wav"\n\n[params]\nedit/loop_mode=2\n',encoding='utf-8')
noise=lambda:random.uniform(-1,1)
save('shot',.34,lambda t,p:(noise()*.7+math.sin(t*420)*.3)*math.exp(-t* 20))
save('explosion',2.3,lambda t,p:(noise()*.5+math.sin(t*100)*.4+math.sin(t*61)*.2)*math.exp(-t*2.4))
save('impact',.27,lambda t,p:(noise()*.5+math.sin(t*330)*.3)*math.exp(-t* 18))
save('step',.17,lambda t,p:noise()*.4*math.exp(-t* 20))
save('door',.38,lambda t,p:(noise()*.35+math.sin(t*230)*.3)*math.exp(-t*11))
save('reload',.7,lambda t,p:noise()*.35*(math.exp(-abs(t-.08)* 80)+math.exp(-abs(t-.36)* 70)+math.exp(-abs(t-.56)* 60)))
save('horn',.65,lambda t,p:(math.sin(t*math.tau*350)+math.sin(t*math.tau*440))*.28)
save('ui',.13,lambda t,p:math.sin(t*math.tau*(650+1000*t))*.25*math.exp(-t*12))
save('engine',2,lambda t,p:(math.sin(math.tau* 50*t)+.5*math.sin(math.tau*100*t)+.23*math.sin(math.tau*150*t)+noise()*.08)*.3,True)
save('siren',4,lambda t,p:math.sin(math.tau*(640*t+130/math.pi*(1-math.cos(t*math.pi))))*.6,True)
save('rain',6,lambda t,p:noise()*.24,True)
save('ambient',8,lambda t,p:noise()*.07+math.sin(math.tau* 70*t)*.035+math.sin(math.tau*114*t)*.025,True)
chord=[110,138.59,164.81,220]
save('radio',16,lambda t,p:sum(math.sin(math.tau*f*t)*.035 for f in chord)+math.sin(math.tau*55*t)*(.15*math.exp(-(t%.5)* 20)),True)
print('Generated 13 original audio assets')
