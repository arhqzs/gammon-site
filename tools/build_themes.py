# -*- coding: utf-8 -*-
import re, os, json

SRC = r"C:\Users\Daniel Lehmann\Downloads\Gammon Themes (shareable).html"
REPO = r"C:\Users\Daniel Lehmann\Documents\backgammon main site"
SCRATCH = r"C:\Users\DANIEL~1\AppData\Local\Temp\claude\C--Users-Daniel-Lehmann-Documents-backgammon-main-site\523e6d0f-cfae-4e2d-9fee-c24f6265f9e1\scratchpad"
OUT = os.path.join(REPO, "designs")
os.makedirs(OUT, exist_ok=True)

h = open(SRC, encoding="utf-8", errors="replace").read()
t = json.loads(re.search(r'type="__bundler/template">(.*?)</script>', h, re.S).group(1))
comp = [c for c in re.findall(r'<script[^>]*>(.*?)</script>', t, flags=re.S) if 'THEMES' in c][0]

FONTS_URL = ("https://fonts.googleapis.com/css2?"
 "family=Archivo:wght@400;500;600;700;800;900&"
 "family=Bricolage+Grotesque:opsz,wght@12..96,400;12..96,500;12..96,600;12..96,700;12..96,800&"
 "family=Cormorant+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&"
 "family=EB+Garamond:ital,wght@0,400;0,500;0,600;0,700;1,400&"
 "family=Hanken+Grotesk:wght@400;500;600;700;800;900&"
 "family=Instrument+Serif:ital@0;1&"
 "family=Schibsted+Grotesk:wght@400;500;600;700;800;900&"
 "family=Space+Grotesk:wght@400;500;600;700&"
 "family=Space+Mono:wght@400;700&"
 "family=Spectral:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap")

def head(title, extra=""):
    return f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gammon — {title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS_URL}" rel="stylesheet">
