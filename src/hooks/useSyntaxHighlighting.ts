import { useState, useCallback } from 'react'

export function useSyntaxHighlighting() {
  const [highlightedContent, setHighlightedContent] = useState<string>('')

  const processSyntax = useCallback((content: string, language?: string) => {
    if (!language || language === 'text') {
      return content
    }

    let processed = content

    // Common patterns for multiple languages
    const patterns = {
      // Keywords (blue)
      keywords: /\b(if|else|for|while|do|switch|case|break|continue|return|function|class|public|private|protected|static|final|abstract|interface|extends|implements|import|export|const|let|var|try|catch|finally|throw|new|this|super|null|undefined|true|false|void|int|float|double|string|bool|boolean|char|byte|long|short)\b/g,
      
      // Strings (orange)
      strings: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'|`([^`\\]|\\.)*`/g,
      
      // Comments (green)
      comments: /\/\*[\s\S]*?\*\/|\/\/.*$/gm,
      
      // Numbers (light green)
      numbers: /\b\d+\.?\d*\b/g,
      
      // Functions (yellow)
      functions: /\b\w+(?=\s*\()/g
    }

    // Language-specific patterns
    const languagePatterns: Record<string, any> = {
      python: {
        keywords: /\b(if|else|elif|for|while|def|class|import|from|as|return|try|except|finally|raise|with|lambda|yield|global|nonlocal|True|False|None|and|or|not|in|is|del|pass|break|continue)\b/g,
        strings: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'|"""[\s\S]*?"""|'''[\s\S]*?'''/g,
        comments: /#.*$/gm,
        functions: /\b\w+(?=\s*\()/g,
        numbers: /\b\d+\.?\d*\b/g
      },
      csharp: {
        keywords: /\b(if|else|for|foreach|while|do|switch|case|break|continue|return|void|int|string|bool|double|float|char|byte|long|short|class|struct|interface|enum|namespace|using|public|private|protected|internal|static|readonly|const|new|this|base|virtual|override|abstract|sealed|partial|async|await|try|catch|finally|throw|lock|using|get|set|add|remove|event|delegate|params|ref|out|in|var|dynamic|object|null|true|false|default|checked|unchecked|fixed|stackalloc|sizeof|typeof|is|as|operator|implicit|explicit|extern|unsafe|volatile|override|readonly|sealed|static|unsafe|virtual|volatile|yield|where|select|from|group|into|orderby|let|join|on|equals|by|ascending|descending)\b/g,
        strings: /"([^"\\]|\\.)*"|@".*?"/g,
        comments: /\/\*[\s\S]*?\*\/|\/\/.*$/gm,
        functions: /\b\w+(?=\s*\()/g,
        numbers: /\b\d+\.?\d*\b/g
      },
      javascript: {
        keywords: /\b(if|else|for|while|do|switch|case|break|continue|return|function|class|const|let|var|try|catch|finally|throw|new|this|super|null|undefined|true|false|void|typeof|instanceof|delete|in|of|yield|await|async|get|set|static|extends|implements|interface|enum|export|import|default|from|as|module|require|debugger|with|strict|use|target|arguments|callee|caller|prototype|constructor|__proto__|__defineGetter__|__defineSetter__|__lookupGetter__|__lookupSetter__|__noSuchMethod__|__count__|__parent__|__proto__|__defineGetter__|__defineSetter__|__lookupGetter__|__lookupSetter__|__noSuchMethod__|__count__|__parent__)\b/g,
        strings: /"([^"\\]|\\.)*"|'([^'\\]|\\.)*'|`([^`\\]|\\.)*`/g,
        comments: /\/\*[\s\S]*?\*\/|\/\/.*$/gm,
        functions: /\b\w+(?=\s*\()/g,
        numbers: /\b\d+\.?\d*\b/g
      }
    }

    const currentPatterns = languagePatterns[language] || patterns

    // Apply highlighting
    processed = processed
      .replace(currentPatterns.keywords, '<span class="keyword">$&</span>')
      .replace(currentPatterns.strings, '<span class="string">$&</span>')
      .replace(currentPatterns.comments, '<span class="comment">$&</span>')
      .replace(currentPatterns.numbers, '<span class="number">$&</span>')
      .replace(currentPatterns.functions, '<span class="function">$&</span>')

    return processed
  }, [])

  const highlightContent = useCallback((content: string, language?: string) => {
    const highlighted = processSyntax(content, language)
    setHighlightedContent(highlighted)
    return highlighted
  }, [processSyntax])

  return {
    highlightedContent,
    highlightContent,
    processSyntax
  }
}