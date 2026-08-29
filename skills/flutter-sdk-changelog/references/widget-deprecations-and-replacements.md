# Flutter Widget & API Deprecations (generated from the stable source tree)

**Generated:** 2026-08-29 by `scripts/build_flutter_sdk_changelog.py` from the
`flutter/flutter` **stable** branch (`git grep` over `@Deprecated` annotations at `d3b14c87690`, Flutter `3.47.2`).

**How the version column is derived:** `docs/contributing/Tree-hygiene.md` requires the annotation to record
*the beta version current when the deprecation landed* (`This feature was deprecated after v<beta>`).
The first **stable** release that carries it is therefore the next stable minor after that marker.
Both numbers are given: `First stable` (derived) and `Source marker` (verbatim from the code).

⚠️ Deprecated is not removed: Flutter currently does **not** remove deprecated APIs on a schedule
(same doc). But several pre-3.10 APIs *were* removed in the past and no longer exist at all —
see the removal list at the end.

## First stable release: Flutter 3.44  (15 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `cacheExtent` | Use scrollCacheExtent instead. | `material/reorderable_list.dart` | `v3.41` |
| `onReorder` | Use the onReorderItem callback instead. The onReorderItem callback adjusts the newIndex parameter for a removed item at the oldIndex. | `material/reorderable_list.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `rendering/viewport.dart` | `v3.41` |
| `cacheExtentStyle` | Use scrollCacheExtent instead. | `rendering/viewport.dart` | `v3.41` |
| `setStyle` | Use updateStyle instead. | `services/text_input.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `widgets/reorderable_list.dart` | `v3.41` |
| `onReorder` | Use the onReorderItem callback instead. The onReorderItem callback adjusts the newIndex parameter for a removed item at the oldIndex. | `widgets/reorderable_list.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `widgets/scroll_view.dart` | `v3.41` |
| `axisAlignment` | Use alignment instead. This property provides full control over both axes, which is an improvement over the old axisAlignment. | `widgets/transitions.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `widgets/two_dimensional_scroll_view.dart` | `v3.41` |
| `cacheExtentStyle` | Use scrollCacheExtent instead. | `widgets/two_dimensional_scroll_view.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `widgets/two_dimensional_viewport.dart` | `v3.41` |
| `cacheExtentStyle` | Use scrollCacheExtent instead. | `widgets/two_dimensional_viewport.dart` | `v3.41` |
| `cacheExtent` | Use scrollCacheExtent instead. | `widgets/viewport.dart` | `v3.41` |
| `cacheExtentStyle` | Use scrollCacheExtent instead. | `widgets/viewport.dart` | `v3.41` |

## First stable release: Flutter 3.41  (6 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `builder` | Use scrollableBuilder instead. | `cupertino/sheet.dart` | `v3.40` |
| `containsSemantics` | Migrate to isSemantics instead. | `flutter_test/matchers.dart` | `v3.40` |
| `filter` | Use filterConfig instead. | `rendering/proxy_box.dart` | `v3.40` |
| `curve` | Use animationStyle instead. | `widgets/expansible.dart` | `v3.38` |
| `duration` | Use animationStyle instead. | `widgets/expansible.dart` | `v3.38` |
| `reverseCurve` | Use animationStyle instead. | `widgets/expansible.dart` | `v3.38` |

## First stable release: Flutter 3.38  (7 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `focusable` | Use focused instead. Setting focused automatically set focusable. | `semantics/semantics.dart` | `v3.36` |
| `isFocusable` | Check if isFocused is null instead. | `semantics/semantics.dart` | `v3.36` |
| `announce` | Use sendAnnouncement instead. This API is incompatible with multiple windows. | `semantics/semantics_service.dart` | `v3.35` |
| `findChildIndexCallback` | Use findItemIndexCallback instead. findChildIndexCallback returns child indices (which include separators), while findItemIndexCallback returns item indices (which do not). If you were multiplying results by 2 to account for separators, you can remove that workaround when migrating to findItemIndexCallback. | `widgets/scroll_view.dart` | `v3.37` |
| `findChildIndexCallback` | Use findItemIndexCallback instead. findChildIndexCallback returns child indices (which include separators), while findItemIndexCallback returns item indices (which do not). If you were multiplying results by 2 to account for separators, you can remove that workaround when migrating to findItemIndexCallback. | `widgets/sliver.dart` | `v3.37` |
| `getNotifier` | Use TickerMode.getValuesNotifier to get both enabled and forceFrames. | `widgets/ticker_provider.dart` | `v3.35` |
| `of` | Use TickerMode.valuesOf to get both enabled and forceFrames. | `widgets/ticker_provider.dart` | `v3.35` |

## First stable release: Flutter 3.35  (19 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `alpha` | Use (*.a * 255.0).round().clamp(0, 255). | `cupertino/colors.dart` | `v3.33` |
| `blue` | Use (*.b * 255.0).round().clamp(0, 255). | `cupertino/colors.dart` | `v3.33` |
| `green` | Use (*.g * 255.0).round().clamp(0, 255). | `cupertino/colors.dart` | `v3.33` |
| `opacity` | Use .a. | `cupertino/colors.dart` | `v3.33` |
| `red` | Use (*.r * 255.0).round().clamp(0, 255). | `cupertino/colors.dart` | `v3.33` |
| `value` | Use component accessors like .r or .g, or toARGB32 for an explicit conversion. | `cupertino/colors.dart` | `v3.33` |
| `withOpacity` | Use .withValues() to avoid precision loss. | `cupertino/colors.dart` | `v3.33` |
| `groupValue` | Use a RadioGroup ancestor to manage group value instead. | `cupertino/radio.dart` | `v3.32` |
| `onChanged` | Use RadioGroup to handle value change instead. | `cupertino/radio.dart` | `v3.32` |
| `pageBuilder` | Use scrollableBuilder instead. | `cupertino/sheet.dart` | `v3.33` |
| `color` | Use backgroundColor instead. | `material/app_bar_theme.dart` | `v3.33` |
| `value` | Use initialValue instead. This will set the initial value for the form field. | `material/dropdown.dart` | `v3.33` |
| `groupValue` | Use a RadioGroup ancestor to manage group value instead. | `material/radio.dart` | `v3.32` |
| `onChanged` | Use RadioGroup to handle value change instead. | `material/radio.dart` | `v3.32` |
| `checked` | Use RadioGroup.groupValue to find which radio is checked. | `material/radio_list_tile.dart` | `v3.32` |
| `groupValue` | Use a RadioGroup ancestor to manage group value instead. | `material/radio_list_tile.dart` | `v3.32` |
| `onChanged` | Use RadioGroup to handle value change instead. | `material/radio_list_tile.dart` | `v3.32` |
| `hasFlag` | Use flagsCollection instead. | `semantics/semantics.dart` | `v3.32` |
| `targetsRootOverlay` | Use OverlayPortal with root overlay instead. | `widgets/overlay.dart` | `v3.33` |

## First stable release: Flutter 3.32  (8 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `ExpansionTileController` | Use ExpansibleController instead. | `material/expansion_tile.dart` | `v3.31` |
| `year2023` | Set this flag to false to opt into the 2024 range slider appearance. Defaults to true. In the future, this flag will default to false. Use SliderThemeData to customize individual properties. | `material/range_slider.dart` | `v3.30` |
| `activeColor` | Use activeThumbColor instead. | `material/switch.dart` | `v3.31` |
| `activeColor` | Use activeThumbColor instead. | `material/switch_list_tile.dart` | `v3.31` |
| `height` | Use Tooltip.constraints instead. | `material/tooltip.dart` | `v3.30` |
| `height` | Use TooltipThemeData.constraints instead. | `material/tooltip_theme.dart` | `v3.30` |
| `flags` | Use flagsCollection instead. | `semantics/semantics.dart` | `v3.29` |
| `show` | Use showWithItems instead. | `services/text_input.dart` | `v3.29` |

## First stable release: Flutter 3.29  (16 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `minSize` | Use minimumSize instead. | `cupertino/button.dart` | `v3.28` |
| `scribbleEnabled` | Use `stylusHandwritingEnabled` instead. | `cupertino/text_field.dart` | `v3.27` |
| `iconAlignment` | Remove this parameter as it is now ignored. Use ButtonStyle.iconAlignment instead. | `material/button_style_button.dart` | `v3.28` |
| `maintainHintHeight` | Use maintainHintSize instead. This will maintain both hint height and hint width. | `material/input_decorator.dart` | `v3.28` |
| `year2023` | Set this flag to false to opt into the 2024 progress indicator appearance. Defaults to true. In the future, this flag will default to false. Use ProgressIndicatorThemeData to customize individual properties. | `material/progress_indicator.dart` | `v3.27` |
| `year2023` | Set this flag to false to opt into the 2024 progress indicator appearance. Defaults to true. In the future, this flag will default to false. Use ProgressIndicatorThemeData to customize individual properties. | `material/progress_indicator_theme.dart` | `v3.27` |
| `year2023` | Set this flag to false to opt into the 2024 slider appearance. Defaults to true. In the future, this flag will default to false. Use SliderThemeData to customize individual properties. | `material/slider.dart` | `v3.27` |
| `always` | Use ShowValueIndicator.onDrag. | `material/slider_theme.dart` | `v3.28` |
| `year2023` | Set this flag to false to opt into the 2024 slider appearance. Defaults to true. In the future, this flag will default to false. Use SliderThemeData to customize individual properties. | `material/slider_theme.dart` | `v3.27` |
| `scribbleEnabled` | Use `stylusHandwritingEnabled` instead. | `material/text_field.dart` | `v3.27` |
| `scribbleEnabled` | Use `stylusHandwritingEnabled` instead. | `material/text_form_field.dart` | `v3.27` |
| `dialogBackgroundColor` | Use DialogThemeData.backgroundColor instead. | `material/theme_data.dart` | `v3.27` |
| `indicatorColor` | Use TabBarThemeData.indicatorColor instead. | `material/theme_data.dart` | `v3.28` |
| `scribble` | Use stylusHandwriting instead. | `services/text_input.dart` | `v3.28` |
| `scribbleEnabled` | Use `stylusHandwritingEnabled` instead. | `widgets/editable_text.dart` | `v3.27` |
| `markForRemove` | Call markForComplete instead. This will let route associated future to complete when route is removed. | `widgets/navigator.dart` | `v3.27` |

## First stable release: Flutter 3.27  (10 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `inactiveColor` | Use fillColor instead. fillColor now manages the background color in all states. | `cupertino/checkbox.dart` | `v3.24` |
| `activeColor` | Use activeTrackColor instead. | `cupertino/switch.dart` | `v3.24` |
| `trackColor` | Use inactiveTrackColor instead. | `cupertino/switch.dart` | `v3.24` |
| `floatingLabelAlignment` | Invalid parameter because a collapsed decoration has no label. | `material/input_decorator.dart` | `v3.24` |
| `floatingLabelBehavior` | Invalid parameter because a collapsed decoration has no label. | `material/input_decorator.dart` | `v3.24` |
| `MaterialStateOutlineInputBorder` | Use WidgetStateInputBorder instead. Renamed to match other WidgetStateProperty objects. | `material/material_state.dart` | `v3.26` |
| `MaterialStateUnderlineInputBorder` | Use WidgetStateInputBorder instead. Renamed to match other WidgetStateProperty objects. | `material/material_state.dart` | `v3.26` |
| `resolveWith` | Use WidgetStateInputBorder.resolveWith() instead. Renamed to match other WidgetStateProperty objects. | `material/material_state.dart` | `v3.26` |
| `year2023` | Set this flag to false to opt into the 2024 progress indicator appearance. Defaults to true. In the future, this flag will default to false. Use ProgressIndicatorThemeData to customize individual properties. | `material/progress_indicator.dart` | `v3.26` |
| `onPop` | Use onPopWithResult instead. | `widgets/navigator_pop_handler.dart` | `v3.26` |

## First stable release: Flutter 3.24  (7 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `debugOutstandingSemanticsHandles` | Use SemanticsBinding.debugOutstandingSemanticsHandles instead. This API is broken (see ensureSemantics). | `rendering/object.dart` | `v3.22` |
| `ensureSemantics` | Call SemanticsBinding.ensureSemantics instead and optionally add a listener to PipelineOwner.semanticsOwner. This API is broken; it does not guarantee that semantics are actually produced. | `rendering/object.dart` | `v3.22` |
| `onPopInvoked` | Use onPopInvokedWithResult instead. | `widgets/form.dart` | `v3.22` |
| `onPopInvoked` | Override onPopInvokedWithResult instead. | `widgets/navigator.dart` | `v3.22` |
| `PopInvokedCallback` | Use PopInvokedWithResultCallback instead. | `widgets/pop_scope.dart` | `v3.22` |
| `onPopInvoked` | Use onPopInvokedWithResult instead. | `widgets/pop_scope.dart` | `v3.22` |
| `onPopInvoked` | Use onPopInvokedWithResult instead. | `widgets/routes.dart` | `v3.22` |

## First stable release: Flutter 3.22  (16 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `ButtonBar` | Use OverflowBar instead. | `material/button_bar.dart` | `v3.21` |
| `ButtonBarThemeData` | Use OverflowBar instead. | `material/button_bar_theme.dart` | `v3.21` |
| `itemExtent` | The itemExtent is already available within the scope of this function. | `material/carousel.dart` | `v3.20` |
| `MaterialPropertyResolver` | Use WidgetPropertyResolver instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialState` | Use WidgetState instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateBorderSide` | Use WidgetStateBorderSide instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateColor` | Use WidgetStateColor instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateMouseCursor` | Use WidgetStateMouseCursor instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateOutlinedBorder` | Use WidgetStateOutlinedBorder instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateProperty` | Use WidgetStateProperty instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStatePropertyAll` | Use WidgetStatePropertyAll instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStateTextStyle` | Use WidgetStateTextStyle instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `MaterialStatesController` | Use WidgetStatesController instead. Moved to the Widgets layer to make code available outside of Material. | `material/material_state.dart` | `v3.19` |
| `buttonBarTheme` | Use OverflowBar instead. | `material/theme_data.dart` | `v3.21` |
| `itemExtent` | The itemExtent is already available within the scope of this function. | `rendering/sliver_fixed_extent_list.dart` | `v3.20` |
| `debugShowWidgetInspectorOverride` | Use WidgetsBinding.instance.debugShowWidgetInspectorOverrideNotifier.value instead. | `widgets/app.dart` | `v3.20` |

## First stable release: Flutter 3.19  (67 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `KeySimulatorTransitModeVariant` | No longer supported. Transit mode is always key data only. | `flutter_test/event_simulation.dart` | `v3.18` |
| `all` | No longer supported. Transit mode is always key data only. | `flutter_test/event_simulation.dart` | `v3.18` |
| `keyDataThenRawKeyData` | No longer supported. Transit mode is always key data only. | `flutter_test/event_simulation.dart` | `v3.18` |
| `rawKeyData` | No longer supported. Transit mode is always key data only. | `flutter_test/event_simulation.dart` | `v3.18` |
| `values` | No longer supported. Transit mode is always key data only. | `flutter_test/event_simulation.dart` | `v3.18` |
| `MemoryAllocations` | Use `FlutterMemoryAllocations` instead. The class `MemoryAllocations` will be introduced in a pure Dart library. | `foundation/memory_allocations.dart` | `v3.18` |
| `background` | Use surface instead. | `material/color_scheme.dart` | `v3.18` |
| `onBackground` | Use onSurface instead. | `material/color_scheme.dart` | `v3.18` |
| `surfaceVariant` | Use surfaceContainerHighest instead. | `material/color_scheme.dart` | `v3.18` |
| `accelerateEasing` | Use Easing.legacyAccelerate (M2) or Easing.standardAccelerate (M3) instead. This curve is updated in M3. | `material/curves.dart` | `v3.18` |
| `decelerateEasing` | Use Easing.legacyDecelerate (M2) or Easing.standardDecelerate (M3) instead. This curve is updated in M3. | `material/curves.dart` | `v3.18` |
| `standardEasing` | Use Easing.legacy (M2) or Easing.standard (M3) instead. This curve is updated in M3. | `material/curves.dart` | `v3.18` |
| `anchorTapClosesMenu` | Use consumeOutsideTap instead. | `material/menu_anchor.dart` | `v3.16` |
| `keyEventManager` | No longer supported. Add a handler to HardwareKeyboard instead. | `services/binding.dart` | `v3.18` |
| `debugKeyEventSimulatorTransitModeOverride` | No longer supported. Transit mode is always key data only. | `services/debug.dart` | `v3.18` |
| `KeyDataTransitMode` | No longer supported. Transit mode is always key data only. | `services/hardware_keyboard.dart` | `v3.18` |
| `KeyEventManager` | No longer supported. Once RawKeyEvent is removed, will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `KeyMessage` | No longer supported. Once RawKeyEvent is removed, it will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `KeyMessageHandler` | No longer supported. Once KeyMessage is removed, will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `_hardwareKeyboard` | No longer supported. Once RawKeyEvent is removed, will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `events` | No longer supported. Once RawKeyEvent is removed, will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `handleKeyData` | No longer supported. Use HardwareKeyboard.instance.addHandler instead. | `services/hardware_keyboard.dart` | `v3.18` |
| `handleRawKeyMessage` | No longer supported. Use HardwareKeyboard.instance.addHandler instead. | `services/hardware_keyboard.dart` | `v3.18` |
| `keyDataThenRawKeyData` | No longer supported. Transit mode is always key data only. | `services/hardware_keyboard.dart` | `v3.18` |
| `keyMessageHandler` | No longer supported. Once RawKeyEvent is removed, will no longer be needed. | `services/hardware_keyboard.dart` | `v3.18` |
| `rawKeyData` | No longer supported. Transit mode is always key data only. | `services/hardware_keyboard.dart` | `v3.18` |
| `KeyboardSide` | No longer supported. | `services/raw_keyboard.dart` | `v3.18` |
| `ModifierKey` | No longer supported. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyDownEvent` | Use KeyDownEvent instead. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyEvent` | Use KeyEvent instead. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyEventData` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyEventHandler` | Use KeyEventCallback instead. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyUpEvent` | Use KeyUpEvent instead. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyboard` | Use HardwareKeyboard instead. | `services/raw_keyboard.dart` | `v3.18` |
| `_` | Use HardwareKeyboard instead. | `services/raw_keyboard.dart` | `v3.18` |
| `data` | Use KeyEvent instead. | `services/raw_keyboard.dart` | `v3.18` |
| `fromMessage` | No longer supported. Use KeyEvent instead. | `services/raw_keyboard.dart` | `v3.18` |
| `getModifierSide` | No longer available. | `services/raw_keyboard.dart` | `v3.18` |
| `instance` | Use HardwareKeyboard.instance instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isAltPressed` | Use HardwareKeyboard.instance.isAltPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isControlPressed` | Use HardwareKeyboard.instance.isControlPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isKeyPressed` | Use HardwareKeyboard.instance.isLogicalKeyPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isMetaPressed` | Use HardwareKeyboard.instance.isMetaPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isModifierPressed` | No longer available. Inspect HardwareKeyboard.instance.logicalKeysPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `isShiftPressed` | Use HardwareKeyboard.instance.isShiftPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `modifiersPressed` | No longer available. Inspect HardwareKeyboard.instance.logicalKeysPressed instead. | `services/raw_keyboard.dart` | `v3.18` |
| `RawKeyEventDataAndroid` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_android.dart` | `v3.18` |
| `RawKeyEventDataFuchsia` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_fuchsia.dart` | `v3.18` |
| `hidUsage` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_fuchsia.dart` | `v3.18` |
| `RawKeyEventDataIos` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_ios.dart` | `v3.18` |
| `GLFWKeyHelper` | No longer supported. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `GtkKeyHelper` | No longer supported. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `KeyHelper` | No longer supported. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `RawKeyEventDataLinux` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `getModifierSide` | No longer supported. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `isModifierPressed` | No longer supported. | `services/raw_keyboard_linux.dart` | `v3.18` |
| `RawKeyEventDataMacOs` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_macos.dart` | `v3.18` |
| `RawKeyEventDataWeb` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_web.dart` | `v3.18` |
| `RawKeyEventDataWindows` | Platform specific key event data is no longer available. See KeyEvent for what is available. | `services/raw_keyboard_windows.dart` | `v3.18` |
| `FocusOnKeyCallback` | Use FocusOnKeyEventCallback instead. | `widgets/focus_manager.dart` | `v3.18` |
| `onKey` | Use onKeyEvent instead. | `widgets/focus_manager.dart` | `v3.18` |
| `onKey` | Use onKeyEvent instead. | `widgets/focus_scope.dart` | `v3.18` |
| `onPopPage` | Use onDidRemovePage instead. | `widgets/navigator.dart` | `v3.16` |
| `RawKeyboardListener` | Use KeyboardListener instead. | `widgets/raw_keyboard_listener.dart` | `v3.18` |
| `setPubRootDirectories` | Use addPubRootDirectories instead. | `widgets/service_extensions.dart` | `v3.18` |
| `isActivatedBy` | Call accepts on the activator instead. | `widgets/shortcuts.dart` | `v3.16` |
| `setPubRootDirectories` | Use addPubRootDirectories instead. | `widgets/widget_inspector.dart` | `v3.18` |

