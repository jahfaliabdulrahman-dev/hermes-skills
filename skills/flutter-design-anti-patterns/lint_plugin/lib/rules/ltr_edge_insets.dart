import 'package:analyzer/dart/ast/ast.dart';
import 'package:analyzer/error/listener.dart';
import 'package:custom_lint_builder/custom_lint_builder.dart';

/// AP-021: No LTR-only EdgeInsets — force EdgeInsetsDirectional for RTL support.
///
/// Detects `EdgeInsets.only(left: ...)`, `EdgeInsets.only(right: ...)`,
/// `Alignment.centerLeft`, `Alignment.topLeft`, `Alignment.bottomLeft`
/// and suggests RTL-safe alternatives.
///
/// **Zero false positives.** `EdgeInsets.only(left:)` is ALWAYS wrong in
/// an RTL-aware app. Use `EdgeInsetsDirectional.only(start:)` instead.
class LtrEdgeInsets extends DartLintRule {
  static const _code = LintCode(
    name: 'ltr_edge_insets',
    problemMessage:
        'LTR-only EdgeInsets/Alignment — use EdgeInsetsDirectional '
        'or AlignmentDirectional for RTL support.',
    correctionMessage:
        "Replace with EdgeInsetsDirectional.only(start: ...) or "
        "AlignmentDirectional.centerStart.",
    errorSeverity: ErrorSeverity.ERROR,
  );

  const LtrEdgeInsets() : super(code: _code);

  // Alignment values that are LTR-only
  static const _ltrAlignments = {
    'centerLeft',
    'topLeft',
    'bottomLeft',
  };

  @override
  void run(
    CustomLintResolver resolver,
    ErrorReporter reporter,
    CustomLintContext context,
  ) {
    // ── Catch EdgeInsets.only(left: ...) and EdgeInsets.only(right: ...) ──
    context.registry.addInstanceCreationExpression((node) {
      final type = node.staticType?.getDisplayString() ?? '';

      if (type == 'EdgeInsets' || type == 'EdgeInsetsGeometry') {
        // Check if constructor is EdgeInsets.only(...)
        final constructor = node.constructorName;
        if (constructor.name?.name == 'only') {
          // Look for `left:` or `right:` named parameters
          final args = node.argumentList.arguments;
          for (final arg in args) {
            if (arg is NamedExpression) {
              final paramName = arg.name.label.name;
              if (paramName == 'left' || paramName == 'right') {
                reporter.reportErrorForNode(_code, arg);
                return; // One report per EdgeInsets.only call
              }
            }
          }
        }
      }
    });

    // ── Catch Alignment.centerLeft, etc. ──
    context.registry.addPrefixedIdentifier((node) {
      final prefix = node.prefix.name;
      if (prefix != 'Alignment') return;
      final property = node.identifier.name;
      if (_ltrAlignments.contains(property)) {
        reporter.reportErrorForNode(_code, node);
      }
    });
  }
}
