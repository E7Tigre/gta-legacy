"""Cache only already documented URLs; retain original provenance."""
import json,pathlib,urllib.request,concurrent.futures,io
from PIL import Image
root=pathlib.Path(__file__).resolve().parent.parent
cache={}
for name,field,folder in [('editions','image','editions'),('trailers','thumbnail','trailers'),('games','cover','covers')]:
    path=root/'data'/f'{name}.json'; rows=json.loads(path.read_text(encoding='utf-8-sig'));(root/'assets'/folder).mkdir(exist_ok=True)
    def fetch(r):
        url=r.get(field)
        if not url or not url.startswith('https://'): return
        dest=root/'assets'/folder/(r['id']+'.jpg')
        try:
            if not dest.exists():
                req=urllib.request.Request(url,headers={'User-Agent':'GTA-Legacy-Archive/1.0 (personal offline research)'})
                with urllib.request.urlopen(req,timeout=25) as response: b=response.read()
                im=Image.open(io.BytesIO(b)).convert('RGB');im.thumbnail((1400,1400));im.save(dest,quality=85)
            r[field+'OriginalUrl']=url;r[field]=f'assets/{folder}/{r["id"]}.jpg'
        except Exception as e: print(name,r['id'],str(e))
    # Sequential requests avoid hammering Wikimedia; existing files are never re-fetched.
    for row in rows: fetch(row)
    path.write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
    print(name,'local',sum(str(r.get(field,'')).startswith('assets/') for r in rows))
