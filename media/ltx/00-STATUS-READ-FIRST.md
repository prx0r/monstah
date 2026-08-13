# LTX Production Pack — status note

Date: 2026-08-13

## Important version correction

No official Lightricks `LTX-2.5` release/checkpoint was found in current official documentation, GitHub, Hugging Face, or the LTX API docs.

The current official production/open-source line is **LTX-2.3**:
- API models: `ltx-2-3-fast`, `ltx-2-3-pro`
- open-source checkpoints/workflows: LTX-2.3
- the older `ltx-2-fast` / `ltx-2-pro` API models are deprecated and scheduled for removal on 2026-08-15.

Community/Hugging Face discussion references LTX-2.5 as a future/roadmap concept, but it is not an official released target in the sources reviewed.

This pack therefore uses:
1. **LTX-2.3 today**
2. a renderer abstraction so a future LTX-2.5 backend can be swapped in
3. a `2.5-WATCHLIST.md` file that lists what to verify on release
