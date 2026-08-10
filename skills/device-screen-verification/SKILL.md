---
name: device-screen-verification
description: Visually verify Android device screens via adb screencap.
version: 1.0.0
metadata:
  hermes:
    tags: [android, adb, vision, device-verification, screenshot, qa]
    related_skills: [android-adb-device-testing, camofox-browser]
---

# Device Screen Verification (adb → local HTTP → browser_vision)

Proven pipeline (2026-08-08, CarSah Stage 4) for *seeing* a connected Android
device's screen and producing verifiable visual evidence. The active LLM is
often text-only; `browser_vision` falls back to the auxiliary vision model
configured for the platform — this pipeline feeds it the screenshot.

**Vision model (pinned 2026-08-09):** `auxiliary.vision` →
`stepfun/step-3.7-flash:free` via provider `nous` (multimodal: text + image +
video → text). Pin it explicitly in the Hermes config (`auxiliary.vision.model`),
do not rely on auto-detect. The accuracy measurements below predate this pin
(auto vision) — re-measure with the pinned model if a small-text/quality doubt
resurfaces.

## When to use

- A build step's definition of done is "device-verified" (e.g. spec pack 14 §14.1)
- You must confirm what is actually rendered (UI acceptance, RTL, state screens)
- You need a screenshot as PASS/FAIL evidence in a verification note (14 §14.2)
- Any time the user asks "look at the phone screen"

## Prerequisites

- Device connected over USB: `adb devices -l` shows it (model, transport)
- Screen awake: `adb shell dumpsys power | grep mWakefulness` → `Awake`.
  If not: `adb shell input keyevent 224` (KEYCODE_WAKEUP)
- Camofox server running: `curl -s http://localhost:9377` →
  `{"ok":true,...,"browserConnected":true}`. If down: `cd ~/camofox-browser && npm start` (background), wait ~5s, re-check. If tab creation hangs after a failed attempt, restart the server (kill + npm start).

## Steps

1. **Capture** (full resolution, keep original):
   ```bash
   adb exec-out screencap -p > /tmp/device_screen.png
   file /tmp/device_screen.png   # confirm PNG + dimensions
   ```
2. **Downscale to JPEG** (≤800px long edge) — large RGBA PNGs can hang the engine:
   ```bash
   sips -s format jpeg -Z 800 /tmp/device_screen.png --out /tmp/device_screen.jpg
   ```
3. **Serve locally** (bind 127.0.0.1 ONLY — never 0.0.0.0; screenshots are private):
   ```bash
   cd /tmp && python3 -m http.server 8090 --bind 127.0.0.1   # background
   ```
4. **Wrap in HTML** — a raw image URL never completes its load event and the
   tab creation times out; an HTML page with `<img>` loads reliably:
   ```html
   <!DOCTYPE html><html><head><meta charset="utf-8"><title>Screen</title></head>
   <body style="margin:0;background:#000">
   <img src="device_screen.jpg" style="width:100%;height:auto;display:block">
   </body></html>
   ```
   (write to `/tmp/view.html` next to the image)
5. **Navigate + see**:
   - `browser_navigate("http://localhost:8090/view.html")` → expect success
   - `browser_vision(question="Describe this Android screen in detail; read visible text exactly.")`
6. **Deliver evidence**: include the original `MEDIA:/tmp/device_screen.png` in
   the reply so the user sees exactly what was analyzed.
7. **Cleanup**: kill the python server (`process kill`), keep Camofox running.

## Accuracy protocol & known limits (empirically tested 2026-08-08)

**Test design:** capture screenshot → extract GROUND TRUTH from the device
(`adb shell dumpsys battery | grep level`, `adb shell date`, `uiautomator dump`
→ parse `text=` attributes) → ask vision to read the same facts → compare.

Measured results (Auto vision, 1080×2460 TECNO LJ7):
- ✅ Full-screen reads: the downscaled full screen is the STANDARD and works —
  layout, visible text, numbers, states are read accurately without any crop
- ✅ Large/medium text numbers: accurate (battery 58 vs device 57→58 charging;
  countdown -١:١٩:٢١ vs ١:١٩:١٨; Eastern-Arabic digit identification correct)
- ✅ Empty/black input: honest "black screen" — no hallucination
- ❌ Small status-bar text (clock): unreadable at 800px downscale and even at
  2× from a 170px native crop (blurry) — crop was TESTED and did NOT help;
  for exact small text use `uiautomator dump` ground truth, not cropping
