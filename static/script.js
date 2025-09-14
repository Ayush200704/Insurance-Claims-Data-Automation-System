// JavaScript for Insurance Claims Data Automation System

// Global variables
let charts = {};
let currentData = null;
let isLoading = false;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    
    // Test backend connection first
    testBackendConnection().then(() => {
        loadDashboardData();
    }).catch(() => {
        console.log('Backend not available, loading fallback data');
        loadFallbackData();
    });
});

// Test if backend is running
async function testBackendConnection() {
    try {
        const response = await fetch('/health', { 
            method: 'GET',
            timeout: 5000 
        });
        if (response.ok) {
            console.log('Backend is running');
            return true;
        } else {
            throw new Error('Backend not responding');
        }
    } catch (error) {
        console.error('Backend connection test failed:', error);
        throw error;
    }
}

// Initialize the application
function initializeApp() {
    console.log('Initializing Insurance Claims Data Automation System...');
    
    // Add smooth scrolling to navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add fade-in animation to sections
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.classList.add('fade-in');
    });
}

// Setup event listeners
function setupEventListeners() {
    // File upload handling
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop functionality
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);
    uploadArea.addEventListener('click', () => fileInput.click());
}

// Load dashboard data
async function loadDashboardData() {
    if (isLoading) return; // Prevent multiple simultaneous loads
    
    try {
        isLoading = true;
        console.log('Loading dashboard data...');
        
        // Load data summary
        const summaryResponse = await fetch('/api/v1/data/summary');
        if (summaryResponse.ok) {
            const summary = await summaryResponse.json();
            updateSummaryCards(summary);
            console.log('Summary data loaded successfully');
        } else {
            console.error('Failed to load summary data:', summaryResponse.status, summaryResponse.statusText);
            // Load fallback data
            loadFallbackData();
        }
        
        // Load dashboard data
        const dashboardResponse = await fetch('/api/v1/dashboard/data');
        if (dashboardResponse.ok) {
            const dashboardData = await dashboardResponse.json();
            currentData = dashboardData;
            createCharts(dashboardData);
            console.log('Dashboard data loaded successfully');
        } else {
            console.error('Failed to load dashboard data:', dashboardResponse.status, dashboardResponse.statusText);
            // Load fallback data
            loadFallbackData();
        }
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data. Please check if the backend is running and try refreshing the page.');
    } finally {
        isLoading = false;
    }
}

// Load fallback data when API fails
function loadFallbackData() {
    console.log('Loading fallback data...');
    
    // Update summary cards with sample data
    document.getElementById('totalRecords').textContent = '4,014';
    document.getElementById('claimRate').textContent = '58.5%';
    document.getElementById('avgAge').textContent = '39.2';
    document.getElementById('avgBMI').textContent = '30.7';
    document.getElementById('avgCharges').textContent = '$13,270';
    document.getElementById('smokerRate').textContent = '20.5%';
    
    // Create sample charts
    const sampleData = {
        claims_by_region: {0: 0.59, 1: 0.50, 2: 0.67, 3: 0.56},
        claims_by_age: {18: 0.67, 25: 0.54, 30: 0.37, 35: 0.24, 40: 0.37, 45: 0.69, 50: 0.66, 55: 0.69, 60: 0.61},
        smoker_impact: {0: 0.50, 1: 0.91},
        charges_distribution: {min: 1121, '25%': 4738, '50%': 9382, '75%': 16658, max: 63770}
    };
    
    createCharts(sampleData);
    showError('Using sample data. Please check if the backend is running.');
}

// Update summary cards
function updateSummaryCards(summary) {
    document.getElementById('totalRecords').textContent = summary.total_records || '-';
    document.getElementById('claimRate').textContent = formatPercentage(summary.claim_rate) || '-';
    document.getElementById('avgAge').textContent = formatNumber(summary.average_age) || '-';
    document.getElementById('avgBMI').textContent = formatNumber(summary.average_bmi) || '-';
    document.getElementById('avgCharges').textContent = formatCurrency(summary.average_charges) || '-';
    document.getElementById('smokerRate').textContent = formatPercentage(summary.smoker_rate) || '-';
}

// Create charts
function createCharts(data) {
    createRegionChart(data.claims_by_region);
    createAgeChart(data.claims_by_age);
    createSmokerChart(data.smoker_impact);
    createChargesChart(data.charges_distribution);
}

