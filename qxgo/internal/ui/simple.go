// Package ui provides user interface components for displaying validation results.
// It includes both interactive TUI (using Bubble Tea) and simple non-interactive output modes.
package ui

import (
	"fmt"
	"io"
	"strings"

	"qxgo/internal/validator"
)

// SimpleUI handles non-interactive output for piped/hook usage
type SimpleUI struct {
	writer io.Writer
}

// NewSimpleUI creates a new simple UI
func NewSimpleUI(w io.Writer) *SimpleUI {
	return &SimpleUI{writer: w}
}

// DisplayResult outputs validation results in a simple, parseable format
func (s *SimpleUI) DisplayResult(result *validator.ValidationResult) {
	// Show formatting status first
	if result.WasFormatted {
		fmt.Fprintln(s.writer, "✓ Content was auto-formatted")
	}

	if !result.HasErrors {
		if !result.WasFormatted {
			fmt.Fprintln(s.writer, "✓ All checks passed")
		}
		return
	}

	// Display markdown issues
	if len(result.MarkdownIssues) > 0 {
		fmt.Fprintln(s.writer, "\nMarkdown validation errors:")
		for _, issue := range result.MarkdownIssues {
			fmt.Fprintf(s.writer, "  Line %d, Col %d: %s\n", issue.Line, issue.Column, issue.Message)
		}
	}

	// Display linter results
	for _, lr := range result.LintResults {
		if !lr.Passed {
			fmt.Fprintf(s.writer, "\n%s errors:\n", lr.Name)
			if lr.Output != "" {
				// Indent each line of output
				lines := strings.Split(lr.Output, "\n")
				for _, line := range lines {
					if line != "" {
						fmt.Fprintf(s.writer, "  %s\n", line)
					}
				}
			}
			if lr.Error != nil {
				fmt.Fprintf(s.writer, "  Error: %v\n", lr.Error)
			}
		}
	}

	// Display summary separator
	fmt.Fprintln(s.writer, "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Fprintln(s.writer, "⚠️  Validation issues found above - please review and address.")
	fmt.Fprintln(s.writer, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
}
