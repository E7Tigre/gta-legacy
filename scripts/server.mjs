import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const types={'.html':'text/html; charset=utf-8','.css':'text/css; charset=utf-8','.js':'text/javascript; charset=utf-8','.json':'application/json; charset=utf-8','.jpg':'image/jpeg','.png':'image/png','.webp':'image/webp','.md':'text/plain; charset=utf-8'};
const port=Number(process.env.PORT||8080);
http.createServer((req,res)=>{
  try{
    if(!['GET','HEAD'].includes(req.method)){res.writeHead(405);return res.end()}
    const pathname=decodeURIComponent(new URL(req.url,'http://localhost').pathname);
    const file=path.resolve(root,'.'+(pathname==='/'?'/index.html':pathname));
    if(!file.startsWith(root+path.sep)){res.writeHead(403);return res.end()}
    if(!fs.existsSync(file)||!fs.statSync(file).isFile()){res.writeHead(404);return res.end('Recurso no disponible')}
    res.writeHead(200,{'Content-Type':types[path.extname(file)]||'application/octet-stream','Content-Length':fs.statSync(file).size,'X-Content-Type-Options':'nosniff','Cache-Control':'no-cache'});
    if(req.method==='HEAD')res.end();else fs.createReadStream(file).pipe(res);
  }catch{res.writeHead(400);res.end('Solicitud no valida')}
}).listen(port,'127.0.0.1',()=>console.log(`GTA Legacy: http://127.0.0.1:${port}`));
