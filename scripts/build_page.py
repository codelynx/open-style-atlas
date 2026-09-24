"""Builds docs/index.html, the page GitHub Pages serves, from styles.json and
every folder in models/. Thumbnails are copied into docs/thumbs/<model>/.

    python3 scripts/build_page.py                 # links to Style Atlas for its paragraphs
    python3 scripts/build_page.py --paragraphs    # shows them: only with the curator's consent
"""
import html, json, os, shutil, sys

ROOT = os.path.join(os.path.dirname(__file__), '..')
VERDICTS = {'w': 'Works', 'h': 'Half', 'f': 'Fails'}
STYLE_ATLAS = 'https://style-atlas-100.sssscryptoman.chatgpt.site/'


def load(path, default):
	path = os.path.join(ROOT, path)
	return json.load(open(path)) if os.path.exists(path) else default


styles = load('styles.json', [])
paragraphs = load('sources/style-atlas-paragraphs.json', {}) if '--paragraphs' in sys.argv else {}
models = []
for name in sorted(os.listdir(os.path.join(ROOT, 'models'))):
	folder = f'models/{name}'
	if not os.path.exists(os.path.join(ROOT, folder, 'model.json')):
		continue
	model = load(f'{folder}/model.json', {})
	models.append({'key': name, 'name': model['name'], 'language': model.get('language', ''), 'config': model,
		'recipes': load(f'{folder}/recipes.json', {}), 'results': load(f'{folder}/results.json', {}),
		'evaluation': load(f'{folder}/evaluation.json', {})})
	thumbs = os.path.join(ROOT, folder, 'thumbs')
	target = os.path.join(ROOT, 'docs', 'thumbs', name)
	os.makedirs(target, exist_ok=True)
	for file in os.listdir(thumbs) if os.path.exists(thumbs) else []:
		shutil.copy2(os.path.join(thumbs, file), target)


def entry(style):
	key = str(style['id'])
	per_model = {}
	for m in models:
		thumb = f"thumbs/{m['key']}/{style['id']:03d}.webp"
		judged = m['evaluation'].get(key, {})
		per_model[m['key']] = {
			'image': thumb if os.path.exists(os.path.join(ROOT, 'docs', thumb)) else '',
			'recipe': m['recipes'].get(key, ''),
			'prompt': m['results'].get(key, {}).get('prompt', ''),
			'verdict': judged.get('verdict', ''), 'note': judged.get('note', ''),
		}
	return {'id': style['id'], 'title': style['title'], 'english': style['english'], 'paragraph': paragraphs.get(key, ''), 'models': per_model}


groups = {}
for style in styles:
	groups.setdefault((style['group'], style['groupName']), []).append(entry(style))
sections = []
for (number, name), items in sorted(groups.items()):
	cards = '\n'.join(
		f'<button class="card" data-entry="{html.escape(json.dumps(e, ensure_ascii=False))}">'
		f'<span class="badge"></span><img alt="{html.escape(e["english"])}" loading="lazy">'
		f'<span class="caption"><span class="title">{html.escape(e["title"])}</span><span class="en">{html.escape(e["english"])}</span><span class="num">#{e["id"]:03d}</span></span></button>'
		for e in items)
	sections.append(f'<section><h2><span class="n">{number:02d}</span> {html.escape(name)} <span class="count">{len(items)}</span></h2><div class="grid">{cards}</div></section>')
def footer():
	"""How each model was drawn, beyond its name: everything needed to draw a picture again."""
	rows = [('Checkpoint', 'checkpoint'), ('Generator', 'generator'), ('Hardware', 'hardware'), ('Size', None), ('Steps', 'steps'), ('CFG', 'cfg'),
		('Sampler', None), ('Clip skip', 'clipSkip'), ('Seed', 'seed'), ('Prompt', 'prompt'), ('Subject', 'subject'), ('Closing', 'closing'),
		('Negative', 'negative'), ('Recipes', 'recipesFrom'), ('Trials', 'trials')]
	parts = ["<h2>How each model was drawn</h2><p>One subject and one seed for every style of a model; the prompt is the template below with the style's recipe in it. Anything here can be improved by a pull request.</p>"]
	for m in models:
		c = m['config']
		values = {'Size': f"{c.get('width')}×{c.get('height')}", 'Sampler': f"{c.get('sampler')} / {c.get('scheduler')}"}
		items = []
		for label, key in rows:
			value = values.get(label) if key is None else c.get(key)
			if value in (None, '', []):
				continue
			if isinstance(value, list):
				value = ' '.join(value)
			items.append(f'<dt>{label}</dt><dd>{html.escape(str(value))}</dd>')
		parts.append(f'<h3>{html.escape(m["name"])}</h3><dl>{"".join(items)}</dl>')
	return ''.join(parts)


