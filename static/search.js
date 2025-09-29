// Wrap everything in an IIFE to avoid polluting global scope
// See: https://developer.mozilla.org/en-US/docs/Glossary/IIFE
(function() {
  'use strict';

  // Private variables
  let index = null;
  let data = null;
  let isInitialized = false;

  // DOM elements (cached)
  let elements = {};

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

    // Handle search form submission
    elements.searchForm.addEventListener('submit', (e) => {
      e.preventDefault();
      performSearch();
    });

    // Add escape key to close overlay
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && elements.searchOverlay.classList.contains('show')) {
        closeSearchOverlay();
      }
    });
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

        // Initialize FlexSearch
        index = new FlexSearch.Document({
          document: {
            id: "id",
            index: ["title"],
          },
          // Add tokenizer settings for better search
          tokenize: "forward",
          resolution: 3
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
  // @returns {Array} Search results
  function performSearchQuery(query) {
    if (!isInitialized) {
      console.warn('Search not yet initialized');
      return [];
    }

    const searchQuery = query || elements.searchInput.value.trim();
    
    if (!searchQuery) {
      return [];
    }

    try {
      const results = index.search(searchQuery);
      
      // Map results to full data objects
      const mappedResults = results.flatMap(result => {
        return result.result.map(id => {
          return data.find(item => item.id == id);
        }).filter(Boolean); // Remove any undefined results
      });

      return mappedResults;
    } catch (error) {
      console.error('Search error:', error);
      return [];
    }
  }

  // Perform search and display results
  function performSearch() {
    const query = elements.searchInput.value.trim();

    if (!query) {
      clearSearchResults();
      return;
    }

    if (!isInitialized) {
      showSearchError('Search is still loading. Please try again in a moment.');
      return;
    }

    const results = performSearchQuery(query);
    displayResults(results);
  }

  // Display search results
  // @param {Array} results - Array of search result objects
  function displayResults(results) {
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
      a.textContent = item.title;
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
      elements.searchResults.innerHTML = `<p class="error">${message}</p>`;
    }
  }

  // Clear search results
  function clearSearchResults() {
    elements.searchInput.value = '';
    elements.searchResults.innerHTML = '';
    elements.searchCount.textContent = '';
    elements.searchClear.classList.remove('show');
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
