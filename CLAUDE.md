# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Personal blog at brentwbenson.org, built with **Quarto** (a Pandoc-based publishing system). Deployed to **GitHub Pages** from the `docs/` output directory.

## Build Commands

```bash
quarto render          # Build the full site to docs/
quarto preview         # Live preview with auto-reload
quarto render posts/my-post/  # Render a single post
```

R environment is managed via `renv`. The `.Rprofile` activates it automatically when R starts.

## Key Configuration

- **`_quarto.yml`**: Main site config (theme, navbar, analytics, output dir)
- **`posts/_metadata.yml`**: Default front matter for all posts (`freeze: true`, `title-block-banner: true`)
- **`renv.lock`**: Locked R package versions

## Writing Posts

Posts live in `posts/<post-name>/index.qmd` as Quarto Markdown with YAML front matter. Images go in the same directory as the post. Lightbox image galleries use `{group="group-name"}` syntax on images.

## Deployment

The rendered site in `docs/` is committed to the repo and served via GitHub Pages with a custom domain (`CNAME` → brentwbenson.org).
