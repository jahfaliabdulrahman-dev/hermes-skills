# isLocalNetwork() Validation — Full Audit Trace

> Captured 2026-07-07 from hermex_android BUG-001 audit.
> See `flutter-android-build-system` SKILL.md §10 for the pattern.

## The Bug

User enters Tailscale IP (100.x.x.x:8642) in ConnectionScreen. Form validation shows:
> "HTTP is only allowed on local networks. Use HTTPS for remote servers."

Connect button blocked. Fix was applied to `ServerRepository.isLocalNetwork()` but appeared to persist.

## Root Cause: Flutter Hot-Reload Doesn't Propagate Static Method Changes

`ServerRepository.isLocalNetwork()` is a **static method** defined in `server_repository.dart`. The UI validator at `connection_screen.dart:97` calls it as `ServerRepository.isLocalNetwork(trimmed)`.

Flutter's hot reload (`r`) and hot restart (`R`) do NOT reliably propagate static method changes across compilation unit boundaries. The old compiled version stays cached.

**Fix:** `flutter clean && flutter run` — full rebuild required. Never trust `r`/`R` for static method edits.

## All isLocalNetwork() Call Sites (hermex_android)

| File | Line | Context |
|---|---|---|
| `server_repository.dart` | 341-356 | Static method definition + RFC 1918 checks + Tailscale range |
| `server_repository.dart` | 288 | `_validateUrl()` calls `isLocalNetwork(url)` — data-layer validation |
| `connection_screen.dart` | 97 | `_validateUrl()` calls `ServerRepository.isLocalNetwork()` — UI form validator |
| `connection_screen.dart` | 301 | `connectionState.isLocalNetwork` — cosmetic hint widget |
| `connection_provider.dart` | 144-145 | Sets `isLocalNetwork` flag on state from `ServerRepository.isLocalNetwork(url)` |
| `connection_provider.dart` | 375 | `detectLocalNetwork()` delegates to `ServerRepository.isLocalNetwork()` |

**Verdict:** Every call site uses the SAME static method. No second validation exists. The fix propagates everywhere once the build cache is flushed.

## Tailscale/CGNAT Range Implementation

```dart
// server_repository.dart lines 352-353, 375-388
if (host.startsWith('100.') && _isTailscaleOrCGNAT(host)) return true;

static bool _isTailscaleOrCGNAT(String host) {
  final parts = host.split('.');
  if (parts.length != 4) return false;
  final second = int.parse(parts[1]);
  return second >= 64 && second <= 127;  // 100.64.0.0/10
}
```

This covers `100.64.0.1` through `100.127.255.255`. Validated correct.

## Structural Issue: Duplicated _validateUrl()

Two near-identical methods exist:
- `connection_screen.dart:70-102` — UI form validator  
- `server_repository.dart:255-297` — pre-health-check validation

Both check: emptiness, URI parseability, userInfo rejection, http/https scheme, and isLocalNetwork(). Any fix must be applied twice. Recommendation: make `ServerRepository._validateUrl` public and have the UI delegate to it.

## Test Cases to Add

```
http://100.64.0.1:8642    → true  (Tailscale bottom of range)
http://100.100.100.100     → true  (Tailscale mid-range)
http://100.127.255.255     → true  (Tailscale top of range)
http://100.63.255.255      → false (below Tailscale range)
http://100.128.0.1         → false (above Tailscale range)
```

## Android Config Dependency

`android/app/src/main/res/xml/network_security_config.xml` must have `cleartextTrafficPermitted="true"` in `<base-config>` for ANY cleartext HTTP to work on Android. The Dart-level `isLocalNetwork()` validation and the OS-level config are complementary — both are needed.
