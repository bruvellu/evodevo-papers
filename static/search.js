document.addEventListener('DOMContentLoaded', function() {
  const searchButton = document.getElementById('search-button');
  const searchOverlay = document.getElementById('search-overlay');

  searchButton.addEventListener('click', () => {
    searchOverlay.classList.add('show');
    document.getElementById('search-input').focus();
  });

  // Close modal when clicking outside the form
  searchOverlay.addEventListener('click', (e) => {
    if (e.target === searchOverlay) {
      searchOverlay.classList.remove('show');
    }
  });

  document.getElementById('search-clear').addEventListener('click', function() {
    document.getElementById('search-results').innerHTML = '';
    document.getElementById('search-count').textContent = '';
    document.getElementById('search-input').focus();
    this.classList.remove('show');
  });

});




//TODO: Revise and clean up this search functions

// Store data globally for mapping
let index;
let data;

// Load data and initialize search
fetch('/static/search_index.json')
  .then(response => response.json())
  .then(jsonData => {
    data = jsonData;

    // Initialize FlexSearch
    index = new FlexSearch.Document({
      document: {
        id: "id",
        index: ["title"]
      }
    });

    data.forEach(item => index.add(item));
    console.log('Indexing complete. Total items:', data.length);

    // Global search function (for console and form)
    window.search = function(query) {
      const results = index.search(query);
      const mappedResults = results.flatMap(result => {
        return result.result.map(id => {
          return data.find(item => item.id == id);
        });
      });
      console.log('Search results:', mappedResults);
      return mappedResults;
    };

    // Form handling (only if DOM is ready)
    if (document.readyState === 'loading') {
      document.addEventListener('DOMContentLoaded', setupForm);
    } else {
      setupForm();
    }

    function setupForm() {
      const form = document.getElementById('search-form');
      if (!form) {
        console.error('Form not found!');
        return;
      }
      form.addEventListener('submit', (e) => {
        e.preventDefault();
        const query = document.getElementById('search-input').value;
        const results = search(query);
        displayResults(results);
      });
    }

    function displayResults(results) {
      const container = document.getElementById('search-results');
      const countElement = document.getElementById('search-count');
      const clearButton = document.getElementById('search-clear');
      container.innerHTML = '';
      if (results.length === 0) {
        container.innerHTML = '<p>No results found.</p>';
        countElement.textContent = '';
        clearButton.classList.remove('show');
      } else {
        countElement.textContent = `${results.length} results`;
        const ul = document.createElement('ul');
        results.forEach(item => {
          const li = document.createElement('li');
          li.innerHTML = `<a href="/post/${item.id}">${item.title}</a>`;
          ul.appendChild(li);
        });
        container.appendChild(ul);
        clearButton.classList.add('show');
      }
    }

  })
  .catch(error => {
    console.error('Error:', error);
  });