tabs = ''.join(f'<button data-model="{m["key"]}">{html.escape(m["name"])}</button>' for m in models)
names = json.dumps({m['key']: m['name'] for m in models})

page = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open Style Atlas</title>
<style>
:root {{ --bg: #f7f6f3; --card: #ffffff; --text: #1d1d1f; --muted: #6e6e73; --line: #e2e0da; --accent: #b4452f; }}
@media (prefers-color-scheme: dark) {{ :root {{ --bg: #161615; --card: #222220; --text: #f2f1ed; --muted: #a1a09a; --line: #34332f; --accent: #e27a5f; }} }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: var(--bg); color: var(--text); font: 15px/1.5 -apple-system, "Hiragino Sans", "Noto Sans JP", sans-serif; }}
a {{ color: var(--accent); }}
header, main {{ max-width: 1400px; margin: auto; padding: 0 16px; }}
header {{ padding-top: 28px; }}
header h1 {{ margin: 0; font-size: 28px; letter-spacing: .04em; }}
header p {{ margin: 6px 0 0; color: var(--muted); }}
nav {{ display: flex; gap: 8px; margin-top: 14px; flex-wrap: wrap; }}
nav button {{ font: inherit; border: 1px solid var(--line); background: var(--card); color: var(--text); border-radius: 99px; padding: 4px 12px; cursor: pointer; }}
nav button.on {{ border-color: var(--accent); color: var(--accent); }}
main {{ padding-bottom: 64px; }}
footer {{ max-width: 1400px; margin: auto; padding: 24px 16px 64px; border-top: 1px solid var(--line); color: var(--muted); font-size: 13px; }}
footer h2 {{ color: var(--text); }}
footer dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 4px 16px; margin: 8px 0 20px; }}
footer dt {{ color: var(--text); }}
footer dd {{ margin: 0; font-family: ui-monospace, Menlo, monospace; font-size: 12px; overflow-wrap: anywhere; }}
h2 {{ font-size: 18px; margin: 36px 0 12px; border-bottom: 1px solid var(--line); padding-bottom: 6px; }}
h2 .n {{ color: var(--accent); font-variant-numeric: tabular-nums; }}
h2 .count {{ color: var(--muted); font-weight: 400; font-size: 13px; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 14px; }}
.card {{ all: unset; cursor: pointer; background: var(--card); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; display: flex; flex-direction: column; position: relative; }}
.card:hover {{ border-color: var(--accent); }}
.card img {{ width: 100%; aspect-ratio: 1; object-fit: cover; display: block; background: repeating-linear-gradient(45deg, transparent 0 8px, var(--line) 8px 9px); }}
.badge {{ position: absolute; top: 8px; left: 8px; font-size: 11px; font-weight: 600; padding: 2px 8px; border-radius: 99px; color: #fff; }}
.badge:empty {{ display: none; }}
.w {{ background: #2e7d4f; }} .h {{ background: #b07a12; }} .f {{ background: #a33a2c; }}
.caption {{ padding: 8px 10px 10px; display: grid; gap: 2px; }}
.title {{ font-weight: 600; font-size: 14px; }}
.en, .num {{ color: var(--muted); font-size: 12px; }}
.hidden {{ display: none; }}
dialog {{ border: 0; border-radius: 14px; padding: 20px; max-width: min(1200px, 94vw); width: 100%; background: var(--card); color: var(--text); }}
dialog::backdrop {{ background: rgb(0 0 0 / .6); }}
.compare {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; margin-top: 12px; }}
.compare img {{ width: 100%; border-radius: 8px; display: block; }}
.label {{ font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: var(--muted); margin: 10px 0 4px; }}
code {{ display: block; white-space: pre-wrap; background: var(--bg); border: 1px solid var(--line); border-radius: 8px; padding: 8px; font: 12px/1.45 ui-monospace, Menlo, monospace; }}
.close {{ float: right; }}
</style>
</head>
<body>
<header>
<h1>Open Style Atlas</h1>
<p>One subject, 猫耳の冒険者と男性剣士, in {len(styles)} styles, drawn by open image models, each prompted in its own language. The styles follow <a href="{STYLE_ATLAS}">Style Atlas</a> by SSSS⚡CRYPTOMAN, which draws them with ChatGPT. A style that fails is part of the result. Better prompts are welcome as pull requests.</p>
<p>Built with Style Atlas's blessing, as an independent project. Source and pull requests: <a href="https://github.com/codelynx/open-style-atlas">github.com/codelynx/open-style-atlas</a>.</p>
<nav id="models">{tabs}</nav>
<nav id="filters"><button data-filter="" class="on">All</button>{"".join(f'<button data-filter="{k}">{v}</button>' for k, v in VERDICTS.items())}</nav>
</header>
<main>{"".join(sections)}</main>
<footer>{footer()}</footer>
<dialog id="detail"><button class="close" onclick="detail.close()">Close</button><h3 id="title"></h3><div id="compare" class="compare"></div></dialog>
<script>
const names = {names};
const verdicts = {json.dumps(VERDICTS)};
let model = Object.keys(names)[0], filter = '';
const cards = [...document.querySelectorAll('.card')];
function show() {{
	document.querySelectorAll('#models button').forEach(b => b.classList.toggle('on', b.dataset.model === model));
	document.querySelectorAll('#filters button').forEach(b => b.classList.toggle('on', b.dataset.filter === filter));
	for (const card of cards) {{
		const m = JSON.parse(card.dataset.entry).models[model] || {{}};
		card.querySelector('img').src = m.image || '';
		const badge = card.querySelector('.badge');
		badge.textContent = verdicts[m.verdict] || '';
		badge.className = 'badge ' + (m.verdict || '');
		card.classList.toggle('hidden', !!filter && m.verdict !== filter);
	}}
}}
document.querySelectorAll('#models button').forEach(b => b.onclick = () => {{ model = b.dataset.model; show(); }});
document.querySelectorAll('#filters button').forEach(b => b.onclick = () => {{ filter = b.dataset.filter; show(); }});
const detail = document.getElementById('detail');
for (const card of cards) card.onclick = () => {{
	const e = JSON.parse(card.dataset.entry);
	document.getElementById('title').textContent = `#${{String(e.id).padStart(3, '0')}} ${{e.title}} · ${{e.english}}`;
	const box = document.getElementById('compare');
	box.innerHTML = '';
	for (const [key, m] of Object.entries(e.models)) {{
		const div = document.createElement('div');
		div.innerHTML = `<strong>${{names[key]}}</strong>` + (m.image ? `<img src="${{m.image}}" alt="">` : '<p>Not drawn yet.</p>')
			+ `<div class="label">Evaluation</div><div>${{m.verdict ? verdicts[m.verdict] + ': ' + m.note : 'not yet'}}</div>`
			+ `<div class="label">Recipe</div><code></code><div class="label">Full prompt</div><code></code>`;
		const codes = div.querySelectorAll('code');
		codes[0].textContent = m.recipe; codes[1].textContent = m.prompt || 'not drawn yet';
		box.append(div);
	}}
	const source = document.createElement('div');
	source.innerHTML = '<strong>ChatGPT, on Style Atlas</strong><div class="label">Paragraph</div>'
		+ (e.paragraph ? '<code></code>' : `<p><a href="{STYLE_ATLAS}">See it on Style Atlas</a></p>`);
	if (e.paragraph) source.querySelector('code').textContent = e.paragraph;
	box.append(source);
	detail.showModal();
}};
detail.onclick = ev => {{ if (ev.target === detail) detail.close(); }};
show();
</script>
</body>
</html>
'''
open(os.path.join(ROOT, 'docs', 'index.html'), 'w').write(page)
print(f'docs/index.html: {len(styles)} styles, {len(models)} models')
