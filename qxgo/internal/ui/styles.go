package ui

import "github.com/charmbracelet/lipgloss"

var (
	// Colors
	colorSuccess = lipgloss.Color("#04B575")
	colorError   = lipgloss.Color("#FF4545")
	colorWarning = lipgloss.Color("#FFAA00")
	colorInfo    = lipgloss.Color("#00AAFF")
	colorMuted   = lipgloss.Color("#888888")

	// Status styles
	SuccessStyle = lipgloss.NewStyle().
			Foreground(colorSuccess).
			Bold(true)

	ErrorStyle = lipgloss.NewStyle().
			Foreground(colorError).
			Bold(true)

	WarningStyle = lipgloss.NewStyle().
			Foreground(colorWarning).
			Bold(true)

	InfoStyle = lipgloss.NewStyle().
			Foreground(colorInfo)

	MutedStyle = lipgloss.NewStyle().
			Foreground(colorMuted)

	// Box styles
	BoxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colorInfo).
			Padding(0, 1)

	ErrorBoxStyle = lipgloss.NewStyle().
			Border(lipgloss.RoundedBorder()).
			BorderForeground(colorError).
			Padding(0, 1)

	// Header styles
	HeaderStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(colorInfo).
			MarginBottom(1)

	// Linter name style
	LinterNameStyle = lipgloss.NewStyle().
			Bold(true).
			Foreground(colorInfo)
)

// Status icons
const (
	IconSuccess = "✓"
	IconError   = "✗"
	IconPending = "○"
	IconRunning = "◉"
)
