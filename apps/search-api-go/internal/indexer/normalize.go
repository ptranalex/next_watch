package indexer

import (
	"regexp"
	"strings"
)

var (
	wordSplitRe = regexp.MustCompile(`[\s\(\)\[\]\{\}\:\;\,\.\-\_\+\=]+`)
	parenRe     = regexp.MustCompile(`\((.*?)\)`)
)

func normalizeText(s string) string {
	return strings.ToLower(strings.TrimSpace(s))
}

func movieVariations(normalizedTitle string, includeWords bool, minWordLen int) []string {
	title := normalizeText(normalizedTitle)
	if title == "" {
		return nil
	}

	out := make([]string, 0, 16)
	seen := make(map[string]struct{}, 16)

	add := func(v string) {
		v = normalizeText(v)
		if v == "" {
			return
		}
		if _, ok := seen[v]; ok {
			return
		}
		seen[v] = struct{}{}
		out = append(out, v)
	}

	add(title)

	if strings.Contains(title, "(") && strings.Contains(title, ")") {
		mainTitle := strings.TrimSpace(strings.Split(title, "(")[0])
		add(mainTitle)

		matches := parenRe.FindAllStringSubmatch(title, -1)
		for _, m := range matches {
			if len(m) < 2 {
				continue
			}
			inner := normalizeText(m[1])
			if len(inner) > 3 {
				add(inner)
			}
		}
	}

	if includeWords {
		if minWordLen < 1 {
			minWordLen = 1
		}
		words := wordSplitRe.Split(title, -1)
		for _, w := range words {
			w = normalizeText(w)
			if w == "" || len(w) < minWordLen {
				continue
			}
			add(w)

			// Prefixes for "important" words (Python uses: if len(word) >= 5)
			if len(w) >= 5 {
				maxPrefixLen := len(w)
				if maxPrefixLen > 6 {
					maxPrefixLen = 6
				}
				for pl := minWordLen; pl < maxPrefixLen; pl++ {
					add(w[:pl])
				}
			}
		}
	}

	return out
}
