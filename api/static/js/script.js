// DOM elements
const searchForm = document.getElementById('searchForm');
const queryInput = document.getElementById('queryInput');
const topKSelect = document.getElementById('topK');
const searchBtn = document.getElementById('searchBtn');
const resultsSection = document.getElementById('resultsSection');
const resultsContainer = document.getElementById('resultsContainer');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const queryDisplay = document.getElementById('queryDisplay');
const resultCount = document.getElementById('resultCount');

// Api configuration
const API_BASE_URL = window.location.origin;
const SEARCH_ENDPOINT = `${API_BASE_URL}/search`;

// utility functions
function showLoader() {
    searchBtn.classList.add('loading');
    searchBtn.disabled = true;
}

function hideLoader() {
    searchBtn.classList.remove('loading');
    searchBtn.disabled = false;
}

function hideAllSections() {
    resultsSection.style.display = 'none';
    errorSection.style.display = 'none';
}

function showError(message) {
    hideAllSections();
    errorMessage.textContent = message;
    errorSection.style.display = 'block';
    
 
    errorSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function showResults(data) {
    hideAllSections();
    
    queryDisplay.textContent = data.query;
    resultCount.textContent = `${data.count} result${data.count !== 1 ? 's' : ''} found`;
    
    resultsContainer.innerHTML = '';
    
    if (!data.results || data.results.length === 0) {
        showError('No documents found matching your query. Try different search terms.');
        return;
    }
    
    data.results.forEach((result, index) => {
        const resultCard = createResultCard(result, index);
        resultsContainer.appendChild(resultCard);
    });
    
    resultsSection.style.display = 'block';
    
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    card.style.animationDelay = `${index * 0.1}s`;
    
    const rankColors = [
        'linear-gradient(135deg, #667eea, #764ba2)',
        'linear-gradient(135deg, #764ba2, #f093fb)',
        'linear-gradient(135deg, #f093fb, #f5576c)'
    ];
    const rankColor = rankColors[Math.min(index, 2)];
    
    card.innerHTML = `
        <div class="result-rank" style="background: ${rankColor};">
            ${result.rank}
        </div>
        <div class="result-doc-id">
            <strong>Document ID:</strong> ${result.document_id}
        </div>
        <div class="result-score">
            Similarity Score: ${(result.score * 100).toFixed(2)}%
        </div>
    `;
    
    return card;
}

// API call 
async function performSearch(query, topK) {
    try {
        showLoader();
        
        const response = await fetch(SEARCH_ENDPOINT, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                top_k: topK
            })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Search request failed');
        }
        
        showResults(data);
        
    } catch (error) {
        console.error('Search error:', error);
        
        let errorMsg = 'Failed to connect to the search server. ';
        
        if (error.message.includes('Failed to fetch')) {
            errorMsg += 'Please ensure the Flask API is running on http://localhost:5000';
        } else {
            errorMsg += error.message;
        }
        
        showError(errorMsg);
        
    } finally {
        hideLoader();
    }
}

// Event listener
searchForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const query = queryInput.value.trim();
    const topK = parseInt(topKSelect.value);
    
    if (!query) {
        showError('Please enter a search query');
        return;
    }
    
    performSearch(query, topK);
});

// Clear error/results when user starts typing again
queryInput.addEventListener('input', () => {
    if (errorSection.style.display === 'block') {
        hideAllSections();
    }
});

// Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
    // Focus search input with '/' key
    if (e.key === '/' && document.activeElement !== queryInput) {
        e.preventDefault();
        queryInput.focus();
    }
    

    if (e.key === 'Escape' && document.activeElement === queryInput) {
        queryInput.value = '';
        queryInput.blur();
        hideAllSections();
    }
});


window.addEventListener('DOMContentLoaded', () => {
    // Focus on search input when page loads
    queryInput.focus();
    
    // Add subtle entrance animation to main elements
    document.querySelector('.header').style.opacity = '0';
    document.querySelector('.search-card').style.opacity = '0';
    
    setTimeout(() => {
        document.querySelector('.header').style.transition = 'opacity 0.8s ease-out';
        document.querySelector('.header').style.opacity = '1';
    }, 100);
    
    setTimeout(() => {
        document.querySelector('.search-card').style.transition = 'opacity 0.8s ease-out';
        document.querySelector('.search-card').style.opacity = '1';
    }, 300);
});

const sampleQueries = [
    'information retrieval',
    'database systems',
    'machine learning',
    'search engine optimization'
];

// Log sample queries to console for testing
console.log('Sample queries you can try:', sampleQueries);