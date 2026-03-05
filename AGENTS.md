# Repository Guidelines

## Project Structure & Module Organization
This repository is a flat ComfyUI custom-node plugin.
- `__init__.py`: plugin entry; exports `NODE_CLASS_MAPPINGS` and `NODE_DISPLAY_NAME_MAPPINGS`.
- `*Control.py`: behavior/prompt composition nodes (for pose, scene, solo/group actions).
- `*Customizer.py`: character appearance, costume, accessory, and male-role customization nodes.
- `README.md`: minimal project description.
- `__pycache__/`: generated artifacts; do not edit or commit intentionally.

Keep new node modules at repository root unless the project is explicitly refactored.

## ComfyUI Plugin Structure Requirements
- Install path: `<ComfyUI>/custom_nodes/ComfyUI-SlaaneshController/`.
- `__init__.py` is mandatory and must expose:
  - `NODE_CLASS_MAPPINGS` (internal node keys -> class objects)
  - `NODE_DISPLAY_NAME_MAPPINGS` (internal node keys -> UI names)
  - optional `WEB_DIRECTORY` only when shipping frontend JS assets.
- Every node class should define `INPUT_TYPES`, `RETURN_TYPES`, `FUNCTION`, and `CATEGORY`.
- Keep `CATEGORY` under `slaaneshcontroller/*` so nodes stay grouped correctly in ComfyUI menus.
- Avoid import-time side effects (network/file writes/heavy init).

## Build, Test, and Development Commands
There is no separate build pipeline; validation is Python syntax + ComfyUI runtime checks.
- `python3 -m py_compile __init__.py AccessoryCustomizer.py BodyCustomizer.py CostumeCustomizer.py GroupSexControl.py MaleCharacterCustomizer.py PoseControl.py SceneControl.py SoloSexControl.py`
  - Fast syntax validation for all shipped modules.
- `python3 -m compileall .`
  - Optional full compile pass.
- `git status && git diff --name-only`
  - Confirm only intended files changed.

For runtime verification, place this folder under `<ComfyUI>/custom_nodes/`, restart ComfyUI, and confirm nodes load under `slaaneshcontroller/*` categories.
- Typical local startup from ComfyUI root: `python main.py`.

## Coding Style & Naming Conventions
- Use 4-space indentation and UTF-8 encoding.
- Follow existing naming patterns:
  - Classes: `SlaaneshXxx` (PascalCase)
  - Functions/locals: `snake_case`
  - Constants/maps: `UPPER_SNAKE_CASE`
- Keep `INPUT_TYPES` UI keys and runtime `kwargs` keys strictly aligned.
- Preserve module-level mapping conventions (`NODE_CLASS_MAPPINGS`, `NODE_DISPLAY_NAME_MAPPINGS`).
- Use relative imports inside the plugin package (for example, `from .PoseControl import SlaaneshPoseControl`).

## Testing Guidelines
Automated tests are not yet established.
- Minimum required checks for every change:
  - Syntax compile (`py_compile` command above)
  - Manual ComfyUI smoke test
- If adding tests, create `tests/` and name files `test_<module>.py` using `pytest` conventions.

## Commit & Pull Request Guidelines
Recent history favors short, focused commits (often module-specific and action-oriented).
- Prefer format: `<module>: <what changed>` (example: `SoloSexControl: fix UI key mapping`).
- Keep one logical change per commit.
- PRs should include:
  - concise summary
  - affected modules
  - manual test notes (ComfyUI workflow + expected node output)
  - screenshots only when UI behavior changes.
