// Logic to handle search indexing and functionality
//
// Uses the library FlexSearch for searching:
// https://github.com/nextapps-de/flexsearch
//
// Code created with LLM-assistance (I don't like JavaScript).

// Wrap everything in an IIFE to avoid polluting global scope
// See: https://developer.mozilla.org/en-US/docs/Glossary/IIFE
(function() {
  'use strict';

  // Private variables
  let index = null;
  let data = null;
  let isInitialized = false;
  let searchTimeout = null;

  // DOM elements (cached)
  let elements = {};

  // Configuration
  const CONFIG = {
    debounceDelay: 10, // ms to wait before searching as user types
    minQueryLength: 2   // minimum characters before triggering live search
  };

  // Initialize search functionality
  function initializeSearch() {
    // Cache DOM elements
    elements = {
      searchButton: document.getElementById('search-button'),
      searchOverlay: document.getElementById('search-overlay'),
      searchInput: document.getElementById('search-input'),
      searchForm: document.getElementById('search-form'),
      searchResults: document.getElementById('search-results'),
      searchCount: document.getElementById('search-count'),
      searchClear: document.getElementById('search-clear')
    };

    // Validate required elements exist
    const requiredElements = ['searchButton', 'searchOverlay', 'searchInput', 'searchForm'];
    const missingElements = requiredElements.filter(key => !elements[key]);
    
    if (missingElements.length > 0) {
      console.error('Search initialization failed: Missing elements:', missingElements);
      return;
    }

    // Set up event listeners
    setupEventListeners();

    // Load search index
    loadSearchIndex();
  }

  // Set up all event listeners
  function setupEventListeners() {
    // Open search overlay
    elements.searchButton.addEventListener('click', () => {
      elements.searchOverlay.classList.add('show');
      elements.searchInput.focus();
    });

    // Add / key to open overlay
    document.addEventListener('keydown', (e) => {
      if (e.key === '/' && !elements.searchOverlay.classList.contains('show')) {
        e.preventDefault();
        elements.searchOverlay.classList.add('show');
        elements.searchInput.focus();
      }
    });

    // Close modal when clicking outside
    elements.searchOverlay.addEventListener('click', (e) => {
      if (e.target === elements.searchOverlay) {
        closeSearchOverlay();
      }
    });

    // Clear search results
    elements.searchClear.addEventListener('click', () => {
      clearSearchResults();
      elements.searchInput.focus();
    });

    // Handle search form submission (still needed for Enter key)
    elements.searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      if (searchTimeout) {
        clearTimeout(searchTimeout);
      }
      performSearch();
    });

    // Live search - search as user types
    elements.searchInput.addEventListener('input', handleLiveSearch);

    // Escape key to close overlay
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && elements.searchOverlay.classList.contains('show')) {
        closeSearchOverlay();
      }
    });
  }

  // Handle live search with debouncing
  function handleLiveSearch() {
    const query = elements.searchInput.value.trim();

    // Clear previous timeout
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }

    // Clear results if query is too short (but don't clear the input!)
    if (query.length < CONFIG.minQueryLength) {
      elements.searchResults.innerHTML = '';
      elements.searchCount.textContent = '';
      elements.searchClear.classList.remove('show');
      return;
    }

    // Debounce: wait for user to stop typing
    searchTimeout = setTimeout(() => {
      performSearch();
    }, CONFIG.debounceDelay);
  }

  // Load and initialize the search index
  function loadSearchIndex() {
    fetch('/static/search_index.json')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(jsonData => {
        if (!Array.isArray(jsonData) || jsonData.length === 0) {
          throw new Error('Invalid search index data');
        }

        data = jsonData;

        // Check if FlexSearch is available
        if (typeof FlexSearch === 'undefined') {
          throw new Error('FlexSearch library not loaded');
        }

        // Initialize FlexSearch with fuzzy matching
        index = new FlexSearch.Document({
          document: {
            id: "id",
            index: ["title"]
          },
          tokenize: "forward",
          resolution: 3,
          // Enable fuzzy matching
          matcher: {
            // Allow 1 character difference for fuzzy matching
            threshold: 1,
            depth: 3
          },
          // Optimize for partial matching
          context: {
            resolution: 3,
            depth: 2,
            bidirectional: true
          }
        });

        // Add all items to index
        data.forEach(item => index.add(item));
        
        isInitialized = true;
        console.log('Search initialized. Indexed items:', data.length);

        // Expose search function for console debugging (optional)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
          window.debugSearch = performSearchQuery;
        }
      })
      .catch(error => {
        console.error('Failed to initialize search:', error);
        showSearchError('Search functionality is currently unavailable.');
      });
  }

  // Perform a search query
  // @param {string} query - Optional query string (uses input value if not provided)
  // @returns {Array} Search results with query for highlighting
  function performSearchQuery(query) {
    if (!isInitialized) {
      console.warn('Search not yet initialized');
      return { results: [], query: '' };
    }

    const searchQuery = query || elements.searchInput.value.trim();
    
    if (!searchQuery) {
      return { results: [], query: '' };
    }

    try {
      const results = index.search(searchQuery, {
        limit: 50,
        suggest: false
      });
      
      // Map results to full data objects
      const mappedResults = results.flatMap(result => {
        return result.result.map(id => {
          return data.find(item => item.id == id);
        }).filter(Boolean); // Remove any undefined results
      });

      return { results: mappedResults, query: searchQuery };
    } catch (error) {
      console.error('Search error:', error);
      return { results: [], query: searchQuery };
    }
  }

  // Perform search and display results
  function performSearch() {
    const query = elements.searchInput.value.trim();

    if (!query || query.length < CONFIG.minQueryLength) {
      if (!query) {
        clearSearchResults();
      }
      return;
    }

    if (!isInitialized) {
      showSearchError('Search is still loading. Please try again in a moment.');
      return;
    }

    const { results, query: searchQuery } = performSearchQuery(query);
    displayResults(results, searchQuery);
  }

  // Highlight matching text in a string
  // @param {string} text - Text to highlight in
  // @param {string} query - Query to highlight
  // @returns {string} HTML string with highlighted matches
  function highlightMatches(text, query) {
    if (!query || !text) {
      return escapeHtml(text);
    }

    let escapedText = escapeHtml(text);
    
    // Split query into individual words
    const words = query.trim().split(/\s+/).filter(word => word.length > 0);
    
    // Highlight each word separately
    words.forEach(word => {
      const escapedWord = escapeRegExp(word);
      const regex = new RegExp(`(${escapedWord})`, 'gi');
      escapedText = escapedText.replace(regex, '<mark>$1</mark>');
    });
    
    return escapedText;
  }

  // Escape HTML special characters
  // @param {string} text - Text to escape
  // @returns {string} Escaped text
  function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  // Escape special regex characters
  // @param {string} str - String to escape
  // @returns {string} Escaped string
  function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }

  // Display search results
  // @param {Array} results - Array of search result objects
  // @param {string} query - Search query for highlighting
  function displayResults(results, query) {
    elements.searchResults.innerHTML = '';

    if (results.length === 0) {
      elements.searchResults.innerHTML = '<p>No results found.</p>';
      elements.searchCount.textContent = '';
      elements.searchClear.classList.remove('show');
      return;
    }

    // Show result count
    elements.searchCount.textContent = `${results.length} result${results.length !== 1 ? 's' : ''}`;

    // Create results list
    const ul = document.createElement('ul');
    results.forEach(item => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `/post/${item.id}`;
      
      // Highlight matches in title
      a.innerHTML = highlightMatches(item.title, query);
      
      li.appendChild(a);
      ul.appendChild(li);
    });

    elements.searchResults.appendChild(ul);
    elements.searchClear.classList.add('show');
  }

  // Show error message to user
  // @param {string} message - Error message to display
  function showSearchError(message) {
    if (elements.searchResults) {
      elements.searchResults.innerHTML = `<p class="error">${escapeHtml(message)}</p>`;
    }
  }

  // Clear search results
  function clearSearchResults() {
    elements.searchInput.value = '';
    elements.searchResults.innerHTML = '';
    elements.searchCount.textContent = '';
    elements.searchClear.classList.remove('show');
    
    // Clear any pending search timeouts
    if (searchTimeout) {
      clearTimeout(searchTimeout);
    }
  }

  // Close search overlay
  function closeSearchOverlay() {
    elements.searchOverlay.classList.remove('show');
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeSearch);
  } else {
    initializeSearch();
  }

})();

