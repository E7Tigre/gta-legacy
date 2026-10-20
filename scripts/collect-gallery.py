"""Extract actual image records from Rockstar's saved public media HTML.
Run with --download to cache resized viewing copies and thumbnails.
"""
import json, re, html, pathlib, urllib.request, concurrent.futures, sys, io
from PIL import Image
ROOT = pathlib.Path(__file__).resolve().parent.parent
source = 'https://www.rockstargames.com/VI/media/screenshots'
raw = (ROOT/'data/vi-source.html').read_text(encoding='utf-8')
records=[]
headings=[(m.start(),html.unescape(m[1]).strip()) for m in re.finditer(r'<h5\b[^>]*>([^<]+)',raw)]
headings=[(pos,title) for pos,title in headings if title in ['Screenshots','Ultimate Edition Benefits','Vintage Vice City Pack']]
for blockmatch in re.finditer(r'<button\b[^>]*aria-label="Open download dialog[^>]*>.*?</button>', raw, re.S):
    block=blockmatch[0]
    section=next((title for pos,title in reversed(headings) if pos<blockmatch.start()),'Screenshots')
    title = html.unescape(re.search(r'aria-label="Open download dialog - (.*?) - \d+ size',block)[1])
    match=re.search(r'\ssrc="([^"]+)"',block)
    if not match: continue
    url=html.unescape(match[1])
    if url.startswith('/'): url='https://www.rockstargames.com'+url
    if any(r['original']==url for r in records): continue
    group=re.sub(r' \d+$','',title)
    category=('Localizaciones' if any(x in group for x in ['Vice City','Leonida','Port Gellhorn','Ambrosia','Grassrivers','Mount Kalaga']) else 'Personajes') if section=='Screenshots' else 'Contenido adicional'
    ident='vi-'+str(len(records)+1).zfill(3)
    records.append(dict(id=ident,title=title,category=category,subject=group,officialSection=section,kind='Captura oficial' if category!='Contenido adicional' else 'Captura de contenido adicional',original=url,src=url,thumbnail=url.replace('imwidth=3840','imwidth=640'),source=source,collectedAt='2026-10-19',verification='Fuente oficial',local=False))
if not records: raise SystemExit('No image records found; source layout may have changed')
# The source page's section boundaries distinguish general screenshots from extras.
def download(r):
    dest=ROOT/'assets/gallery'/f"{r['id']}.jpg";thumb=ROOT/'assets/thumbs'/f"{r['id']}.jpg"
    try:
        if not dest.exists():
            req=urllib.request.Request(r['original'].replace('imwidth=3840','imwidth=1920'),headers={'User-Agent':'Mozilla/5.0'})
            with urllib.request.urlopen(req,timeout=45) as response: content=response.read()
            im=Image.open(io.BytesIO(content)).convert('RGB');im.thumbnail((1920,1920));im.save(dest,quality=86,optimize=True)
        im=Image.open(dest);im.thumbnail((640,640));im.save(thumb,quality=80,optimize=True)
        r.update(src=f'assets/gallery/{r["id"]}.jpg',thumbnail=f'assets/thumbs/{r["id"]}.jpg',local=True)
        return True
    except Exception as e:
        r['downloadError']=str(e);return False
if '--download' in sys.argv:
    (ROOT/'assets/gallery').mkdir(parents=True,exist_ok=True);(ROOT/'assets/thumbs').mkdir(parents=True,exist_ok=True)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool: results=list(pool.map(download,records))
    print('Downloaded',sum(results),'of',len(records))
(ROOT/'data/gallery.json').write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print('Extracted',len(records),'unique image records')
