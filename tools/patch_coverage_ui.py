from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Add XLSX export button to the compact coverage toolbar.
if 'id="covExportXlsx"' not in s:
    old = '<div class="count"><b id="covvisible">0</b> strutture</div></div><div class="wrap">'
    new = '<button id="covExportXlsx" class="primary" type="button" onclick="exportCoverageXlsx()">Esporta XLSX</button><div class="count"><b id="covvisible">0</b> strutture</div></div><div class="wrap">'
    if old not in s:
        raise SystemExit('Coverage toolbar marker not found')
    s = s.replace(old, new, 1)

marker = '<!-- COVERAGE_XLSX_V1 -->'
if marker not in s:
    addon = r'''<!-- COVERAGE_XLSX_V1 -->
<script>
let coverageXlsxLoader=null;
function loadCoverageXlsxLib(){
  if(window.XLSX)return Promise.resolve(window.XLSX);
  if(coverageXlsxLoader)return coverageXlsxLoader;
  coverageXlsxLoader=new Promise((resolve,reject)=>{
    const sc=document.createElement('script');
    sc.src='https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js';
    sc.onload=()=>window.XLSX?resolve(window.XLSX):reject(new Error('Libreria XLSX non disponibile'));
    sc.onerror=()=>reject(new Error('Impossibile caricare la libreria XLSX'));
    document.head.appendChild(sc);
  });
  return coverageXlsxLoader;
}
function coverageRowsForExport(){
  const covOrder=['Elba','Sardegna','Toscana','Corsica'];
  const idx=new Map(covOrder.map((x,i)=>[x,i]));
  const present=r=>r.has_internal_2027===true||r.source_coverage_status==='PRESENTE';
  const q=(document.getElementById('covq')?.value||'').trim().toLowerCase();
  const d=document.getElementById('covdest')?.value||'';
  const st=document.getElementById('covst')?.value||'';
  return (structures||[])
    .filter(r=>r.napoleon_active&&r.live_napoleon_status==='live')
    .filter(r=>{
      const pr=present(r),txt=((r.canonical_name||'')+' '+(r.locality||'')).toLowerCase();
      return(!d||r.destination===d)&&(!st||(st==='present'?pr:!pr))&&(!q||txt.includes(q));
    })
    .sort((a,b)=>(idx.get(a.destination)??99)-(idx.get(b.destination)??99)||String(a.canonical_name||'').localeCompare(String(b.canonical_name||''),'it')||String(a.locality||'').localeCompare(String(b.locality||''),'it'))
    .map(r=>({
      'Catalogo':r.destination||'',
      'Struttura':r.canonical_name||'',
      'Località':r.locality||'',
      'USO INTERNO 2027':present(r)?'PRESENTE':'MANCANTE'
    }));
}
async function exportCoverageXlsx(){
  const rows=coverageRowsForExport();
  if(!rows.length){toastMsg('Nessuna struttura da esportare');return}
  const btn=document.getElementById('covExportXlsx');
  const old=btn?.textContent;
  if(btn){btn.disabled=true;btn.textContent='Preparazione…'}
  try{
    const XLSX=await loadCoverageXlsxLib();
    const ws=XLSX.utils.json_to_sheet(rows,{header:['Catalogo','Struttura','Località','USO INTERNO 2027']});
    ws['!cols']=[{wch:14},{wch:44},{wch:28},{wch:20}];
    if(ws['!ref'])ws['!autofilter']={ref:ws['!ref']};
    const wb=XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb,ws,'Copertura USO INTERNO');
    const d=document.getElementById('covdest')?.value||'TUTTI';
    const st=document.getElementById('covst')?.value==='present'?'PRESENTI':document.getElementById('covst')?.value==='missing'?'MANCANTI':'TUTTI';
    const q=(document.getElementById('covq')?.value||'').trim();
    const safe=v=>String(v).normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^A-Za-z0-9]+/g,'_').replace(/^_+|_+$/g,'').toUpperCase();
    let name=`USO_INTERNO_2027_${safe(d)}_${st}`;
    if(q)name+=`_RICERCA_${safe(q).slice(0,35)}`;
    XLSX.writeFile(wb,name+'.xlsx',{compression:true});
    toastMsg(`${rows.length} strutture esportate in XLSX`);
  }catch(e){toastMsg(e.message||'Errore esportazione XLSX')}
  finally{if(btn){btn.disabled=false;btn.textContent=old||'Esporta XLSX'}}
}
</script>
'''
    s = s.replace('</body>', addon + '</body>', 1)

# Explicitly keep the coverage XLSX export available to every authenticated user.
visibility_marker = '<!-- COVERAGE_EXPORT_ALL_USERS_V1 -->'
if visibility_marker not in s:
    visibility = r'''<!-- COVERAGE_EXPORT_ALL_USERS_V1 -->
<script>
(function(){
  function showCoverageExport(){
    const b=document.getElementById('covExportXlsx');
    if(!b)return;
    b.hidden=false;
    b.removeAttribute('hidden');
    b.style.setProperty('display','inline-block','important');
    b.style.setProperty('visibility','visible','important');
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',showCoverageExport);
  else showCoverageExport();
  setTimeout(showCoverageExport,250);
  setTimeout(showCoverageExport,1000);
})();
</script>
'''
    s = s.replace('</body>', visibility + '</body>', 1)

# Reduce stale HTML on workstations after UI releases.
if 'http-equiv="Cache-Control"' not in s:
    cache_meta = '<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate"><meta http-equiv="Pragma" content="no-cache"><meta http-equiv="Expires" content="0">'
    viewport = '<meta name="viewport" content="width=device-width,initial-scale=1">'
    if viewport in s:
        s = s.replace(viewport, viewport + cache_meta, 1)

p.write_text(s, encoding='utf-8')
print('coverage XLSX export patched for all users')
