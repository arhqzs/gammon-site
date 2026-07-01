# -*- coding: utf-8 -*-
import re, os, json

SRC = r"C:\Users\Daniel Lehmann\Downloads\Gammon Themes (shareable).html"
REPO = r"C:\Users\Daniel Lehmann\Documents\backgammon main site"
SCRATCH = r"C:\Users\DANIEL~1\AppData\Local\Temp\claude\C--Users-Daniel-Lehmann-Documents-backgammon-main-site\523e6d0f-cfae-4e2d-9fee-c24f6265f9e1\scratchpad"
OUT = os.path.join(REPO, "designs")

# ---- the 12 liked themes, in the order the user listed them ----
LIKED = ["Zine Punk","Sapphire","Pine Court","Butter","Walnut","Tundra",
         "Carbon","Mono Red","Periwinkle","Buttermilk","Peach","Red & Black"]

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
    return (f'<!DOCTYPE html>\n<html lang="en"><head>\n<meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            f'<title>Gammon — {title}</title>\n'
            f'<link rel="preconnect" href="https://fonts.googleapis.com">'
            f'<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
            f'<link href="{FONTS_URL}" rel="stylesheet">\n'
            f'<style>*{{box-sizing:border-box}}html,body{{margin:0;padding:0}}'
            f"body{{font-family:'Hanken Grotesk','Archivo',system-ui,sans-serif}}{extra}</style>\n</head>\n<body>\n")

def clean(b):
    b = re.sub(r'</?sc-(if|for)[^>]*>', '', b)
    b = re.sub(r'\s+hint-placeholder-val="[^"]*"', '', b)
    b = re.sub(r'</?x-dc[^>]*>', '', b)
    return b.strip()

h = open(SRC, encoding="utf-8", errors="replace").read()
t = json.loads(re.search(r'type="__bundler/template">(.*?)</script>', h, re.S).group(1))
comp = [c for c in re.findall(r'<script[^>]*>(.*?)</script>', t, flags=re.S) if 'THEMES' in c][0]

# hand-built themes (name -> section index, key, dots)
meta = re.findall(r"\{\s*key:'([^']+)',\s*name:'([^']+)',\s*dot1:'([^']+)',\s*dot2:'([^']+)'\s*\}",
                  re.search(r'THEMES\s*=\s*\[(.*?)\];', comp, re.S).group(1))
opens = sorted([(m.start(), m.end(), int(m.group(1)))
                for m in re.finditer(r'<sc-if value="\{\{ s(\d{1,3}) \}\}"[^>]*>', t)], key=lambda x: x[2])
hand = {}   # name -> (idx, key, d1, d2)
for i,(k,n,d1,d2) in enumerate(meta):
    hand[n] = (i, k, d1, d2)

# generic themes
FONTS = re.findall(r'"((?:[^"\\]|\\.)*)"', re.search(r'FONTS\s*=\s*\[(.*?)\];', comp, re.S).group(1))
pool_txt = re.search(r'POOL\s*=\s*\[(.*?)\];', comp, re.S).group(1)
POOL = [{"t":a,"k":b} for a,b in re.findall(r"\{t:'((?:[^'\\]|\\.)*)',k:'((?:[^'\\]|\\.)*)'\}", pool_txt)]
graw = comp[comp.find('GEN_RAW = ['):comp.index('];', comp.find('GEN_RAW = ['))]
tup = re.findall(r"\['([^']+)','([^']+)',(\d+),'([dl])','([^']+)','([^']+)','([^']+)','([^']+)','([^']+)',(\d+),(\d+),(\d+)\]", graw)
gen = {}    # name -> dict
for gi,r in enumerate(tup):
    p = POOL[(42+gi) % len(POOL)]
    gen[r[1]] = {"key":r[0],"name":r[1],"arch":int(r[2]),"htitle":p["t"],"hkicker":p["k"],
                 "sw":r[6],"sw2":r[8],
                 "spec":{"bg":r[4],"ink":r[5],"acc":r[6],"on":r[7],"acc2":r[8],
                         "disp":FONTS[int(r[9])],"body":FONTS[int(r[10])],"rad":int(r[11])}}

# validate all liked exist
missing = [n for n in LIKED if n not in hand and n not in gen]
assert not missing, "not found: " + str(missing)

# 6 architecture templates (for kept generic themes)
gblock = t[t.index('<sc-if value="{{ isGeneric }}"'):]
arch_html = {}
for a in re.finditer(r'<sc-if value="\{\{ (g[A-F]) \}\}"[^>]*>', gblock):
    close = gblock.index('</sc-if>', a.end())
    inner = clean(gblock[a.end():close]).replace('{{ g.title }}','<span data-g="title"></span>')\
             .replace('{{ g.kicker }}','<span data-g="kicker"></span>').replace('{{ g.name }}','<span data-g="name"></span>')
    arch_html[a.group(1)] = inner

