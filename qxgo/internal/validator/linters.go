package validator

import (
	"bytes"
	"context"
	"fmt"
	"os/exec"
	"path/filepath"
	"strings"

	"qxgo/internal/config"
)

// LintResult represents the outcome of running a linter
type LintResult struct {
	Name    string
	Passed  bool
	Output  string
	Error   error
}

// Linter defines the interface for all linters
type Linter interface {
	Name() string
	Applies(ext string) bool
	Run(ctx context.Context, filePath string) LintResult
}

// BiomeLinter runs biome check on JavaScript/TypeScript files
type BiomeLinter struct {
	cfg *config.Config
}

func NewBiomeLinter(cfg *config.Config) *BiomeLinter {
	return &BiomeLinter{cfg: cfg}
}

func (l *BiomeLinter) Name() string {
	return "biome"
}

func (l *BiomeLinter) Applies(ext string) bool {
	jsExts := []string{"js", "jsx", "ts", "tsx", "mjs", "cjs"}
	for _, e := range jsExts {
		if ext == e {
			return true
		}
	}
	return false
}

func (l *BiomeLinter) Run(ctx context.Context, filePath string) LintResult {
	args := []string{"check", "--write"}
	if l.cfg.BiomeConfigPath != "" {
		// Biome's --config-path expects a directory, not a file path
		// If user provided a file path, extract the directory
		configPath := l.cfg.BiomeConfigPath
		if filepath.Ext(configPath) == ".json" {
			configPath = filepath.Dir(configPath)
		}
		args = append(args, "--config-path="+configPath)
	}
	// Disable VCS ignore file to ensure temp files are checked
	args = append(args, "--vcs-use-ignore-file=false")
	args = append(args, filePath)

	return runCommand(ctx, "biome", args)
}

// RuffLinter runs ruff check on Python files
type RuffLinter struct {
	cfg *config.Config
}

func NewRuffLinter(cfg *config.Config) *RuffLinter {
	return &RuffLinter{cfg: cfg}
}

func (l *RuffLinter) Name() string {
	return "ruff"
}

func (l *RuffLinter) Applies(ext string) bool {
	return ext == "py"
}

func (l *RuffLinter) Run(ctx context.Context, filePath string) LintResult {
	args := []string{"check", "--fix"}
	if l.cfg.RuffConfigPath != "" {
		args = append(args, "--config="+l.cfg.RuffConfigPath)
	}
	args = append(args, filePath)

	return runCommand(ctx, "ruff", args)
}

// PyrightLinter runs pyright type checker on Python files
type PyrightLinter struct {
	cfg *config.Config
}

func NewPyrightLinter(cfg *config.Config) *PyrightLinter {
	return &PyrightLinter{cfg: cfg}
}

func (l *PyrightLinter) Name() string {
	return "pyright"
}

func (l *PyrightLinter) Applies(ext string) bool {
	return ext == "py"
}

func (l *PyrightLinter) Run(ctx context.Context, filePath string) LintResult {
	args := []string{}
	if l.cfg.PyrightConfigPath != "" {
		projectDir := filepath.Dir(l.cfg.PyrightConfigPath)
		args = append(args, "--project="+projectDir)
	}
	args = append(args, filePath)

	return runCommand(ctx, "pyright", args)
}

// MarkdownlintLinter runs markdownlint on Markdown files
type MarkdownlintLinter struct {
	cfg *config.Config
}

func NewMarkdownlintLinter(cfg *config.Config) *MarkdownlintLinter {
	return &MarkdownlintLinter{cfg: cfg}
}

func (l *MarkdownlintLinter) Name() string {
	return "markdownlint"
}

func (l *MarkdownlintLinter) Applies(ext string) bool {
	return ext == "md" || ext == "markdown"
}

func (l *MarkdownlintLinter) Run(ctx context.Context, filePath string) LintResult {
	args := []string{}
	if l.cfg.MarkdownlintConfigPath != "" {
		args = append(args, "-c", l.cfg.MarkdownlintConfigPath)
	}
	args = append(args, filePath)

	return runCommand(ctx, "markdownlint", args)
}

// runCommand executes a command and returns a LintResult.
//
// VALIDATION PHILOSOPHY:
// - All linters are expected to be installed in the environment
// - Missing linters or execution failures indicate an improperly configured environment
// - Validation failures (linter finding issues) are reported informationally
// - The calling code decides whether to block based on validation results
func runCommand(ctx context.Context, name string, args []string) LintResult {
	cmd := exec.CommandContext(ctx, name, args...)

	var stdout, stderr bytes.Buffer
	cmd.Stdout = &stdout
	cmd.Stderr = &stderr

	err := cmd.Run()

	// Combine stdout and stderr for output
	output := strings.TrimSpace(stdout.String() + "\n" + stderr.String())

	result := LintResult{
		Name:   name,
		Output: output,
	}

	if err != nil {
		// Both "linter found issues" and "linter not installed" are validation issues
		// Report them informationally and let Claude Code decide
		if exitErr, ok := err.(*exec.ExitError); ok {
			result.Passed = false
			result.Error = fmt.Errorf("%s exited with code %d", name, exitErr.ExitCode())
		} else {
			result.Passed = false
			result.Error = fmt.Errorf("failed to run %s: %w", name, err)
		}
		return result
	}

	result.Passed = true
	return result
}

// Formatter defines the interface for formatters that can auto-fix content
type Formatter interface {
	Name() string
	Applies(ext string) bool
	Format(ctx context.Context, filePath string) error
}

// RuffFormatter runs ruff format on Python files
type RuffFormatter struct {
	cfg *config.Config
}

func NewRuffFormatter(cfg *config.Config) *RuffFormatter {
	return &RuffFormatter{cfg: cfg}
}

func (f *RuffFormatter) Name() string {
	return "ruff-format"
}

func (f *RuffFormatter) Applies(ext string) bool {
	return ext == "py"
}

func (f *RuffFormatter) Format(ctx context.Context, filePath string) error {
	args := []string{"format"}
	if f.cfg.RuffConfigPath != "" {
		args = append(args, "--config="+f.cfg.RuffConfigPath)
	}
	args = append(args, filePath)

	cmd := exec.CommandContext(ctx, "ruff", args...)
	return cmd.Run()
}

// GetApplicableFormatters returns all formatters that apply to the given file extension
func GetApplicableFormatters(ext string, cfg *config.Config) []Formatter {
	allFormatters := []Formatter{
		NewRuffFormatter(cfg),
	}

	var applicable []Formatter
	for _, formatter := range allFormatters {
		if formatter.Applies(ext) {
			applicable = append(applicable, formatter)
		}
	}

	return applicable
}

// GetApplicableLinters returns all linters that apply to the given file extension
func GetApplicableLinters(ext string, cfg *config.Config) []Linter {
	allLinters := []Linter{
		NewBiomeLinter(cfg),
		NewRuffLinter(cfg),
		NewPyrightLinter(cfg),
		NewMarkdownlintLinter(cfg),
	}

	var applicable []Linter
	for _, linter := range allLinters {
		if linter.Applies(ext) {
			applicable = append(applicable, linter)
		}
	}

	return applicable
}
