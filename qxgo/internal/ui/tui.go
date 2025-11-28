package ui

import (
	"context"
	"fmt"
	"strings"
	"time"

	"github.com/charmbracelet/bubbles/spinner"
	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
	"qxgo/internal/config"
	"qxgo/internal/validator"
)

type linterState int

const (
	statePending linterState = iota
	stateRunning
	stateDone
	stateFailed
)

type linterStatus struct {
	name   string
	state  linterState
	result *validator.LintResult
}

// Model represents the TUI state
type Model struct {
	validator       *validator.Validator
	input           validator.ValidationInput
	spinner         spinner.Model
	linters         []linterStatus
	markdownIssues  []validator.MarkdownIssue
	validationDone  bool
	validationError error
	result          *validator.ValidationResult
	quitting        bool
}

type validationCompleteMsg struct {
	result *validator.ValidationResult
	err    error
}

// NewModel creates a new TUI model
func NewModel(cfg *config.Config, input validator.ValidationInput, linterNames []string) Model {
	s := spinner.New()
	s.Spinner = spinner.Dot
	s.Style = lipgloss.NewStyle().Foreground(colorInfo)

	linters := make([]linterStatus, len(linterNames))
	for i, name := range linterNames {
		linters[i] = linterStatus{
			name:  name,
			state: statePending,
		}
	}

	return Model{
		validator: validator.New(cfg),
		input:     input,
		spinner:   s,
		linters:   linters,
	}
}

func (m Model) Init() tea.Cmd {
	return tea.Batch(
		m.spinner.Tick,
		m.runValidation,
	)
}

func (m Model) runValidation() tea.Msg {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	result, err := m.validator.Validate(ctx, m.input)
	return validationCompleteMsg{result: result, err: err}
}

func (m Model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "q", "ctrl+c":
			m.quitting = true
			return m, tea.Quit
		}

	case validationCompleteMsg:
		m.validationDone = true
		m.validationError = msg.err
		m.result = msg.result

		if msg.result != nil {
			m.markdownIssues = msg.result.MarkdownIssues
			// Update linter states based on results
			for i, lr := range msg.result.LintResults {
				if i < len(m.linters) {
					m.linters[i].result = &lr
					if lr.Passed {
						m.linters[i].state = stateDone
					} else {
						m.linters[i].state = stateFailed
					}
				}
			}
		}

		// Auto-quit after showing results briefly
		return m, tea.Sequence(
			tea.Tick(500*time.Millisecond, func(t time.Time) tea.Msg {
				return tea.Quit()
			}),
		)

	case spinner.TickMsg:
		var cmd tea.Cmd
		m.spinner, cmd = m.spinner.Update(msg)
		return m, cmd
	}

	return m, nil
}

func (m Model) View() string {
	if m.quitting {
		return ""
	}

	var b strings.Builder

	// Header
	b.WriteString(HeaderStyle.Render("🔍 Validating file changes..."))
	b.WriteString("\n\n")

	// Show markdown validation
	if len(m.markdownIssues) > 0 {
		b.WriteString(ErrorStyle.Render("✗ Markdown validation failed"))
		b.WriteString("\n")
		for _, issue := range m.markdownIssues {
			b.WriteString(fmt.Sprintf("  Line %d, Col %d: %s\n", issue.Line, issue.Column, issue.Message))
		}
		b.WriteString("\n")
	}

	// Show linter statuses
	if len(m.linters) > 0 {
		b.WriteString("Linters:\n")
		for _, ls := range m.linters {
			b.WriteString(m.renderLinterStatus(ls))
			b.WriteString("\n")
		}
	}

	// Show validation error
	if m.validationError != nil {
		b.WriteString("\n")
		b.WriteString(ErrorBoxStyle.Render(fmt.Sprintf("Error: %v", m.validationError)))
		b.WriteString("\n")
	}

	// Show final result
	if m.validationDone && m.result != nil {
		b.WriteString("\n")
		if m.result.HasErrors {
			b.WriteString(ErrorBoxStyle.Render("⚠️  Validation issues found - please review"))
		} else {
			b.WriteString(BoxStyle.Render("✓ All checks passed"))
		}
		b.WriteString("\n")
	}

	return b.String()
}

func (m Model) renderLinterStatus(ls linterStatus) string {
	var icon, status string

	switch ls.state {
	case statePending:
		icon = MutedStyle.Render(IconPending)
		status = MutedStyle.Render("pending")
	case stateRunning:
		icon = m.spinner.View()
		status = InfoStyle.Render("running")
	case stateDone:
		icon = SuccessStyle.Render(IconSuccess)
		status = SuccessStyle.Render("passed")
	case stateFailed:
		icon = ErrorStyle.Render(IconError)
		status = ErrorStyle.Render("failed")
	}

	line := fmt.Sprintf("  %s %s %s", icon, LinterNameStyle.Render(ls.name), status)

	// If failed and we have output, show it
	if ls.state == stateFailed && ls.result != nil && ls.result.Output != "" {
		line += "\n"
		// Show first few lines of output
		outputLines := strings.Split(ls.result.Output, "\n")
		maxLines := 5
		if len(outputLines) > maxLines {
			outputLines = outputLines[:maxLines]
			outputLines = append(outputLines, MutedStyle.Render("  ... (truncated)"))
		}
		for _, ol := range outputLines {
			if ol != "" {
				line += MutedStyle.Render(fmt.Sprintf("    %s", ol)) + "\n"
			}
		}
	}

	return line
}

// Run starts the TUI and returns the validation result
func Run(cfg *config.Config, input validator.ValidationInput, linterNames []string) (*validator.ValidationResult, error) {
	m := NewModel(cfg, input, linterNames)
	p := tea.NewProgram(m)

	finalModel, err := p.Run()
	if err != nil {
		return nil, fmt.Errorf("TUI error: %w", err)
	}

	finalM := finalModel.(Model)
	if finalM.validationError != nil {
		return nil, finalM.validationError
	}

	return finalM.result, nil
}
