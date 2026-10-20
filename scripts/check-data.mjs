import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const data=Object.fromEntries(['games','trailers','gallery','editions'].map(k=>[k,JSON.parse(fs.readFileSync(path.join(root,'data',k+'.json'),'utf8'))]));
let assets=0;
for(const [key,rows] of Object.entries(data)){
  const ids=new Set();
  for(const row of rows){
    assert.match(row.id,/^[a-zA-Z0-9_-]+$/);assert(!ids.has(row.id),`Duplicate ${key}:${row.id}`);ids.add(row.id);
    assert(row.title||row.name,`Missing title ${row.id}`);
    if(row.gameId)assert(data.games.some(g=>g.id===row.gameId),`Missing game ${row.gameId}`);
    if(row.youtubeId)assert.match(row.youtubeId,/^[a-zA-Z0-9_-]{11}$/);
    if(row.date)assert(!Number.isNaN(Date.parse(row.date)));
    for(const field of ['src','thumbnail','image','cover'])if(row[field]?.startsWith('assets/')){assert(fs.existsSync(path.join(root,row[field])),`Missing asset ${row[field]}`);assets++}
    for(const source of row.sources||[row.source])assert(/^https?:\/\//.test(source),`Invalid source ${row.id}`);
  }
}
assert.equal(new Set(data.gallery.map(g=>g.original)).size,data.gallery.length,'Duplicate gallery original');
const context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(root,'data/catalog.js'),'utf8'),context);
assert(JSON.stringify(context.window.GTA_CATALOG)===JSON.stringify(data),'Offline bundle is stale');
console.log(JSON.stringify({status:'PASS',collections:Object.fromEntries(Object.entries(data).map(([k,v])=>[k,v.length])),localAssetReferences:assets,galleryUnique:true,offlineBundleMatches:true},null,2));
