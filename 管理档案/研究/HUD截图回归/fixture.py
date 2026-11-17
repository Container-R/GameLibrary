from PIL import Image, ImageChops, ImageDraw
W, H = 1280, 720
def render(mode):
    im=Image.new('RGB',(W,H),'#1d2b38')
    d=ImageDraw.Draw(im)
    d.rectangle((0,320,31,351),fill='#9bc7d6' if mode=='background' else '#365169')
    d.rectangle((88,88,183,151),fill='#0f151a')
    if mode!='missing':
        x=108 if mode=='moved' else 100
        d.rectangle((x,100,x+31,131),fill='#33a1bd' if mode=='old' else '#ffd23d')
    return im

def diff(a,b):
    return sum(c != (0,0,0) for c in ImageChops.difference(a,b).getdata())

modes=['approved','new','background','missing','moved','old']
images={mode:render(mode) for mode in modes}
for mode, im in images.items(): im.save(mode+'.png')
roi=(88,88,184,152)
anchor=images['approved']
pairs=[(diff(anchor,images[m]),diff(anchor.crop(roi),images[m].crop(roi))) for m in modes[1:]]
assert pairs==[(0,0),(1024,0),(1024,1024),(512,512),(1024,1024)]
follow=diff(anchor.crop((100,100,132,132)),images['moved'].crop((108,100,140,132)))
assert follow==0
print('case        frame  fixed  ROI ratio')
for mode,(full,local) in zip(modes[1:],pairs):
    print(f'{mode:11s} {full:5d} {local:6d} {local/(96*64):9.2%}')
print('moved, following crop:',follow)
sheet=Image.new('RGB',(780,280),'#f1f4f6')
d=ImageDraw.Draw(sheet)
for i,m in enumerate(modes):
    x=(i%3)*260;y=(i//3)*140
    sheet.paste(images[m].crop(roi).resize((192,128),Image.Resampling.NEAREST),(x,y))
    sheet.paste(images[m].crop((0,320,32,352)),(x+200,y+20))
    d.text((x+193,y+64),m,fill='black')
sheet.save('contact.png')
