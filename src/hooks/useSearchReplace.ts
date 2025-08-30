import { useState, useCallback } from 'react'

export function useSearchReplace() {
  const [isSearchVisible, setIsSearchVisible] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [replaceQuery, setReplaceQuery] = useState('')
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0)
  const [totalMatches, setTotalMatches] = useState(0)
  const [matches, setMatches] = useState<Array<{ line: number; start: number; end: number }>>([])

  const showSearch = useCallback(() => {
    setIsSearchVisible(true)
  }, [])

  const hideSearch = useCallback(() => {
    setIsSearchVisible(false)
    setSearchQuery('')
    setReplaceQuery('')
    setCurrentMatchIndex(0)
    setTotalMatches(0)
    setMatches([])
  }, [])

  const findNext = useCallback(() => {
    if (currentMatchIndex < totalMatches - 1) {
      setCurrentMatchIndex(prev => prev + 1)
    } else {
      setCurrentMatchIndex(0) // Wrap around
    }
  }, [currentMatchIndex, totalMatches])

  const findPrevious = useCallback(() => {
    if (currentMatchIndex > 0) {
      setCurrentMatchIndex(prev => prev - 1)
    } else {
      setCurrentMatchIndex(totalMatches - 1) // Wrap around
    }
  }, [currentMatchIndex, totalMatches])

  const replace = useCallback(() => {
    // Implementation would depend on the editor content
    console.log('Replace current match with:', replaceQuery)
  }, [replaceQuery])

  const replaceAll = useCallback(() => {
    // Implementation would depend on the editor content
    console.log('Replace all matches with:', replaceQuery)
  }, [replaceQuery])

  const updateSearchQuery = useCallback((query: string) => {
    setSearchQuery(query)
    // Here you would implement the actual search logic
    // and update matches and totalMatches accordingly
  }, [])

  const updateReplaceQuery = useCallback((query: string) => {
    setReplaceQuery(query)
  }, [])

  return {
    isSearchVisible,
    searchQuery,
    replaceQuery,
    currentMatchIndex,
    totalMatches,
    matches,
    showSearch,
    hideSearch,
    findNext,
    findPrevious,
    replace,
    replaceAll,
    updateSearchQuery,
    updateReplaceQuery
  }
}