// Create region chart
function createRegionChart(regionData) {
    const ctx = document.getElementById('regionChart').getContext('2d');
    
    if (charts.regionChart) {
        charts.regionChart.destroy();
    }
    
    const regionNames = ['Northeast', 'Northwest', 'Southeast', 'Southwest'];
    const labels = Object.keys(regionData).map(key => regionNames[key] || `Region ${key}`);
    const values = Object.values(regionData);
    
    charts.regionChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    '#3498db',
                    '#e74c3c',
                    '#2ecc71',
                    '#f39c12'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        usePointStyle: true
                    }
                }
            }
        }
    });
}

// Create age chart
function createAgeChart(ageData) {
    const ctx = document.getElementById('ageChart').getContext('2d');
    
    if (charts.ageChart) {
        charts.ageChart.destroy();
    }
    
    const labels = Object.keys(ageData).sort((a, b) => parseInt(a) - parseInt(b));
    const values = labels.map(age => ageData[age]);
    
    charts.ageChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Claim Rate',
                data: values,
                borderColor: '#3498db',
                backgroundColor: 'rgba(52, 152, 219, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#3498db',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create smoker chart
function createSmokerChart(smokerData) {
    const ctx = document.getElementById('smokerChart').getContext('2d');
    
    if (charts.smokerChart) {
        charts.smokerChart.destroy();
    }
    
    const labels = ['Non-Smoker', 'Smoker'];
    const values = [smokerData[0] || 0, smokerData[1] || 0];
    
    charts.smokerChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Claim Rate',
                data: values,
                backgroundColor: [
                    'rgba(52, 152, 219, 0.8)',
                    'rgba(231, 76, 60, 0.8)'
                ],
                borderColor: [
                    '#3498db',
                    '#e74c3c'
                ],
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1,
                    ticks: {
                        callback: function(value) {
                            return (value * 100).toFixed(0) + '%';
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Create charges chart
function createChargesChart(chargesData) {
    const ctx = document.getElementById('chargesChart').getContext('2d');
    
    if (charts.chargesChart) {
        charts.chargesChart.destroy();
    }
    
    const labels = ['Min', '25%', 'Median', '75%', 'Max'];
    const values = [
        chargesData.min || 0,
        chargesData['25%'] || 0,
        chargesData['50%'] || 0,
        chargesData['75%'] || 0,
        chargesData.max || 0
    ];
    
    charts.chargesChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Charges ($)',
                data: values,
                backgroundColor: 'rgba(46, 204, 113, 0.8)',
                borderColor: '#2ecc71',
                borderWidth: 2,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

// Calculate reserves
async function calculateReserves(method) {
    try {
        const response = await fetch(`/api/v1/reserves/calculate?method=${method}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            const result = await response.json();
            updateReserveDisplay(method, result);
            showSuccess(`Reserves calculated successfully using ${result.method} method!`);
        } else {
            throw new Error('Failed to calculate reserves');
        }
        
    } catch (error) {
        console.error('Error calculating reserves:', error);
        showError('Failed to calculate reserves. Please try again.');
    }
}

// Update reserve display
function updateReserveDisplay(method, result) {
    const reserveElement = document.getElementById(getReserveElementId(method));
    if (reserveElement) {
        reserveElement.textContent = formatCurrency(result.total_reserves);
    }
}

// Get reserve element ID
function getReserveElementId(method) {
    const mapping = {
        'chain_ladder': 'chainLadderReserve',
        'bornhuetter_ferguson': 'bfReserve',
        'frequency_severity': 'fsReserve'
    };
    return mapping[method] || '';
}

// Analyze trends
async function analyzeTrends() {
    try {
        const response = await fetch('/api/v1/trends/analyze', {
            method: 'POST'
        });
        
        if (response.ok) {
            const trends = await response.json();
            displayTrendResults(trends);
            showSuccess('Trend analysis completed successfully!');
        } else {
            throw new Error('Failed to analyze trends');
        }
        
    } catch (error) {
        console.error('Error analyzing trends:', error);
        showError('Failed to analyze trends. Please try again.');
    }
}

// Display trend results
function displayTrendResults(trends) {
    const container = document.getElementById('trendResults');
    container.innerHTML = '';
    
    Object.entries(trends).forEach(([metric, data]) => {
        const trendItem = document.createElement('div');
        trendItem.className = 'trend-item';
        
        const directionClass = data.trend_direction === 'increasing' ? 'trend-increasing' :
                              data.trend_direction === 'decreasing' ? 'trend-decreasing' : 'trend-stable';
        
        trendItem.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <div>
                    <div class="trend-metric">${data.metric}</div>
                    <small class="text-muted">Strength: ${(data.trend_strength * 100).toFixed(1)}%</small>
                </div>
                <span class="trend-direction ${directionClass}">
                    ${data.trend_direction}
                </span>
            </div>
        `;
        
        container.appendChild(trendItem);
    });
}

// Generate Excel report
async function generateExcelReport() {
    try {
        const response = await fetch('/api/v1/dashboard/excel');
        
        if (response.ok) {
            const result = await response.json();
            showSuccess('Excel report generated successfully!');
            
            // Create download link using the API endpoint
            const link = document.createElement('a');
            link.href = `/api/v1/dashboard/download/${result.filename}`;
            link.download = result.filename;
            link.click();
        } else {
            const errorText = await response.text();
            console.error('API Error:', response.status, errorText);
            throw new Error(`Failed to generate Excel report: ${response.status}`);
        }
        
    } catch (error) {
        console.error('Error generating Excel report:', error);
        showError('Failed to generate Excel report. Please try again.');
    }
}

// Download report
function downloadReport() {
    generateExcelReport();
}

// File upload handling
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        processFile(file);
    }
}

// Drag and drop handling
function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.classList.add('dragover');
}

function handleDragLeave(event) {
    event.currentTarget.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.classList.remove('dragover');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        processFile(files[0]);
    }
}

// Process uploaded file
async function processFile(file) {
    if (!file.name.toLowerCase().endsWith('.csv')) {
        showError('Please upload a CSV file.');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        showUploadProgress();
        
        const response = await fetch('/upload-data', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            const result = await response.json();
            showUploadResults(result);
            // Reload dashboard data
            setTimeout(() => {
                loadDashboardData();
            }, 1000);
        } else {
            throw new Error('Failed to upload file');
        }
        
        hideUploadProgress();
    } catch (error) {
        console.error('Error uploading file:', error);
        hideUploadProgress();
        showError('Failed to upload file. Please try again.');
    }
}

// Show upload progress
function showUploadProgress() {
    document.getElementById('uploadProgress').style.display = 'block';
    document.getElementById('uploadResults').style.display = 'none';
}

// Hide upload progress
function hideUploadProgress() {
    document.getElementById('uploadProgress').style.display = 'none';
}

// Show upload results
function showUploadResults(result) {
    const resultsDiv = document.getElementById('uploadResults');
    const statsDiv = document.getElementById('uploadStats');
    
    statsDiv.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <strong>Records Processed:</strong> ${result.results.records_processed}
            </div>
            <div class="col-md-6">
                <strong>Records Loaded:</strong> ${result.results.records_loaded}
            </div>
        </div>
        <div class="row mt-2">
            <div class="col-md-6">
                <strong>Model Accuracy:</strong> ${(result.results.model_performance.accuracy * 100).toFixed(2)}%
            </div>
            <div class="col-md-6">
                <strong>Claim Rate:</strong> ${(result.results.summary_statistics.claim_rate * 100).toFixed(2)}%
            </div>
        </div>
    `;
    
    resultsDiv.style.display = 'block';
}

// Utility functions
function formatCurrency(value) {
    if (value === null || value === undefined) return '-';
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(value);
}

function formatPercentage(value) {
    if (value === null || value === undefined) return '-';
    return (value * 100).toFixed(1) + '%';
}

function formatNumber(value) {
    if (value === null || value === undefined) return '-';
    return value.toFixed(1);
}

// Loading functions removed - no longer needed

// Show success message
function showSuccess(message) {
    showAlert(message, 'success');
}

// Show error message
function showError(message) {
    showAlert(message, 'danger');
}

// Show alert
function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alertDiv);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.parentNode.removeChild(alertDiv);
        }
    }, 5000);
}

// Scroll to section
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Resize charts on window resize
window.addEventListener('resize', function() {
    Object.values(charts).forEach(chart => {
        if (chart) {
            chart.resize();
        }
    });
});

