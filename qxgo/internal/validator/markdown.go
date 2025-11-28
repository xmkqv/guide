package validator

import (
	"fmt"
	"regexp"
	"strings"
)

// MarkdownIssue represents a problem found in markdown content
type MarkdownIssue struct {
	Line    int
	Column  int
	Message string
}

var (
	// Regex patterns for detecting bold text in markdown
	boldAsteriskPattern  = regexp.MustCompile(`\*\*[^*]+\*\*`)
	boldUnderscorePattern = regexp.MustCompile(`__[^_]+__`)
)

// CheckMarkdownBold checks for bold text patterns in markdown content
// Returns a slice of issues found, or empty slice if none
func CheckMarkdownBold(content string) []MarkdownIssue {
	var issues []MarkdownIssue

	lines := strings.Split(content, "\n")
	for lineNum, line := range lines {
		// Check for **bold** pattern
		if matches := boldAsteriskPattern.FindAllStringIndex(line, -1); matches != nil {
			for _, match := range matches {
				issues = append(issues, MarkdownIssue{
					Line:    lineNum + 1,
					Column:  match[0] + 1,
					Message: fmt.Sprintf("Bold text using ** is not allowed: %s", line[match[0]:match[1]]),
				})
			}
		}

		// Check for __bold__ pattern
		if matches := boldUnderscorePattern.FindAllStringIndex(line, -1); matches != nil {
			for _, match := range matches {
				issues = append(issues, MarkdownIssue{
					Line:    lineNum + 1,
					Column:  match[0] + 1,
					Message: fmt.Sprintf("Bold text using __ is not allowed: %s", line[match[0]:match[1]]),
				})
			}
		}
	}

	return issues
}
