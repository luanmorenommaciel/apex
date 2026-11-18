import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import assert from 'node:assert/strict';
import { JSDOM, VirtualConsole } from '../../../front/node_modules/jsdom/lib/api.js';

const folder=fileURLToPath(new URL('./',import.meta.url));
const html=readFileSync(folder+'2026-11-09-apresentacao-mvp-deck.html','utf8');
const issues=[];
const vc=new VirtualConsole();
vc.on('jsdomError',error=>issues.push(error.message));
const dom=new JSDOM(html,{url:'http://localhost/deck.html#8',runScripts:'dangerously',virtualConsole:vc});
const {window:w}=dom;
const d=w.document;
const results=[];
function check(name, fn) { fn(); results.push({name,status:'pass'}); }
function active(){ return [...d.querySelectorAll('.slide')].findIndex(s=>s.classList.contains('active'))+1; }
function key(value){d.dispatchEvent(new w.KeyboardEvent('keydown',{key:value,bubbles:true,cancelable:true}));}
check('19 slides and working hash entry',()=>{assert.equal(d.querySelectorAll('.slide').length,19);assert.equal(active(),8);});
check('all slides reachable with matching hash and counter',()=>{
  key('Home');
  for(let n=1;n<=19;n++){
    assert.equal(active(),n);
    assert.equal(w.location.hash,'#'+n);
    assert.equal(d.querySelector('#hud').textContent,n<=16 ? n+' / 16' : 'Apêndice '+(n-16)+' / 3');
    const expectedProgress=n<=16 ? n/16*100 : (n-16)/3*100;
    assert(Math.abs(parseFloat(d.querySelector('#progress').style.width)-expectedProgress)<0.001);
    if(n===16) key('a'); else if(n<19) key('ArrowRight');
  }
});
check('closing slide does not advance into appendix',()=>{
  key('Escape');assert.equal(active(),16);
  key('ArrowRight');assert.equal(active(),16);
  d.body.dispatchEvent(new w.MouseEvent('click',{bubbles:true,clientX:900}));assert.equal(active(),16);
});
check('appendix opens deliberately and Escape returns',()=>{key('a');assert.equal(active(),17);key('ArrowRight');assert.equal(active(),18);key('Escape');assert.equal(active(),16);});
check('notes drawer toggles and Escape hides it',()=>{key('Home');key('n');assert(d.querySelector('#notes').classList.contains('on'));key('Escape');assert(!d.querySelector('#notes').classList.contains('on'));});
check('embedded source image byte-matches published evidence',()=>{
  const src=d.querySelector('[data-image-zoom] img').getAttribute('src');
  const bytes=Buffer.from(src.split(',')[1],'base64');
  assert(bytes.equals(readFileSync(folder+'2026-11-16-demo-evidence/console-20261028.png')));
});
// JSDOM does not implement native HTMLDialogElement.showModal/close.
// Stub only that platform boundary; this checks the real click/key wiring.
const viewer=d.querySelector('#image-viewer');
viewer.showModal=function(){this.open=true;};
viewer.close=function(){this.open=false;};
check('image click/key wiring without slide advance (native dialog API stubbed)',()=>{
  for(let n=1;n<8;n++)key('ArrowRight');
  d.querySelector('[data-image-zoom]').click();
  assert(d.querySelector('#image-viewer').open);
  assert.equal(active(),8);
  assert.equal(d.querySelector('#image-viewer img').src,d.querySelector('[data-image-zoom] img').src);
  key('ArrowRight');assert.equal(active(),8);
  key('Escape');assert(!viewer.open);assert.equal(active(),8);
  d.querySelector('[data-image-zoom]').click();
  d.querySelector('#image-viewer button').click();
  assert(!d.querySelector('#image-viewer').open);assert.equal(active(),8);
});
check('visible evidence boundaries remain in the main slides',()=>{
  const slides=[...d.querySelectorAll('.slide')];
  for (const [index,expected] of [[7,'Captura real · 28/10/2026'],[8,'Plano B'],[9,'alguns PRs seguem abertos'],[10,'zero replays']])assert(slides[index].textContent.includes(expected));
});
check('no runtime errors during navigation',()=>assert.deepEqual(issues,[]));
const receipt={deck_sha256:createHash('sha256').update(html).digest('hex'),checks:results,scope:'DOM runtime checks in JSDOM; native dialog API stubbed for event-wiring checks. Not pixel layout, browser-native dialog, projector or real integration proof'};
if (process.argv.includes('--write-receipt')) {
  writeFileSync(folder+'2026-11-16-demo-evidence/design-final-checks.json',JSON.stringify(receipt,null,2)+'\n');
}
console.log(JSON.stringify(receipt,null,2));
dom.window.close();