## First stable release: Flutter 3.16  (10 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `end` | Use endNode instead. This method was originally created before semantics finders were available. Semantics finders avoid edge cases where some nodes are not discoverable by widget finders and should be preferred for semantics testing. | `flutter_test/controller.dart` | `v3.15` |
| `start` | Use startNode instead. This method was originally created before semantics finders were available. Semantics finders avoid edge cases where some nodes are not discoverable by widget finders and should be preferred for semantics testing. | `flutter_test/controller.dart` | `v3.15` |
| `apply` | Override FinderBase.findInCandidates instead. Using the FinderBase API allows for more consistent caching behavior and cleaner options for interacting with the widget tree. | `flutter_test/finders.dart` | `v3.13` |
| `description` | Use FinderBase.describeMatch instead. FinderBase.describeMatch allows for more readable descriptions and removes ambiguity about pluralization. | `flutter_test/finders.dart` | `v3.13` |
| `precache` | Use FinderBase.tryFind or FinderBase.runCached instead. Using the FinderBase API allows for more consistent caching behavior and cleaner options for interacting with the widget tree. | `flutter_test/finders.dart` | `v3.13` |
| `describeEnum` | Use the `name` getter on enums instead. | `foundation/diagnostics.dart` | `v3.14` |
| `initialDate` | This parameter has no effect and can be removed. Previously it controlled the month that was used in "onChanged" when a new year was selected, but now that role is filled by "selectedDate" instead. | `material/calendar_date_picker.dart` | `v3.13` |
| `useMaterial3` | Use a ThemeData constructor (.from, .light, or .dark) instead. These constructors all have a useMaterial3 argument, and they set appropriate default values based on its value. See the useMaterial3 API documentation for full details. | `material/theme_data.dart` | `v3.13` |
| `onAccept` | Use onAcceptWithDetails instead. This callback is similar to onAcceptWithDetails but does not provide drag details. | `widgets/drag_target.dart` | `v3.14` |
| `onWillAccept` | Use onWillAcceptWithDetails instead. This callback is similar to onWillAcceptWithDetails but does not provide drag details. | `widgets/drag_target.dart` | `v3.14` |

