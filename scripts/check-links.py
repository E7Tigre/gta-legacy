"""Read-only HTTP availability audit. A 403/429 is not proof a source is absent."""
import json,pathlib,urllib.request,urllib.error,urllib.parse,concurrent.futures,collections,sys
root=pathlib.Path(__file__).resolve().parent.parent
urls=set()
for key in ['games','trailers','editions']:
    for row in json.loads((root/'data'/f'{key}.json').read_text(encoding='utf-8')):
        urls.update(row.get('sources',[]))
        if row.get('url'): urls.add(row['url'])
urls.add('https://www.rockstargames.com/VI/media/screenshots')
previous=[]
if '--retry-errors' in sys.argv and (root/'data/link-audit.json').exists():
    previous=json.loads((root/'data/link-audit.json').read_text(encoding='utf-8'))
    urls={r['url'] for r in previous if r['status'] is None}
    previous=[r for r in previous if r['status'] is not None]
def check(url):
    try:
        req=urllib.request.Request(urllib.parse.quote(url,safe=':/?&=%'),method='HEAD',headers={'User-Agent':'Mozilla/5.0'})
        with urllib.request.urlopen(req,timeout=15) as res:return dict(url=url,status=res.status,finalUrl=res.url,checkedAt='2026-10-19')
    except urllib.error.HTTPError as e:return dict(url=url,status=e.code,note='HTTP HEAD; restriction or unavailable resource',checkedAt='2026-10-19')
    except Exception as e:return dict(url=url,status=None,note=str(e),checkedAt='2026-10-19')
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=previous+list(pool.map(check,sorted(urls)))
(root/'data/link-audit.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
print(dict(collections.Counter(str(r['status']) for r in results)))
