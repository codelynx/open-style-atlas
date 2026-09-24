# Open Style Atlas

One subject, 猫耳の冒険者と男性剣士 (a cat-eared adventurer and a male swordsman), drawn in 100 art styles by open image models, each prompted in its own language. The styles and their numbering follow [Style Atlas](https://style-atlas-100.sssscryptoman.chatgpt.site/) by SSSS⚡CRYPTOMAN, which draws 200 styles with ChatGPT. This atlas asks how the same styles come out on models you can run yourself.

A style that fails is part of the result: it shows what a model cannot reach with prompts alone.

**Built with Style Atlas's blessing.** This atlas uses Style Atlas's styles, names and grouping, with credit and links, and its curator, SSSS⚡CRYPTOMAN, approved it. It is an independent project, not part of Style Atlas.

## Models

| Model | Prompt language | Drawn | First evaluation |
|---|---|---|---|
| [Animagine XL 4.0](https://huggingface.co/cagliostrolab/animagine-xl-4.0) | Danbooru tags | 100 | 49 work, 36 half, 15 fail |
| [Illustrious XL 2.0](https://huggingface.co/OnomaAIResearch/Illustrious-XL-v2.0) | Danbooru tags, Animagine's recipes unchanged | 100 | 20 work, 44 half, 36 fail |

Illustrious keeps the two characters apart better, but holds to its own look: the same tags change it far less than they change Animagine. Its recipes need their own tuning. Its official settings (clip skip 2, style before subject, 1536×1536, CFG 5) were tried on 10 styles with no gain: they changed its default look, not how well it follows style tags. Better Illustrious recipes are especially welcome.

Planned: Qwen-Image (sentences).

## Layout

- `styles.json`: the shared list. Number, group, Japanese title, English name.
- `models/<model>/`: one folder per model.
  - `model.json`: checkpoint, settings, the subject in the model's language, the prompt template
  - `recipes.json`: each style's words for this model
  - `results.json`: what was drawn: prompt, seed, time
  - `evaluation.json`: works, half or fails, with a note
  - `thumbs/`: pictures for the page
  - `images/`: full-size originals, kept out of git and attached to releases
- `sources/`: third-party material, kept out of the repository. Style Atlas's own paragraphs stay local; they are added only with the curator's consent.
- `scripts/draw.py`: draws a model's recipes through a running ComfyUI.
- `scripts/build_page.py`: builds `docs/index.html`, served by GitHub Pages.

## Draw and build

```sh
python3 scripts/draw.py models/animagine-xl-4.0          # what is not drawn yet
python3 scripts/draw.py models/animagine-xl-4.0 6 16    # just these, again
python3 scripts/build_page.py
```

Every picture uses the model's own seed and settings in `model.json` (also listed at the foot of the page), so any picture can be drawn again. `clipSkip` above 1 adds ComfyUI's `CLIPSetLastLayer`.

## Contributing

Better words for a style are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Licenses

- Scripts: MIT, see [LICENSE](LICENSE).
- Pictures, recipes and evaluations: CC BY 4.0, see [LICENSE-CONTENT](LICENSE-CONTENT).
- Pictures are made with each model under its own license; see the model's card. Animagine XL 4.0's outputs come with its license's use restrictions.
- Style Atlas's names, grouping and paragraphs belong to its curator.
