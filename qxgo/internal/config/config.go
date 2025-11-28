// Package config manages configuration loading from environment variables.
// It provides paths to external linter configuration files.
package config

import "os"

// Config holds configuration values for the validator
type Config struct {
	BiomeConfigPath       string
	RuffConfigPath        string
	PyrightConfigPath     string
	MarkdownlintConfigPath string
}

// Load reads configuration from environment variables
func Load() *Config {
	return &Config{
		BiomeConfigPath:       os.Getenv("BIOME_CONFIG_PATH"),
		RuffConfigPath:        os.Getenv("RUFF_CONFIG_PATH"),
		PyrightConfigPath:     os.Getenv("PYRIGHT_CONFIG_PATH"),
		MarkdownlintConfigPath: os.Getenv("MARKDOWNLINT_CONFIG_PATH"),
	}
}
