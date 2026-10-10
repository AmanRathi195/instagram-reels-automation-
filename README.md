# Instagram Reels Automation (Free / No AI Credits)

This is a separate, public media generator for @just_feeling_it___.

## What works
- Python + Pillow + FFmpeg create a 9-second vertical Reel without AI-generation credits.
- GitHub Actions runs daily at 12:15 UTC (17:45 IST), or manually.
- GitHub Pages hosts the most recently generated video at `reel.mp4` and metadata at `manifest.json`.

## One-time setup
1. Repository Settings → Pages → Build and deployment → Source: **GitHub Actions**.
2. Actions → Generate daily Reel → Run workflow.
3. Confirm the GitHub Pages URL serves `reel.mp4` and `manifest.json`.

## Important limitations
**This does not publish to Instagram yet.** Official Instagram API credentials, permissions, token handling, and a publisher workflow still need to be configured and tested. Do not put tokens in this public repository; use GitHub Actions secrets.

This prototype rotates a small, finite quote bank. Expand and editorially review the content bank before daily posting. The media URL points to the latest video and changes daily; a real publishing workflow must use a stable, immutable per-post URL and verify availability before publishing. Public GitHub Pages is subject to GitHub's terms and limits; verify suitability for automated media delivery. No platform can guarantee a free tier forever.

No Runway, subscriptions, or paid AI services are used.
