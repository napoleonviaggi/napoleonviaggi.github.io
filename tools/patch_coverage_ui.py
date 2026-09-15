from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

s = s.replace(
    '<button class="tab" data-p="coverage">Copertura</button>',
    '<button class="tab" data-p="coverage">Copertura USO INTERNO</button>'
)

old = '<section id="p-coverage" class="panel"><div id="coverage"></div></section>'
new = '''<section id="p-coverage" class="panel"><div id="coverage" style="display:none"></div><div class="card" style="padding:8px 10px"><b>Copertura USO INTERNO 2027</b><span id="covSummary" class="small" style="margin-left:10px"></span></div><div class="toolbar"><div class="field search"><label>Ricerca</label><input id="covq" placeholder="Struttura o località"></div><div class="field"><label>Catalogo</label><select id="covdest"><option value="">Tutti</option><option>Elba</option><option>Sardegna</option><option>Toscana</option><option>Corsica</option></select></div><div class="field"><label>USO INTERNO</label><select id="covst"><option value="">Tutti</option><option value="present">Presenti</option><option value="missing">Mancanti</option></select></div><div class="count"><b id="covvisible">0</b> strutture</div></div><div class="wrap"><table style="table-layout:auto"><thead><tr><th style="width:10%">Catalogo</th><th>Struttura</th><th style="width:22%">Località</th><th style="width:16%">USO INTERNO 2027</th></tr></thead><tbody id="covbody"></tbody></table></div></section>'''

if old in s:
    s = s.replace(old, new, 1)
elif 'id="covbody"' not in s:
    raise SystemExit('Coverage section marker not found')

marker = '<!-- COVERAGE_COMPACT_V1 -->'
if marker not in s:
    addon = r'''<!-- COVERAGE_COMPACT_V1 -->
<script>
(function(){
  const covOrder=['Elba','Sardegna','Toscana','Corsica'];
  function covPresent(r){return r.has_internal_2027===true || r.source_coverage_status==='PRESENTE'}
  function renderCoverageCompact(){
    const body=document.getElementById('covbody'); if(!body)return;
    const active=(structures||[]).filter(r=>r.napoleon_active&&r.live_napoleon_status==='live');
    const q=(document.getElementById('covq')?.value||'').trim().toLowerCase();
    const d=document.getElementById('covdest')?.value||'';
    const st=document.getElementById('covst')?.value||'';
    const idx=new Map(covOrder.map((x,i)=>[x,i]));
    const rr=active.filter(r=>{
      const pr=covPresent(r),txt=((r.canonical_name||'')+' '+(r.locality||'')).toLowerCase();
      return(!d||r.destination===d)&&(!st||(st==='present'?pr:!pr))&&(!q||txt.includes(q));
    }).sort((a,b)=>(idx.get(a.destination)??99)-(idx.get(b.destination)??99)||String(a.canonical_name||'').localeCompare(String(b.canonical_name||''),'it')||String(a.locality||'').localeCompare(String(b.locality||''),'it'));
    body.innerHTML=rr.map(r=>{const pr=covPresent(r);return `<tr style="background:${pr?'#eefaf3':'#fff2f2'}"><td><b>${esc(r.destination)}</b></td><td><b>${esc(r.canonical_name)}</b></td><td>${esc(r.locality)}</td><td><span class="badge ${pr?'green':'red'}">${pr?'PRESENTE':'MANCANTE'}</span></td></tr>`}).join('');
    const v=document.getElementById('covvisible');if(v)v.textContent=rr.length;
    const total=active.length,covered=active.filter(covPresent).length;
    const parts=covOrder.map(x=>{const z=active.filter(r=>r.destination===x),c=z.filter(covPresent).length;return `${x} ${c}/${z.length}`});
    const sm=document.getElementById('covSummary');if(sm)sm.textContent=`Totale ${covered}/${total} · ${parts.join(' · ')}`;
  }
  const oldRS=renderStructures;
  renderStructures=function(){const x=oldRS.apply(this,arguments);renderCoverageCompact();return x};
  ['covq','covdest','covst'].forEach(id=>{const el=document.getElementById(id);if(el)el.addEventListener(id==='covq'?'input':'change',renderCoverageCompact)});
  const tab=document.querySelector('.tab[data-p="coverage"]');if(tab)tab.addEventListener('click',()=>setTimeout(renderCoverageCompact,0));
  setTimeout(renderCoverageCompact,500);
})();
</script>
'''
    s = s.replace('</body>', addon + '</body>', 1)

p.write_text(s, encoding='utf-8')
print('coverage UI patched')
