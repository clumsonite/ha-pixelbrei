# ha-pixelbrei

Home Assistant custom integration `pixel_clock` for iPixel Color BLE LED panels (Action
"LED flexible fun screen", 64x16, Bluetooth name `LED_BLE_…`). Independent copy of
an upstream public repo (as of 1583dff, version 0.2.0); the domain stays `pixel_clock`.

## Protocol and hardware (verified by the original author, 2026-11-01)

- Device info type 131 = 64x16, MTU 517, PNG/GIF upload with ACKs works, GIF with partial frames
  (disposal 1) decodes correctly on the panel. ~5-6 KB/s over BLE from a laptop
  (`tools/live_test.py`).
- Uploads: write without response, 509-byte chunks, MTU must be acquired on BlueZ (else 23).
  Measured: 22 KB GIF in 0.4 s (laptop); notification visible ~2 s after the action in HA.
- While HA is connected the panel does not advertise: for laptop tests disable the entry
  (`config_entries/disable`) and enable it again afterwards.
- Fast uploads over a Raspberry Pi's BlueZ lost data in 12 KB windows (also with an 8 ms pause per
  chunk); fixed with an acknowledged write every 8th chunk + last chunk of each window, and an
  in-place retry with acknowledged writes. Preview (image entity) is built in a background task
  after the upload (it delayed the state by seconds on the Pi).
- The panel has no sensors: info response bytes 5/6 count up like an uptime (mm:ss), rhythm mode
  gets its levels from the phone's microphone, the app's temperature is internet weather.
- USB of the panel is power only. Control is BLE only.

## Architecture notes

- HACS does not install the blueprints; they have to be copied to
  /config/blueprints/automation/pixel_clock/ or imported via the README links.
- README images come from `tools/docs_images.py`; Action article: action.com/de-de/p/3226274.
- Version 2: pages are config subentries of type "app" (types clock, date, weather, value, power,
  status, text, calendar; icon, colour, effect each). Migration 1->2 turned the options into apps.
- Never add entities with config_subentry_id while they share the panel device: HA then moves
  the device between subentries and deletes the entities of the previous assignment (happened
  with f07d198, repaired by _detach_from_subentries in e842cc0).
- Clock with seconds = GIF counting to the end of the minute; Rendered.valid_until keeps it from
  being re-sent within the minute (re-sending restarted the GIF and the seconds jumped).
- App switches on the device page are user choices; don't "fix" disabled apps.
- On/off times are not part of the integration (removed in 0.5.0 after 0.3 and 0.4 tried page windows and
  panel slots; the user prefers them in Node-RED). The light entity is the plain master switch. Power off
  or all pages off = dark: current app "off", black preview, notifications dropped (all pages off keeps new
  notifications showing).
- Page transitions (`transitions.py`, select "transition"): a short GIF from the old to the new picture with a
  long-held last frame, then the real page in a second upload. Directly in front of the page's frames does not
  work: a GIF loops as a whole. Brightness steps (0.5.1) were dropped because they do nothing at 1 % brightness.
- Brightness is a number entity; weather app option "forecast" (daily high/low via
  weather.get_forecasts, cached 30 min).
- A BLE error whose recovery also failed (`client.disconnect()` timing out with the proxy gone) once
  killed the display task for good, while the entities stayed available. `async_disconnect` must never
  raise, and every BLE operation has an overall timeout.
- Public repo: no personal data in code, docs, commits or PRs; commit as clumsonite with the
  GitHub noreply address (set in the repo's git config).

## Ideas not done yet

- Animated LaMetric icons (only the first frame is used), night dimming, 12 h clock.

## Rules

- Never commit the vendor APK/APKM (in .gitignore) or decompiled app code.
- The protocol came from DEX string checks plus pypixelcolor 0.5.0 (MIT) source.
- Pure modules (protocol, font, icons, render) must not import Home Assistant (tests load them
  without HA via tests/conftest.py).
