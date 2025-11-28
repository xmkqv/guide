// Package hook provides functionality for parsing and processing Claude Code hook data.
// It handles JSON input from stdin containing tool invocation details for Edit and Write operations.
package hook

import (
	"encoding/json"
	"fmt"
	"io"
)

// HookData represents the JSON structure passed to the hook via stdin
type HookData struct {
	ToolName  string    `json:"tool_name"`
	ToolInput ToolInput `json:"tool_input"`
}

// ToolInput contains the parameters passed to the tool
type ToolInput struct {
	FilePath  string `json:"file_path"`
	OldString string `json:"old_string"` // For Edit operations
	NewString string `json:"new_string"` // For Edit operations
	Content   string `json:"content"`    // For Write operations
}

// ParseHookData reads and parses hook data from an io.Reader (typically stdin)
func ParseHookData(r io.Reader) (*HookData, error) {
	data, err := io.ReadAll(r)
	if err != nil {
		return nil, fmt.Errorf("failed to read hook data: %w", err)
	}

	var hookData HookData
	if err := json.Unmarshal(data, &hookData); err != nil {
		return nil, fmt.Errorf("failed to parse hook JSON: %w", err)
	}

	return &hookData, nil
}

// GetValidationContent returns the content that should be validated
// For Edit operations, returns the new_string
// For Write operations, returns the full content
func (h *HookData) GetValidationContent() string {
	if h.ToolName == "Edit" {
		return h.ToolInput.NewString
	}
	return h.ToolInput.Content
}

// GetFullContent returns the full file content for linter validation
// Returns empty string for Edit operations (Edit operations only validate changes)
// Returns full content for Write operations
func (h *HookData) GetFullContent() string {
	if h.ToolName == "Edit" {
		return ""
	}
	return h.ToolInput.Content
}

// IsEditOperation returns true if this is an Edit operation
func (h *HookData) IsEditOperation() bool {
	return h.ToolName == "Edit"
}

// IsWriteOperation returns true if this is a Write operation
func (h *HookData) IsWriteOperation() bool {
	return h.ToolName == "Write"
}
