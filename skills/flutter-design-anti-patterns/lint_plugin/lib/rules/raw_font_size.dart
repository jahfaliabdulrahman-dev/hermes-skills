import 'package:analyzer/dart/ast/ast.dart';
import 'package:analyzer/error/listener.dart';
import 'package:custom_lint_builder/custom_lint_builder.dart';

/// AP-007: No raw `fontSize: N` — force Theme.of(context).textTheme usage.
///
/// Detects hardcoded fontSize values in TextStyle and suggests using
/// Material 3's textTheme for consistent typography and accessibility scaling.
///
/// **Zero false positives.** Raw fontSize values bypass the theme's
/// built-in text scaling (for accessibility) and typography consistency.
/// Severity: WARNING (not ERROR) because there are legitimate edge cases
/// (e.g., clock displays, code editors).
class RawFontSize extends DartLintRule {
  static const _code = LintCode(
    name: 'raw_font_size',
    problemMessage:
        'Raw fontSize — use Theme.of(context).textTheme instead for '
        'accessibility scaling and typography consistency.',
    correctionMessage:
        'Replace with Theme.of(context).textTheme.bodyLarge (or '
        'headlineMedium, titleLarge, labelSmall, etc.)',
    errorSeverity: ErrorSeverity.WARNING,
  );

  const RawFontSize() : super(code: _code);

  @override
  void run(
    CustomLintResolver resolver,
    ErrorReporter reporter,
    CustomLintContext context,
  ) {
    context.registry.addInstanceCreationExpression((node) {
      final type = node.staticType?.getDisplayString() ?? '';

      // Only flag TextStyle constructors
      if (type != 'TextStyle') return;

      // Check for fontSize parameter
      final args = node.argumentList.arguments;
      for (final arg in args) {
        if (arg is NamedExpression) {
          final paramName = arg.name.label.name;
          if (paramName == 'fontSize') {
            reporter.reportErrorForNode(_code, arg);
            return;
          }
        }
      }
    });
  }
}
