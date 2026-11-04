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

## Ideas not done yet

- Animated LaMetric icons (only the first frame is used), night dimming, 12 h clock.

## Rules

- Never commit the vendor APK/APKM (in .gitignore) or decompiled app code.
- The protocol came from DEX string checks plus pypixelcolor 0.5.0 (MIT) source.
- Pure modules (protocol, font, icons, render) must not import Home Assistant (tests load them
  without HA via tests/conftest.py).
