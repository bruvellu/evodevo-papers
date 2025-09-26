// Step 1: Load your JSON index
//fetch('/static/search_index.json')
  //.then(response => {
    //if (!response.ok) {
      //throw new Error('Failed to load search_index.json');
    //}
    //return response.json();
  //})
  //.then(data => {
    //console.log('Loaded data:', data); // Debug: Log the loaded data

    //// Step 2: Initialize FlexSearch and add documents
    //const index = new FlexSearch.Document({
      //document: {
        //id: "id",
        //index: ["title"]
      //}
    //});

    //data.forEach(item => {
      //console.log('Adding item to index:', item); // Debug: Log each item
      //index.add(item);
    //});

    //console.log('Indexing complete. Total items:', data.length); // Debug: Confirm indexing
  //})
  //.catch(error => {
    //console.error('Error loading or indexing:', error);
  //});



// Step 1: Load your JSON index and initialize FlexSearch
//let index; // Declare index globally so we can access it in the console

//fetch('/static/search_index.json')
  //.then(response => response.json())
  //.then(data => {
    //console.log('Loaded data:', data);

    //// Initialize FlexSearch
    //index = new FlexSearch.Document({
      //document: {
        //id: "id",
        //index: ["title"]
      //}
    //});

    //data.forEach(item => index.add(item));
    //console.log('Indexing complete. Total items:', data.length);

    //// Step 2: Define a search function (for testing in console)
    //window.search = function(query) {
      //const results = index.search(query);
      //console.log('Search results for "' + query + '":', results);
      //return results;
    //};
  //})
  //.catch(error => {
    //console.error('Error:', error);
  //});

// Store data globally for mapping
//let index;
//let data; // Store the original data for mapping

//fetch('/static/search_index.json')
  //.then(response => response.json())
  //.then(jsonData => {
    //data = jsonData; // Store data globally
    //console.log('Loaded data:', data);

    //// Initialize FlexSearch
    //index = new FlexSearch.Document({
      //document: {
        //id: "id",
        //index: ["title"]
      //}
    //});

    //data.forEach(item => index.add(item));
    //console.log('Indexing complete. Total items:', data.length);

    //// Improved search function
    //window.search = function(query) {
      //const results = index.search(query);
      //console.log('Raw results:', results);

      //// Map IDs to actual items
      //const mappedResults = results.map(result => {
        //return data.find(item => item.id == result);
      //});

      //console.log('Mapped results:', mappedResults);
      //return mappedResults;
    //};
  //})
  //.catch(error => {
    //console.error('Error:', error);
  //});

// Store data globally for mapping
//let index;
//let data; // Store the original data for mapping

//fetch('/static/search_index.json')
  //.then(response => response.json())
  //.then(jsonData => {
    //data = jsonData; // Store data globally
    //console.log('Loaded data:', data);

    //// Initialize FlexSearch
    //index = new FlexSearch.Document({
      //document: {
        //id: "id",
        //index: ["title"]
      //}
    //});

    //data.forEach(item => index.add(item));
    //console.log('Indexing complete. Total items:', data.length);

    //// Improved search function
    //window.search = function(query) {
      //const results = index.search(query);
      //console.log('Raw results:', results);

      //// Correct mapping: results is an array of {field: 'title', result: [id1, id2, ...]}
      //const mappedResults = results.flatMap(result => {
        //return result.result.map(id => {
          //return data.find(item => item.id == id);
        //});
      //});

      //console.log('Mapped results:', mappedResults);
      //return mappedResults;
    //};
  //})
  //.catch(error => {
    //console.error('Error:', error);
  //});

// Store data globally for mapping
//let index;
//let data;

//fetch('/static/search_index.json')
  //.then(response => response.json())
  //.then(jsonData => {
    //data = jsonData;

    //// Initialize FlexSearch
    //index = new FlexSearch.Document({
      //document: {
        //id: "id",
        //index: ["title"]
      //}
    //});

    //data.forEach(item => index.add(item));

    //// Search function
    //function search(query) {
      //const results = index.search(query);
      //return results.flatMap(result => {
        //return result.result.map(id => {
          //return data.find(item => item.id == id);
        //});
      //});
    //}

    //// Handle form submission
    //document.addEventListener('DOMContentLoaded', () => {
      //const form = document.getElementById('search-form');
      //const input = document.getElementById('search-input');
      //const resultsContainer = document.getElementById('search-results');

      //form.addEventListener('submit', (e) => {
        //e.preventDefault();
        //const query = input.value;
        //const results = search(query);

        //// Display results
        //resultsContainer.innerHTML = '';
        //if (results.length === 0) {
          //resultsContainer.innerHTML = '<p>No results found.</p>';
        //} else {
          //results.forEach(item => {
            //const div = document.createElement('div');
            //div.innerHTML = `<a href="${item.link}">${item.title}</a>`;
            //resultsContainer.appendChild(div);
          //});
        //}
      //});
    //});
  //})
  //.catch(error => {
    //console.error('Error:', error);
  //});

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
      container.innerHTML = '';
      if (results.length === 0) {
        container.innerHTML = '<p>No results found.</p>';
      } else {
        results.forEach(item => {
          const p = document.createElement('p');
          p.innerHTML = `<a href="/post/${item.id}">${item.title}</a>`;
          container.appendChild(p);
        });
      }
    }
  })
  .catch(error => {
    console.error('Error:', error);
  });