- ❌ AMBIGUITY FABRICATION: when the rendered page is ambiguous (huge images
  sliced by the viewport), the model fills in plausible content. **User-confirmed
  (2026-08-08):** it "saw" a Google folder with Translate/Maps/Drive/Meet that
  does not exist — the real dock is YouTube/Gmail/Google/المعرض/واتساب/تيليجرام/
  الآلة الحاسبة/alrajhi bank (uiautomator + owner). Meanwhile its NUMBER reads
  (battery 58% vs charging progression 57→58→60; countdown -1:19:21 vs owner
  reading 1:11:24 eight minutes later) were exact. Rule: numbers/clear text =
  trustworthy; small ambiguous icons = fabricate-risk. NEVER treat a single
  vision pass as proof of absence — cross-check with uiautomator.

**About cropping — minimal, optional, never ritualized:** Do NOT crop by
default and do not treat "small text" as a doctrine. The one measured
small-text failure (2026-08-08) was the status-bar CLOCK at 800px downscale —
a pathological case (tiny ~8px glyphs), and it is a dated single observation,
not a law: normal app UI text (titles, labels, buttons) reads fine from the
full downscaled screen. Exact-text claims ALWAYS come from `uiautomator dump`
— no vision pass is ever needed to prove a string exists. A crop is justified
only when you must magnify ONE specific visual region (e.g. a dense chart or
icon cluster) to judge appearance — and if it fails, accept it and rely on
uiautomator + layout evidence. Never report a "crop needed" finding for text
that uiautomator already confirms.

**Hard rules for PASS/FAIL evidence:**
1. `browser_vision` analyzes the **1280×720 viewport** of the RENDERED page, not
   the raw file. Control the layout: `object-fit:contain; height:100vh` for a
   single region; one region per page — never side-by-side huge images.
2. Always pair vision with `uiautomator dump` ground truth for text claims.
3. Treat "I don't see X" as "not readable in this capture", not "X absent".

## Pitfalls (all hit in the field)

| Symptom | Cause | Fix |
|---|---|---|
| `400 Bad Request` on `file://...` | Camofox blocks non-http(s) schemes | Serve over HTTP (step 3) |
| Tab creation times out (30s) on an image URL | Raw image page never fires load completion | HTML wrapper (step 4) |
| Timeout even after wrapper (first try) | Engine still warming up / stale tab state | Restart camofox server, retry |
| Engine fetched the image but still hangs | Large RGBA PNG rendering | Downscale to JPEG ≤800px |
| python server on 0.0.0.0 | LAN exposure of private screenshots | Always `--bind 127.0.0.1` |

## Black-screen triage — verify, never assume a benign cause (2026-08-10)

A black screen on the device has a real-failure class that a plausible-sounding
dismissal can bury. Observed: the implementer saw a black screen and recorded
"low-battery display state, not an app issue" — while the founder, watching the
actual device, confirmed the screen was ON, the app process was ALIVE, and the
app was rendering BLACK (a real bug: after save from the root route, the app
navigated to a broken route → blank frame; the auditor later admitted the
dismissal was wrong). Triage rules:

1. **Ground truth first:** `adb shell dumpsys power | grep mWakefulness` (screen
   state), `adb shell dumpsys battery | grep level` (battery — actually
   MEASURE it, don't assume), `adb shell dumpsys activity activities | grep
   ResumedActivity` (is the app the resumed activity?), `logcat -d | grep -i
   fatal\|render\|surface` (renderer/activity errors).
2. **A benign claim needs proof.** "Low battery display" requires the battery
   level to be genuinely critical — if it is 40%+ and the screen is awake,
   the claim is false by measurement.
3. **The founder's eyes beat a plausible story.** When the founder says the
   device shows something, treat it as ground truth and RE-DIAGNOSE — the
   agent's hypothesis must reconcile with the founder's observation, not the
   other way around.
4. **Root-cause, then pin it.** Fix the navigation/render cause AND add a
   regression assertion (e.g. "after save from root route, we must land on
   /dashboard") so the class cannot silently recur.

## Honest notes

- Vision quality = auxiliary vision model (config-dependent). For text-heavy
  verification cross-check details (e.g. battery %, visible numbers) against
  the analysis; flag uncertainty instead of inventing content.
- The screenshot stays local; never upload a device screenshot to a public
  service. Serving on 127.0.0.1 keeps the Camofox engine fetching it locally.
- adb screen state: screencap captures whatever is displayed (lock screen
  included). Wake the device first for meaningful captures.
