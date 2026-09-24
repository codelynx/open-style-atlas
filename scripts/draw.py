"""Draws a model's recipes through a running ComfyUI.

    python3 scripts/draw.py models/animagine-xl-4.0            # everything not drawn yet
    python3 scripts/draw.py models/animagine-xl-4.0 6 16      # just these, again

Reads the model's model.json (checkpoint, settings, subject, prompt template)
and recipes.json (style id -> recipe), and writes images/<id>.png (the
original), thumbs/<id>.webp (for the page) and results.json (the prompt,
seed and time of each). It works for checkpoint models with a plain
text-to-image graph, such as SDXL models; a model that needs another graph
gets its own script.
"""
import json, os, sys, time, urllib.request

COMFY = os.environ.get('COMFYUI', 'http://127.0.0.1:8188')


def post(path, body):
	request = urllib.request.Request(COMFY + path, json.dumps(body).encode(), {'Content-Type': 'application/json'})
	return json.load(urllib.request.urlopen(request))


def draw(model, prompt):
	# clip skip 2, as Illustrious asks, reads the text from the second-to-last CLIP layer
	clip = ['8', 0] if model.get('clipSkip', 1) > 1 else ['1', 1]
	graph = {
		'1': {'class_type': 'CheckpointLoaderSimple', 'inputs': {'ckpt_name': model['checkpoint']}},
		'2': {'class_type': 'CLIPTextEncode', 'inputs': {'text': prompt, 'clip': clip}},
		'3': {'class_type': 'CLIPTextEncode', 'inputs': {'text': model['negative'], 'clip': clip}},
		'4': {'class_type': 'EmptyLatentImage', 'inputs': {'width': model['width'], 'height': model['height'], 'batch_size': 1}},
		'5': {'class_type': 'KSampler', 'inputs': {'model': ['1', 0], 'positive': ['2', 0], 'negative': ['3', 0], 'latent_image': ['4', 0],
			'seed': model['seed'], 'steps': model['steps'], 'cfg': model['cfg'], 'sampler_name': model['sampler'], 'scheduler': model['scheduler'], 'denoise': 1}},
		'6': {'class_type': 'VAEDecode', 'inputs': {'samples': ['5', 0], 'vae': ['1', 2]}},
		'7': {'class_type': 'PreviewImage', 'inputs': {'images': ['6', 0]}},
	}
	if model.get('clipSkip', 1) > 1:
		graph['8'] = {'class_type': 'CLIPSetLastLayer', 'inputs': {'clip': ['1', 1], 'stop_at_clip_layer': -model['clipSkip']}}
	prompt_id = post('/prompt', {'prompt': graph})['prompt_id']
	while True:
		time.sleep(2)
		history = json.load(urllib.request.urlopen(f'{COMFY}/history/{prompt_id}')).get(prompt_id)
		if history and history.get('outputs'):
			image = history['outputs']['7']['images'][0]
			url = f"{COMFY}/view?filename={image['filename']}&subfolder={image['subfolder']}&type={image['type']}"
			return urllib.request.urlopen(url).read()
		if history and history.get('status', {}).get('status_str') == 'error':
			raise RuntimeError('ComfyUI reported an error')


def thumbnail(png_path, webp_path):
	from PIL import Image
	image = Image.open(png_path).convert('RGB')
	image.thumbnail((640, 640))
	image.save(webp_path, 'WEBP', quality=82)


def main():
	folder = sys.argv[1]
	wanted = {int(a) for a in sys.argv[2:]}
	model = json.load(open(f'{folder}/model.json'))
	recipes = json.load(open(f'{folder}/recipes.json'))
	styles = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'styles.json')))
	results_path = f'{folder}/results.json'
	results = json.load(open(results_path)) if os.path.exists(results_path) else {}
	os.makedirs(f'{folder}/images', exist_ok=True)
	os.makedirs(f'{folder}/thumbs', exist_ok=True)
	for style in styles:
		key = str(style['id'])
		if key not in recipes or (wanted and style['id'] not in wanted):
			continue
		png = f"{folder}/images/{style['id']:03d}.png"
		if os.path.exists(png) and not wanted:
			continue
		prompt = model['prompt'].format(subject=model['subject'], recipe=recipes[key], closing=model['closing'])
		start = time.time()
		try:
			open(png, 'wb').write(draw(model, prompt))
			thumbnail(png, f"{folder}/thumbs/{style['id']:03d}.webp")
			results[key] = {'prompt': prompt, 'negative': model['negative'], 'seed': model['seed'], 'seconds': round(time.time() - start)}
		except Exception as error:
			results[key] = {'prompt': prompt, 'error': str(error)}
		json.dump(results, open(results_path, 'w'), ensure_ascii=False, indent=1)
		print(style['id'], style['english'], results[key].get('seconds', 'failed'), flush=True)


if __name__ == '__main__':
	main()
