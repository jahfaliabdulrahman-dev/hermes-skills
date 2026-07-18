/// Flutter Design Lint — Core plugin entry point.
///
/// Registers 3 core rules (zero false positives):
/// 1. [HardcodedColor] — No raw Color(0x...) outside theme files
/// 2. [LtrEdgeInsets] — Force EdgeInsetsDirectional for RTL support
/// 3. [RawFontSize] — Force Theme.of(context).textTheme usage
library flutter_design_lint;

import 'package:custom_lint_builder/custom_lint_builder.dart';

import 'rules/hardcoded_color.dart';
import 'rules/ltr_edge_insets.dart';
import 'rules/raw_font_size.dart';

PluginBase createPlugin() => _FlutterDesignLint();

class _FlutterDesignLint extends PluginBase {
  @override
  List<LintRule> getLintRules(CustomLintConfigs configs) => [
        const HardcodedColor(),
        const LtrEdgeInsets(),
        const RawFontSize(),
      ];
}