<style>*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}body{{font-family:'Hanken Grotesk','Archivo',system-ui,sans-serif}}{extra}</style>
</head>
<body>
"""

def clean(body):
    body = re.sub(r'</?sc-(if|for)[^>]*>', '', body)
    body = re.sub(r'\s+hint-placeholder-val="[^"]*"', '', body)
    body = re.sub(r'</?x-dc[^>]*>', '', body)
    return body.strip()

# ---------- 1) 42 hand-built themes (bound each by its own first </sc-if>) ----------
meta = re.findall(r"\{\s*key:'([^']+)',\s*name:'([^']+)',\s*dot1:'([^']+)',\s*dot2:'([^']+)'\s*\}",
                  re.search(r'THEMES\s*=\s*\[(.*?)\];', comp, re.S).group(1))
opens = sorted([(m.start(), m.end(), int(m.group(1)))
                for m in re.finditer(r'<sc-if value="\{\{ s(\d{1,3}) \}\}"[^>]*>', t)], key=lambda x: x[2])
assert len(meta) == len(opens) == 42, (len(meta), len(opens))

studio = []
keep = set()
for i, (s, e, num) in enumerate(opens):
    close = t.index('</sc-if>', e)          # own closing tag (sections don't nest)
    body = clean(t[e:close])
    key, name, d1, d2 = meta[i]
    nn = f"{i+1:02d}"
    fn = f"theme-{nn}-{key}.html"; keep.add(fn)
    open(os.path.join(OUT, fn), "w", encoding="utf-8").write(head(name) + body + "\n</body></html>\n")
    studio.append({"n": nn, "file": f"../designs/{fn}", "title": name, "sw": d1, "sw2": d2})

# ---------- 2) generic engine data ----------
fonts_txt = re.search(r'FONTS\s*=\s*\[(.*?)\];', comp, re.S).group(1)
FONTS = re.findall(r'"((?:[^"\\]|\\.)*)"', fonts_txt)
pool_txt = re.search(r'POOL\s*=\s*\[(.*?)\];', comp, re.S).group(1)
POOL = [{"t": a, "k": b} for a, b in re.findall(r"\{t:'((?:[^'\\]|\\.)*)',k:'((?:[^'\\]|\\.)*)'\}", pool_txt)]
graw_txt = comp[comp.find('GEN_RAW = ['):comp.index('];', comp.find('GEN_RAW = ['))]
tup = re.findall(r"\['([^']+)','([^']+)',(\d+),'([dl])','([^']+)','([^']+)','([^']+)','([^']+)','([^']+)',(\d+),(\d+),(\d+)\]", graw_txt)
GEN = [{"key":r[0],"name":r[1],"arch":int(r[2]),
        "spec":{"mode":r[3],"bg":r[4],"ink":r[5],"acc":r[6],"on":r[7],"acc2":r[8],
                "disp":FONTS[int(r[9])],"body":FONTS[int(r[10])],"rad":int(r[11])}} for r in tup]
print("FONTS", len(FONTS), "POOL", len(POOL), "GEN", len(GEN))
assert len(GEN) == 108 and len(POOL) == 12 and len(FONTS) == 10

# ---------- 3) extract the 6 architecture templates ----------
gi = t.index('<sc-if value="{{ isGeneric }}"')
gblock = t[gi:]
genroot_open = re.search(r'<div id="gen-root"[^>]*>', gblock).group(0)
arch_html = {}
for aopen in re.finditer(r'<sc-if value="\{\{ (g[A-F]) \}\}"[^>]*>', gblock):
    name = aopen.group(1)
    close = gblock.index('</sc-if>', aopen.end())
    inner = clean(gblock[aopen.end():close])
    inner = inner.replace('{{ g.title }}', '<span data-g="title"></span>')
    inner = inner.replace('{{ g.kicker }}', '<span data-g="kicker"></span>')
    inner = inner.replace('{{ g.name }}', '<span data-g="name"></span>')
    assert '{{' not in inner, ("leftover interp in", name, inner[inner.find('{{'):inner.find('{{')+40])
    arch_html[name] = inner
assert set(arch_html) == set(['gA','gB','gC','gD','gE','gF']), arch_html.keys()

# ---------- 4) write designs/gen.html ----------
archs_dom = "\n".join(f'<div class="arch" data-arch="{k}">{arch_html[k]}</div>' for k in ['gA','gB','gC','gD','gE','gF'])
extra_css = "#gen-root{min-height:100vh;background-color:var(--g-bg);color:var(--g-ink);font-family:var(--g-body)}.arch{display:none}.arch.on{display:block}"
gen_js = f"""
const FONTS={json.dumps(FONTS)};
const POOL={json.dumps(POOL, ensure_ascii=False)};
const GEN={json.dumps(GEN, ensure_ascii=False)};
const OFFSET=42, ARCH=['gA','gB','gC','gD','gE','gF'];
function applyVars(s){{
  const el=document.getElementById('gen-root');
  const mix=(a,p,b)=>`color-mix(in srgb, ${{a}} ${{p}}%, ${{b}})`;
  const V={{'--g-bg':s.bg,'--g-ink':s.ink,'--g-acc':s.acc,'--g-on':s.on,'--g-acc2':s.acc2,'--g-disp':s.disp,'--g-body':s.body,
    '--g-rad':s.rad+'px','--g-rbtn':Math.min(s.rad,14)+'px','--g-surface':mix(s.bg,90,s.ink),'--g-surface2':mix(s.bg,82,s.ink),
    '--g-line':mix(s.ink,15,'transparent'),'--g-line2':mix(s.ink,32,'transparent'),'--g-dim':mix(s.ink,80,s.bg),
    '--g-muted':mix(s.ink,56,s.bg),'--g-soft':mix(s.acc,15,'transparent'),'--g-felt':mix(s.acc2,58,'#0c110d'),
    '--g-frame':mix(s.bg,60,s.ink),'--g-p1':s.acc,'--g-p2':s.acc2}};
  for(const k in V) el.style.setProperty(k,V[k]);
}}
function render(){{
  const key=(location.hash||'').replace('#','');
  let i=GEN.findIndex(t=>t.key===key); if(i<0) i=0;
  const t=GEN[i]; applyVars(t.spec);
  const p=POOL[(OFFSET+i)%POOL.length];
  document.querySelectorAll('.arch').forEach(el=>el.classList.remove('on'));
  const el=document.querySelector('.arch[data-arch="'+(ARCH[t.arch]||'gA')+'"]'); if(el) el.classList.add('on');
  document.querySelectorAll('[data-g="title"]').forEach(n=>n.textContent=p.t);
  document.querySelectorAll('[data-g="kicker"]').forEach(n=>n.textContent=p.k);
  document.querySelectorAll('[data-g="name"]').forEach(n=>n.textContent=t.name);
  document.title='Gammon — '+t.name;
}}
window.addEventListener('hashchange',render); render();
"""
gen_doc = head("Design", extra_css) + f'<div id="gen-root">\n{archs_dom}\n</div>\n<script>{gen_js}</script>\n</body></html>\n'
open(os.path.join(OUT, "gen.html"), "w", encoding="utf-8").write(gen_doc)
keep.add("gen.html")
print("gen.html bytes:", len(gen_doc))

# ---------- 5) append generic themes to studio list ----------
for i, g in enumerate(GEN):
    nn = f"{42+i+1:02d}"
    studio.append({"n": nn, "file": f"../designs/gen.html#{g['key']}", "title": g["name"],
                   "sw": g["spec"]["acc"], "sw2": g["spec"]["acc2"]})

# clean stale design files
for f in os.listdir(OUT):
    if f.endswith(".html") and f not in keep:
        os.remove(os.path.join(OUT, f)); print("removed stale", f)

with open(os.path.join(SCRATCH, "studio_themes.js"), "w", encoding="utf-8") as f:
    f.write("const THEMES = [\n")
    for x in studio:
        f.write(f'  {{n:"{x["n"]}", file:{json.dumps(x["file"])}, title:{json.dumps(x["title"], ensure_ascii=False)}, sw:"{x["sw"]}", sw2:"{x["sw2"]}"}},\n')
    f.write("];\n")
print("TOTAL studio themes:", len(studio))
