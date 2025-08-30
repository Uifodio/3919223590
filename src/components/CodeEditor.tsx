import React, { useRef, useEffect, useState } from 'react'
import { useSyntaxHighlighting } from '../hooks/useSyntaxHighlighting'
import './CodeEditor.css'

interface CodeEditorProps {
  content: string
  language?: string
  onChange: (content: string) => void
}

const CodeEditor: React.FC<CodeEditorProps> = ({ content, language, onChange }) => {
  const textareaRef = useRef<HTMLTextAreaElement>(null)
  const lineNumbersRef = useRef<HTMLDivElement>(null)
  const [cursorPosition, setCursorPosition] = useState({ line: 1, col: 1 })
  const [selection, setSelection] = useState({ start: 0, end: 0 })
  const { highlightContent } = useSyntaxHighlighting()

  const updateLineNumbers = () => {
    if (lineNumbersRef.current) {
      const lines = content.split('\n')
      const lineNumbers = lines.map((_, index) => index + 1)
      lineNumbersRef.current.innerHTML = lineNumbers
        .map(num => `<div class="line-number">${num.toString().padStart(4, ' ')}</div>`)
        .join('')
    }
  }

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newContent = e.target.value
    onChange(newContent)
    updateCursorPosition(e.target)
  }

  const updateCursorPosition = (element: HTMLTextAreaElement) => {
    const { selectionStart } = element
    const lines = content.split('\n')
    let line = 1
    let col = 1
    
    for (let i = 0; i < lines.length; i++) {
      if (selectionStart <= lines[i].length) {
        col = selectionStart + 1
        break
      }
      selectionStart -= lines[i].length + 1
      line++
    }
    
    setCursorPosition({ line, col })
  }

  const handleScroll = () => {
    if (textareaRef.current && lineNumbersRef.current) {
      lineNumbersRef.current.scrollTop = textareaRef.current.scrollTop
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Tab') {
      e.preventDefault()
      const target = e.target as HTMLTextAreaElement
      const { selectionStart, selectionEnd } = target
      const newContent = content.substring(0, selectionStart) + '  ' + content.substring(selectionEnd)
      onChange(newContent)
      
      // Set cursor position after the inserted spaces
      setTimeout(() => {
        target.setSelectionRange(selectionStart + 2, selectionStart + 2)
      }, 0)
    } else if (e.key === 'Enter') {
      // Auto-indent
      const target = e.target as HTMLTextAreaElement
      const { selectionStart } = target
      const lines = content.split('\n')
      const currentLineIndex = content.substring(0, selectionStart).split('\n').length - 1
      const currentLine = lines[currentLineIndex] || ''
      const indentMatch = currentLine.match(/^(\s*)/)
      const indent = indentMatch ? indentMatch[1] : ''
      
      if (indent) {
        e.preventDefault()
        const newContent = content.substring(0, selectionStart) + '\n' + indent + content.substring(selectionStart)
        onChange(newContent)
        
        setTimeout(() => {
          target.setSelectionRange(selectionStart + indent.length + 1, selectionStart + indent.length + 1)
        }, 0)
      }
    }
  }

  const handleSelectionChange = () => {
    if (textareaRef.current) {
      const { selectionStart, selectionEnd } = textareaRef.current
      setSelection({ start: selectionStart, end: selectionEnd })
      updateCursorPosition(textareaRef.current)
    }
  }

  useEffect(() => {
    updateLineNumbers()
  }, [content])

  useEffect(() => {
    if (textareaRef.current) {
      updateCursorPosition(textareaRef.current)
    }
  }, [content])

  return (
    <div className="code-editor">
      <div className="line-numbers" ref={lineNumbersRef}>
        <div className="line-number">1</div>
      </div>
      
      <div className="editor-main">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={handleChange}
          onScroll={handleScroll}
          onKeyDown={handleKeyDown}
          onSelect={handleSelectionChange}
          onMouseUp={handleSelectionChange}
          className="code-textarea"
          placeholder="Start typing your code..."
          spellCheck={false}
          wrap="off"
        />
        
        <div 
          className="syntax-highlighting"
          dangerouslySetInnerHTML={{ 
            __html: highlightContent(content, language) 
          }}
        />
      </div>
    </div>
  )
}

export default CodeEditor