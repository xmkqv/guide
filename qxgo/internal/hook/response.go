package hook

import (
	"encoding/json"
	"fmt"
	"strings"

	"qxgo/internal/validator"
)

// ClaudeCodeHookResponse represents the JSON structure Claude Code expects from hooks
type ClaudeCodeHookResponse struct {
	HookSpecificOutput HookSpecificOutput `json:"hookSpecificOutput"`
}

// HookSpecificOutput contains the PostToolUse specific fields
type HookSpecificOutput struct {
	HookEventName     string `json:"hookEventName"`
	Decision          string `json:"decision,omitempty"`
	Reason            string `json:"reason,omitempty"`
	AdditionalContext string `json:"additionalContext,omitempty"`
}

// BuildJSONResponse creates a Claude Code compatible JSON response from validation results
func BuildJSONResponse(result *validator.ValidationResult) (string, error) {
	// Build context message from validation results
	var contextParts []string

	// Add formatting status
	if result.WasFormatted {
		contextParts = append(contextParts, "✓ Content was auto-formatted")
	}

	// If no errors and not formatted, indicate success
	if !result.HasErrors {
		if !result.WasFormatted {
			contextParts = append(contextParts, "✓ All checks passed")
		}

		response := ClaudeCodeHookResponse{
			HookSpecificOutput: HookSpecificOutput{
				HookEventName:     "PostToolUse",
				Decision:          "approve",
				AdditionalContext: strings.Join(contextParts, "\n"),
			},
		}

		jsonBytes, err := json.MarshalIndent(response, "", "  ")
		if err != nil {
			return "", fmt.Errorf("failed to marshal JSON: %w", err)
		}
		return string(jsonBytes), nil
	}

	// Build detailed error context
	if len(result.MarkdownIssues) > 0 {
		contextParts = append(contextParts, "\nMarkdown validation errors:")
		for _, issue := range result.MarkdownIssues {
			contextParts = append(contextParts, fmt.Sprintf("  Line %d, Col %d: %s", issue.Line, issue.Column, issue.Message))
		}
	}

	// Add linter results
	for _, lr := range result.LintResults {
		if !lr.Passed {
			contextParts = append(contextParts, fmt.Sprintf("\n%s errors:", lr.Name))
			if lr.Output != "" {
				lines := strings.Split(lr.Output, "\n")
				for _, line := range lines {
					if line != "" {
						contextParts = append(contextParts, fmt.Sprintf("  %s", line))
					}
				}
			}
			if lr.Error != nil {
				contextParts = append(contextParts, fmt.Sprintf("  Error: %v", lr.Error))
			}
		}
	}

	// Add summary
	contextParts = append(contextParts, "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	contextParts = append(contextParts, "⚠️  Validation issues found above - please review and address.")
	contextParts = append(contextParts, "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

	response := ClaudeCodeHookResponse{
		HookSpecificOutput: HookSpecificOutput{
			HookEventName:     "PostToolUse",
			Decision:          "approve", // Never block, just inform
			Reason:            "Validation completed with issues",
			AdditionalContext: strings.Join(contextParts, "\n"),
		},
	}

	jsonBytes, err := json.MarshalIndent(response, "", "  ")
	if err != nil {
		return "", fmt.Errorf("failed to marshal JSON: %w", err)
	}

	return string(jsonBytes), nil
}
