package main

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/term"
	"qxgo/internal/config"
	"qxgo/internal/hook"
	"qxgo/internal/ui"
	"qxgo/internal/validator"
)

const (
	exitSuccess = 0
	exitError   = 1
)

func main() {
	os.Exit(run())
}

func run() int {
	// Parse hook data from stdin
	hookData, err := hook.ParseHookData(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing hook data: %v\n", err)
		return exitError
	}

	// If no file path, allow operation
	if hookData.ToolInput.FilePath == "" {
		return exitSuccess
	}

	// Load configuration
	cfg := config.Load()

	// Prepare validation input
	input := validator.ValidationInput{
		FilePath:        hookData.ToolInput.FilePath,
		ChangeContent:   hookData.GetValidationContent(),
		FullContent:     hookData.GetFullContent(),
		IsEditOperation: hookData.IsEditOperation(),
	}

	// Get file extension to determine applicable linters
	ext := strings.TrimPrefix(filepath.Ext(input.FilePath), ".")
	linters := validator.GetApplicableLinters(ext, cfg)
	linterNames := make([]string, len(linters))
	for i, l := range linters {
		linterNames[i] = l.Name()
	}

	// Detect if running in TTY (interactive terminal)
	isTTY := term.IsTerminal(int(os.Stdout.Fd()))

	var result *validator.ValidationResult

	if isTTY && !input.IsEditOperation && len(linters) > 0 {
		// Use TUI for interactive mode
		result, err = ui.Run(cfg, input, linterNames)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Validation error: %v\n", err)
			return exitError
		}
	} else {
		// Use simple mode for piped/hook usage
		v := validator.New(cfg)
		ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
		defer cancel()

		result, err = v.Validate(ctx, input)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Validation error: %v\n", err)
			return exitError
		}

		// Output JSON to stdout for Claude Code to read
		jsonResponse, err := hook.BuildJSONResponse(result)
		if err != nil {
			fmt.Fprintf(os.Stderr, "Error building JSON response: %v\n", err)
			return exitError
		}
		fmt.Fprintln(os.Stdout, jsonResponse)

		// Also display results to stderr for user visibility
		simpleUI := ui.NewSimpleUI(os.Stderr)
		simpleUI.DisplayResult(result)
	}

	// Always return success - we report validation issues but don't block operations
	// Claude Code will see the validation output and make the decision
	return exitSuccess
}
