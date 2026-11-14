"""Original ideal pinhole projection, with no depth scaling or engine dependency."""
from pathlib import Path

f = 600
camera = (512, 230)

def silhouette(points, x, y, z, color):
    projected = [(camera[0] + f*(x+dx)/z, camera[1] - f*(y+dy)/z) for dx,dy in points]
    a, b = min(p[0] for p in projected), max(p[0] for p in projected)
    path = ' '.join(f'{px:g},{py:g}' for px,py in projected)
    return f'<polygon points="{path}" fill="{color}" />', a, b

ship = [(-100,-12),(-78,18),(32,18),(60,10),(100,0),(76,-15),(-88,-15)]
shuttle = [(-10,-2),(-7,2),(3,3),(10,0),(5,-2)]
cases = [("A", 1000, 115, 26), ("B", 100, 11.5, 2.6)]
colors = ['#86c5e8','#ffce6b']
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="424" viewBox="0 0 1024 424" role="img">',
       '<title>Same camera, same ship, different shuttle depth</title>',
       '<rect width="1024" height="424" fill="#131e2b" />',
       '<text fill="#f0f5ff" x="512" y="45" font-size="28" text-anchor="middle">Same camera, same ship, different shuttle depth</text>']
for i, (name,z,x,y) in enumerate(cases):
    dx = -256 if i == 0 else 256
    out.append(f'<g transform="translate({dx} 0)">')
    out.append(f'<rect x="278" y="77" width="468" height="314" rx="13" fill="#203040" />')
    out.append(f'<text fill="#f0f5ff" x="512" y="113" font-size="23" text-anchor="middle">{name} / Shuttle depth: {z} m</text>')
    for j, (poly, cx, cy, cz) in enumerate([(ship,-115,-26,1000),(shuttle,x,y,z)]):
        mark,left,right = silhouette(poly,cx,cy,cz,colors[j])
        width = right-left
        assert width == ([120,12] if i==0 else [120,120])[j]
        print(name, 'ship' if j==0 else 'shuttle', f'z={cz:g}m width={width:g}px')
        out.append(mark)
        row = 284 if j == 0 else 166
        c = colors[j]
        out.append(f'<path d="M{left:g},{row-6}v12 M{left:g},{row}H{right:g} M{right:g},{row-6}v12" stroke="{c}" stroke-width="2" fill="none" />')
        label_y = row+34 if j==0 else row-14
        out.append(f'<text x="{(left+right)/2:g}" y="{label_y}" fill="{c}" font-size="20" text-anchor="middle">{width:g} px</text>')
    out.append('<text fill="#f0f5ff" x="512" y="365" font-size="19" text-anchor="middle">Ship: 200 m wide · Shuttle: 20 m wide</text></g>')
out.append('<style>text {font-family: DejaVu Sans, sans-serif;}</style></svg>')
Path(__file__).with_name('projection-comparison.svg').write_text('\n'.join(out)+'\n')