# ---- wipe designs and regenerate only kept themes ----
for f in os.listdir(OUT):
    if f.endswith(".html"): os.remove(os.path.join(OUT,f))

studio = []
kept_gen = []
for pos,name in enumerate(LIKED, start=1):
    nn = f"{pos:02d}"
    if name in hand:
        idx,key,d1,d2 = hand[name]
        s,e,_ = opens[idx]
        body = clean(t[e:t.index('</sc-if>', e)])
        fn = f"theme-{nn}-{key}.html"
        open(os.path.join(OUT,fn),"w",encoding="utf-8").write(head(name)+body+"\n</body></html>\n")
        studio.append({"n":nn,"file":f"../designs/{fn}","title":name,"sw":d1,"sw2":d2})
    else:
        g = gen[name]
        kept_gen.append(g)
        studio.append({"n":nn,"file":f"../designs/gen.html#{g['key']}","title":name,"sw":g["sw"],"sw2":g["sw2"]})

# ---- gen.html with only kept generic themes (hero text baked in) ----
archs_dom = "\n".join(f'<div class="arch" data-arch="{k}">{arch_html[k]}</div>' for k in ['gA','gB','gC','gD','gE','gF'])
GENJS = [{"key":g["key"],"name":g["name"],"arch":g["arch"],"htitle":g["htitle"],"hkicker":g["hkicker"],"spec":g["spec"]} for g in kept_gen]
extra = "#gen-root{min-height:100vh;background-color:var(--g-bg);color:var(--g-ink);font-family:var(--g-body)}.arch{display:none}.arch.on{display:block}"
js = """
const GEN=%s, ARCH=['gA','gB','gC','gD','gE','gF'];
function applyVars(s){
  const el=document.getElementById('gen-root'); const mix=(a,p,b)=>`color-mix(in srgb, ${a} ${p}%%, ${b})`;
  const V={'--g-bg':s.bg,'--g-ink':s.ink,'--g-acc':s.acc,'--g-on':s.on,'--g-acc2':s.acc2,'--g-disp':s.disp,'--g-body':s.body,
    '--g-rad':s.rad+'px','--g-rbtn':Math.min(s.rad,14)+'px','--g-surface':mix(s.bg,90,s.ink),'--g-surface2':mix(s.bg,82,s.ink),
    '--g-line':mix(s.ink,15,'transparent'),'--g-line2':mix(s.ink,32,'transparent'),'--g-dim':mix(s.ink,80,s.bg),
    '--g-muted':mix(s.ink,56,s.bg),'--g-soft':mix(s.acc,15,'transparent'),'--g-felt':mix(s.acc2,58,'#0c110d'),
    '--g-frame':mix(s.bg,60,s.ink),'--g-p1':s.acc,'--g-p2':s.acc2};
  for(const k in V) el.style.setProperty(k,V[k]);
}
function render(){
  const key=(location.hash||'').replace('#',''); let t=GEN.find(x=>x.key===key)||GEN[0]; if(!t) return;
  applyVars(t.spec);
  document.querySelectorAll('.arch').forEach(el=>el.classList.remove('on'));
  const el=document.querySelector('.arch[data-arch="'+(ARCH[t.arch]||'gA')+'"]'); if(el) el.classList.add('on');
  document.querySelectorAll('[data-g="title"]').forEach(n=>n.textContent=t.htitle);
  document.querySelectorAll('[data-g="kicker"]').forEach(n=>n.textContent=t.hkicker);
  document.querySelectorAll('[data-g="name"]').forEach(n=>n.textContent=t.name);
  document.title='Gammon — '+t.name;
}
window.addEventListener('hashchange',render); render();
""" % json.dumps(GENJS, ensure_ascii=False)
open(os.path.join(OUT,"gen.html"),"w",encoding="utf-8").write(
    head("Design",extra)+f'<div id="gen-root">\n{archs_dom}\n</div>\n<script>{js}</script>\n</body></html>\n')

# ---- studio list ----
with open(os.path.join(SCRATCH,"studio_themes.js"),"w",encoding="utf-8") as f:
    f.write("const THEMES = [\n")
    for x in studio:
        f.write(f'  {{n:"{x["n"]}", file:{json.dumps(x["file"])}, title:{json.dumps(x["title"], ensure_ascii=False)}, sw:"{x["sw"]}", sw2:"{x["sw2"]}"}},\n')
    f.write("];\n")

print("kept", len(studio), "themes:")
for x in studio: print(" ", x["n"], x["title"])
print("static files:", sorted(f for f in os.listdir(OUT) if f.startswith("theme-")))
print("gen.html generic themes:", [g["key"] for g in GENJS])
