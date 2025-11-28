package validator

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"golang.org/x/sync/errgroup"
	"qxgo/internal/config"
)

// ValidationInput contains all information needed for validation
type ValidationInput struct {
	FilePath        string
	ChangeContent   string // For checking in changes (Edit new_string)
	FullContent     string // For linting full files (Write content)
	IsEditOperation bool
}

// ValidationResult contains the results of all validation checks
type ValidationResult struct {
	MarkdownIssues   []MarkdownIssue
	LintResults      []LintResult
	HasErrors        bool
	FormattedContent string // The formatted version of the content
	WasFormatted     bool   // Whether formatting was applied
}

// Validator orchestrates all validation checks
type Validator struct {
	cfg *config.Config
}

// New creates a new Validator
func New(cfg *config.Config) *Validator {
	return &Validator{cfg: cfg}
}

// Validate performs all applicable validations on the input
func (v *Validator) Validate(ctx context.Context, input ValidationInput) (*ValidationResult, error) {
	result := &ValidationResult{
		MarkdownIssues: []MarkdownIssue{},
		LintResults:    []LintResult{},
		HasErrors:      false,
	}

	// If no file path, nothing to validate
	if input.FilePath == "" {
		return result, nil
	}

	ext := strings.TrimPrefix(filepath.Ext(input.FilePath), ".")
	if ext == "" {
		return result, nil
	}

	// Check markdown bold text in the changes (both Edit and Write)
	if (ext == "md" || ext == "markdown") && input.ChangeContent != "" {
		issues := CheckMarkdownBold(input.ChangeContent)
		if len(issues) > 0 {
			result.MarkdownIssues = issues
			result.HasErrors = true
		}
	}

	// Skip linter validation for Edit operations (only check changes, not full file)
	if input.IsEditOperation {
		return result, nil
	}

	// For Write operations, validate full content with linters
	if input.FullContent == "" {
		return result, nil
	}

	// Create temp file for linter validation
	tempFile, err := createTempFile(input.FilePath, input.FullContent)
	if err != nil {
		return nil, fmt.Errorf("failed to create temp file: %w", err)
	}
	defer os.Remove(tempFile)

	// Run formatters first
	formatters := GetApplicableFormatters(ext, v.cfg)
	for _, formatter := range formatters {
		if err := formatter.Format(ctx, tempFile); err != nil {
			// Log but don't fail on format errors
			fmt.Fprintf(os.Stderr, "Warning: %s formatting failed: %v\n", formatter.Name(), err)
		}
	}

	// Get applicable linters
	linters := GetApplicableLinters(ext, v.cfg)
	if len(linters) == 0 {
		// Even if no linters, check if content was formatted
		formattedContent, err := os.ReadFile(tempFile)
		if err == nil && string(formattedContent) != input.FullContent {
			result.FormattedContent = string(formattedContent)
			result.WasFormatted = true
		}
		return result, nil
	}

	// Run linters concurrently
	g, gctx := errgroup.WithContext(ctx)
	results := make([]LintResult, len(linters))

	for i, linter := range linters {
		g.Go(func() error {
			results[i] = linter.Run(gctx, tempFile)
			return nil
		})
	}

	if err := g.Wait(); err != nil {
		return nil, fmt.Errorf("linter execution failed: %w", err)
	}

	// Check results for errors
	for _, lr := range results {
		result.LintResults = append(result.LintResults, lr)
		if !lr.Passed {
			result.HasErrors = true
		}
	}

	// Read back formatted content
	formattedContent, err := os.ReadFile(tempFile)
	if err == nil && string(formattedContent) != input.FullContent {
		result.FormattedContent = string(formattedContent)
		result.WasFormatted = true
	}

	return result, nil
}

// createTempFile creates a temporary file with the given content.
// The file is named with the same extension as the original file.
// Note: os.CreateTemp appends random characters to the pattern, so we use
// a two-step process to ensure the extension is preserved correctly.
func createTempFile(originalPath, content string) (string, error) {
	ext := filepath.Ext(originalPath)
	filename := filepath.Base(originalPath)
	base := strings.TrimSuffix(filename, ext)

	// Create temp file with base name pattern (without extension)
	tmpFile, err := os.CreateTemp("", base+".*")
	if err != nil {
		return "", fmt.Errorf("failed to create temp file: %w", err)
	}
	tmpFile.Close()

	// Get the temp file name and rename it to have the correct extension
	tmpName := tmpFile.Name()
	if ext != "" {
		// Replace any extension with the original extension
		newName := strings.TrimSuffix(tmpName, filepath.Ext(tmpName)) + ext
		if err := os.Rename(tmpName, newName); err != nil {
			os.Remove(tmpName)
			return "", fmt.Errorf("failed to rename temp file: %w", err)
		}
		tmpName = newName
	}

	// Write content to the renamed file
	if err := os.WriteFile(tmpName, []byte(content), 0600); err != nil {
		os.Remove(tmpName)
		return "", fmt.Errorf("failed to write temp file: %w", err)
	}

	return tmpName, nil
}
