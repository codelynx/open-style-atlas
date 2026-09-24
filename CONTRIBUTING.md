# Contributing

The atlas gets better one style at a time: a recipe that brings a model closer to the style.

## Improving a recipe

1. Change the style's entry in `models/<model>/recipes.json`. Keep to the model's language: tags for tag models, sentences for sentence models.
2. Draw it with the model's own seed and settings from `model.json`, for example `python3 scripts/draw.py models/animagine-xl-4.0 47`.
3. Open a pull request with the new picture and its before-and-after, and say what changed and why.

Please don't change `model.json` in the same pull request: the shared seed and settings are what make the pictures comparable.

## Adding a model

Add `models/<model>/` with `model.json` (settings, the subject in the model's language, the prompt template) and `recipes.json`. The first recipes can be a straight translation of another model's; the atlas records how far they get.

## Rules

- No artist names in recipes. Styles are described by how they look, not by who draws them.
- Keep the subject and `safe`. Two adults, fully clothed.
