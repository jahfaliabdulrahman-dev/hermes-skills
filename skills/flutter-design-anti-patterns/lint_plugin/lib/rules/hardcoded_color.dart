import 'package:analyzer/dart/ast/ast.dart';
import 'package:analyzer/error/listener.dart';
import 'package:custom_lint_builder/custom_lint_builder.dart';

/// AP-001: No raw `Color(0x...)` outside theme definition files.
///
/// Enforces that all colors come from Theme.of(context).colorScheme,
/// not hardcoded hex values.
///
/// **Zero false positives.** Theme definition files (matching `*theme*.dart`,
/// `*color*.dart`, `*token*.dart`) are excluded by default.
class HardcodedColor extends DartLintRule {
  static const _code = LintCode(
    name: 'hardcoded_color',
    problemMessage:
        'Hardcoded Color(0x...) — use Theme.of(context).colorScheme instead. '
        'Define colors in your theme file, not in widget code.',
    correctionMessage:
        'Replace with Theme.of(context).colorScheme.primary (or surface, '
        'secondary, tertiary, etc.)',
    errorSeverity: ErrorSeverity.ERROR,
  );

  const HardcodedColor() : super(code: _code);

  /// Override to define which files are EXCLUDED from this rule.
  /// Theme definition files where Color(0x...) is appropriate.
  bool _isThemeFile(String path) {
    final lower = path.toLowerCase();
    return lower.contains('theme') ||
        lower.contains('color') ||
        lower.contains('token') ||
        lower.contains('design_system') ||
        lower.contains('app_theme');
  }

  @override
  void run(
    CustomLintResolver resolver,
    ErrorReporter reporter,
    CustomLintContext context,
  ) {
    // Skip theme definition files — colors belong there
    if (_isThemeFile(resolver.path)) return;

    context.registry.addInstanceCreationExpression((node) {
      // Check for Color(0x...) constructor calls
      final type = node.staticType?.getDisplayString() ?? '';
      if (!type.startsWith('Color')) return;

      // Only flag Color constructors with integer arguments (hex values)
      final args = node.argumentList.arguments;
      if (args.isEmpty) return;

      final firstArg = args.first;
      if (firstArg is IntegerLiteral) {
        final hexValue = firstArg.value;
        // Flag all integer Color constructors — these are hex values
        reporter.reportErrorForNode(
          _code,
          node,
          [hexValue.toRadixString(16).toUpperCase().padLeft(8, '0')],
        );
      }
    });
  }
}