## First stable release: Flutter 3.13  (36 deprecated members)

| Deprecated | Replacement / guidance | Source file | Marker |
| :--- | :--- | :--- | :--- |
| `additionalTime` | This is no longer supported and has no effect. | `flutter_test/widget_tester.dart` | `v3.12` |
| `AbstractNode` | If needed, inline any required functionality of AbstractNode in your class directly. | `foundation/node.dart` | `v3.12` |
| `hitTest` | Use hitTestInView and specify the view to hit test. | `gestures/binding.dart` | `v3.11` |
| `hitTest` | Use hitTestInView and specify the view to hit test. | `gestures/hit_test.dart` | `v3.11` |
| `reorderItemDown` | Use the reorderItemDown from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `reorderItemLeft` | Use the reorderItemLeft from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `reorderItemRight` | Use the reorderItemRight from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `reorderItemToEnd` | Use the reorderItemToEnd from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `reorderItemToStart` | Use the reorderItemToStart from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `reorderItemUp` | Use the reorderItemUp from WidgetsLocalizations instead. | `material/material_localizations.dart` | `v3.10` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `material/selectable_text.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `painting/text_painter.dart` | `v3.12` |
| `textScaleFactor` | Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `painting/text_scaler.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `painting/text_style.dart` | `v3.12` |
| `pipelineOwner` | Interact with the pipelineOwner tree rooted at RendererBinding.rootPipelineOwner instead. Or instead of accessing the SemanticsOwner of any PipelineOwner interact with the SemanticsBinding directly. | `rendering/binding.dart` | `v3.10` |
| `renderView` | Consider using RendererBinding.renderViews instead as the binding may manage multiple RenderViews. | `rendering/binding.dart` | `v3.10` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `rendering/editable.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `rendering/paragraph.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/basic.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/editable_text.dart` | `v3.12` |
| `onWillPop` | Use canPop and/or onPopInvokedWithResult instead. | `widgets/form.dart` | `v3.12` |
| `maybeTextScaleFactorOf` | Use maybeTextScalerOf instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/media_query.dart` | `v3.12` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/media_query.dart` | `v3.12` |
| `textScaleFactorOf` | Use textScalerOf instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/media_query.dart` | `v3.12` |
| `WillPopCallback` | Use PopInvokedCallback instead. | `widgets/navigator.dart` | `v3.12` |
| `willPop` | Use popDisposition instead. | `widgets/navigator.dart` | `v3.12` |
| `addScopedWillPopCallback` | Use registerPopEntry or PopScope instead. | `widgets/routes.dart` | `v3.12` |
| `hasScopedWillPopCallback` | Use popDisposition instead. | `widgets/routes.dart` | `v3.12` |
| `removeScopedWillPopCallback` | Use unregisterPopEntry or PopScope instead. | `widgets/routes.dart` | `v3.12` |
| `willPop` | Use popDisposition instead. | `widgets/routes.dart` | `v3.12` |
| `SlottedMultiChildRenderObjectWidgetMixin` | Extend SlottedMultiChildRenderObjectWidget instead of mixing in SlottedMultiChildRenderObjectWidgetMixin. | `widgets/slotted_render_object_widget.dart` | `v3.10` |
| `textScaleFactor` | Use textScaler instead. Use of textScaleFactor was deprecated in preparation for the upcoming nonlinear text scaling support. | `widgets/text.dart` | `v3.12` |
| `deprecatedDoNotUseWillBeRemovedWithoutNoticePipelineOwner` | Do not use. This parameter only exists to implement the deprecated RendererBinding.pipelineOwner property until it is removed. | `widgets/view.dart` | `v3.10` |
| `deprecatedDoNotUseWillBeRemovedWithoutNoticeRenderView` | Do not use. This parameter only exists to implement the deprecated RendererBinding.renderView property until it is removed. | `widgets/view.dart` | `v3.10` |
| `WillPopScope` | Use PopScope instead. The Android predictive back feature will not work with WillPopScope. | `widgets/will_pop_scope.dart` | `v3.12` |
| `key` | Use PopScope instead. The Android predictive back feature will not work with WillPopScope. | `widgets/will_pop_scope.dart` | `v3.12` |

---

## Removed, not deprecated — these no longer exist in the SDK

Verified absent from the current stable tree (`git grep 'class FlatButton'` returns nothing).
Code using them does not compile at all, so treat them as hard build breaks, not warnings:

| Removed API | Modern equivalent |
| :--- | :--- |
| `FlatButton` | `TextButton` |
| `RaisedButton` | `ElevatedButton` |
| `OutlineButton` | `OutlinedButton` |
| `TextTheme.headline1` … `headline6`, `bodyText1/2`, `subtitle1/2` | `displayLarge` … `bodyLarge`, `titleMedium` … |
| `ThemeData.accentColor` | `ColorScheme.secondary` |
| `Scaffold.of(context).showSnackBar(...)` | `ScaffoldMessenger.of(context).showSnackBar(...)` |
| `ThemeData.toggleableActiveColor` | per-widget `WidgetStateProperty` colors |

