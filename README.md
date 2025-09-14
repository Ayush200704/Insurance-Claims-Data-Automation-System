# Insurance Claims Data Automation System

A comprehensive data pipeline system for automating insurance claims processing, reserve calculation, and reporting using Python, FastAPI, SQLite, Pandas, Excel, and modern web technologies.

## 🚀 Features

- **Modern Web Interface**: Beautiful, responsive frontend with Bootstrap 5 and Chart.js
- **Real-time Dashboard**: Interactive charts and metrics with live data updates
- **Automated Data Pipeline**: Extract, clean, and transform large insurance claims datasets
- **Reserve Calculation**: Implement multiple actuarial methods (Chain Ladder, Bornhuetter-Ferguson, Frequency-Severity)
- **Trend Analysis**: Automated analysis of claims patterns and risk factors
- **Excel Report Generation**: Professional Excel dashboards with charts and multiple sheets
- **File Upload System**: Drag-and-drop CSV file upload with progress tracking
- **RESTful API**: Complete FastAPI backend with comprehensive endpoints
- **Error Handling**: Robust error handling and user feedback system
- **Docker Ready**: Containerized for easy deployment and scaling

## 📊 Dataset

The system processes insurance claims data with the following parameters:
- `age`: Age of the policyholder
- `sex`: Gender (0=female, 1=male)
- `bmi`: Body Mass Index
- `children`: Number of children
- `smoker`: Smoking status (0=no, 1=yes)
- `region`: Geographic region (0-3)
- `charges`: Insurance charges
- `insuranceclaim`: Claim status (0=no claim, 1=claim)

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Frontend  │───▶│   FastAPI       │───▶│  Data Pipeline  │
│   (HTML/CSS/JS) │    │   (Backend)     │    │  (ETL Process)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Excel Reports  │◀───│   SQLite DB     │◀───│  Reserve Calc   │
│  (Charts/Data)  │    │   (Data Store)  │    │  (Actuarial)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Trend Analysis │
                       │  (ML Models)    │
                       └─────────────────┘
```

## 🛠️ Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+), Bootstrap 5, Chart.js
- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, Pydantic
- **Data Processing**: Pandas, NumPy, Scikit-learn, SciPy
- **Database**: SQLite (with PostgreSQL support)
- **Visualization**: Chart.js, OpenPyXL charts
- **Excel Integration**: OpenPyXL, XlsxWriter
- **API Documentation**: FastAPI auto-generated docs
- **Error Handling**: Comprehensive error handling and user feedback
- **Containerization**: Docker, Docker Compose
- **Monitoring**: Loguru, Health Checks, CORS support

## 📦 Installation

### Prerequisites

- Python 3.10+
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Docker and Docker Compose (optional)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd insurance-claims-automation
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   # Method 1: Direct Python execution
   python app/main.py
   
   # Method 2: Using uvicorn
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   
   # Method 3: Using Docker
   docker-compose up
   ```

4. **Access the application**
   - **Web Interface**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Health Check**: http://localhost:8000/health

### Load Sample Data

The system comes with sample data pre-loaded, but you can also upload your own CSV files:

**Using the Web Interface:**
1. Open http://localhost:8000
2. Navigate to the "Upload" section
3. Drag and drop your CSV file or click "Browse Files"
4. The system will automatically process and load the data

**Using the API:**
```bash
# Upload your insurance claims CSV file
curl -X POST "http://localhost:8000/upload-data" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@insurance2.csv"
```

## 🚀 AWS Deployment

### Prerequisites

- AWS CLI configured
- ECR repository created
- ECS cluster set up
- RDS PostgreSQL instance
- Application Load Balancer

### Deploy to AWS

1. **Build and push Docker image**
   ```bash
   # Windows
   deploy.bat
   
   # Linux/Mac
   ./deploy.sh
   ```

2. **Manual deployment steps**
   ```bash
   # Build image
   docker build -t insurance-claims-automation .
   
   # Tag for ECR
   docker tag insurance-claims-automation:latest \
       YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/insurance-claims-automation:latest
   
   # Push to ECR
   docker push YOUR_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/insurance-claims-automation:latest
   
   # Update ECS service
   aws ecs update-service --cluster insurance-claims-cluster \
       --service insurance-claims-automation-service --force-new-deployment
   ```

## 🌐 Web Interface Features

### Dashboard
- **Real-time Metrics**: Total records, claim rates, average age, BMI, charges
- **Interactive Charts**: Claims by region, age groups, smoker impact, charges distribution
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Live Data Updates**: Automatic data refresh and error handling

### Reserve Calculations
- **Multiple Methods**: Chain Ladder, Bornhuetter-Ferguson, Frequency-Severity
- **One-click Calculation**: Calculate reserves with a single button click
- **Real-time Results**: Instant display of calculated reserves
- **Method Comparison**: Side-by-side comparison of different methods

### Trend Analysis
- **Automated Analysis**: Click to analyze trends in claims data
- **Visual Results**: Clear display of trend directions and strengths
- **Multiple Metrics**: Age, BMI, charges, and smoker rate trends

### File Upload
- **Drag & Drop**: Easy file upload with drag-and-drop interface
- **Progress Tracking**: Visual progress bar during file processing
- **Format Validation**: Automatic CSV format validation
- **Success Feedback**: Clear success/error messages

### Excel Reports
- **Professional Reports**: Multi-sheet Excel files with charts
- **One-click Generation**: Generate comprehensive reports instantly
- **Automatic Download**: Files download automatically when ready
- **Rich Visualizations**: Pie charts, bar charts, and data summaries

<img width="1919" height="992" alt="image" src="https://github.com/user-attachments/assets/8880bc25-063d-4387-8e8e-09ca18715e09" />
<img width="1919" height="988" alt="image" src="https://github.com/user-attachments/assets/3e551941-f169-4b27-ab11-49813a767cf5" />
<img width="1919" height="993" alt="image" src="https://github.com/user-attachments/assets/37c85ff8-3d47-4094-bb65-552d662102a4" />


## 📊 API Endpoints

### Core Endpoints
- `GET /` - Web interface homepage
- `GET /health` - Health check endpoint
- `POST /upload-data` - Upload new insurance data

### Data Management
- `GET /api/v1/data/summary` - Get data summary statistics
- `POST /api/v1/pipeline/process` - Process data pipeline
- `GET /api/v1/dashboard/data` - Get dashboard visualization data

### Reserve Calculations
- `POST /api/v1/reserves/calculate` - Calculate reserves (chain_ladder, bornhuetter_ferguson, frequency_severity)
- `GET /api/v1/reserves/summary` - Get reserve calculation summary

### Analytics & Reporting
- `POST /api/v1/trends/analyze` - Perform trend analysis
- `GET /api/v1/dashboard/excel` - Generate Excel dashboard
- `GET /api/v1/dashboard/download/{filename}` - Download Excel file

### Predictions
- `GET /api/v1/predictions/{record_id}` - Predict claim for specific record

## 📈 Reserve Calculation Methods

### 1. Chain Ladder Method
- Uses development triangles to project ultimate claims
- Calculates development factors from historical data
- Provides confidence intervals for reserve estimates

### 2. Bornhuetter-Ferguson Method
- Combines expected loss ratios with reported claims
- Uses development factors to estimate ultimate claims
- Balances between reported and expected claims

### 3. Frequency-Severity Method
- Separates claim frequency and severity analysis
- Calculates expected claims from exposure and rates
- Provides variance estimates for confidence intervals

## 📊 Excel Dashboard Features

### Multi-Sheet Reports
- **Executive Summary**: Key metrics, KPIs, and claims distribution pie chart
- **Data Analysis**: Detailed breakdowns by age groups, BMI categories, and regions with bar charts
- **Reserve Calculations**: Multiple actuarial methods with comparison bar chart
- **Trend Analysis**: Time-series analysis and risk factor patterns
- **Raw Data**: Complete dataset for further analysis

### Professional Visualizations
- **Pie Charts**: Claims distribution, BMI category analysis
- **Bar Charts**: Age group claims, reserve method comparisons
- **Data Tables**: Formatted tables with proper styling
- **Summary Statistics**: Comprehensive metrics and percentages
- **Auto-formatting**: Professional Excel formatting with colors and fonts

## 🔧 Configuration

### Default Settings
The system works out-of-the-box with sensible defaults:
- **Database**: SQLite (no configuration required)
- **Port**: 8000
- **CORS**: Enabled for all origins
- **Logging**: INFO level with structured logging

### Environment Variables (Optional)

```bash
# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./insurance_claims.db

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
BATCH_SIZE=1000
MAX_WORKERS=4

# Reserve Calculation
CONFIDENCE_LEVEL=0.95
DEVELOPMENT_PERIOD=12
TAIL_FACTOR=1.05

# AWS Configuration (for deployment)
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_DEFAULT_REGION=us-east-1
AWS_S3_BUCKET=your-bucket-name
```

## 📝 Usage Examples

### Web Interface Usage
1. **Open the Dashboard**: Navigate to http://localhost:8000
2. **View Metrics**: See real-time statistics and charts
3. **Calculate Reserves**: Click reserve calculation buttons
4. **Analyze Trends**: Click "Analyze Trends" button
5. **Upload Data**: Drag and drop CSV files
6. **Generate Reports**: Click "Generate Excel Report" button

### API Usage Examples

#### Get Data Summary
```python
import requests

# Get data summary
response = requests.get("http://localhost:8000/api/v1/data/summary")
print(response.json())
```

#### Calculate Reserves
```python
# Calculate reserves using Chain Ladder method
response = requests.post(
    "http://localhost:8000/api/v1/reserves/calculate",
    params={"method": "chain_ladder"}
)
print(response.json())
```

#### Generate Excel Dashboard
```python
# Generate Excel dashboard
response = requests.get("http://localhost:8000/api/v1/dashboard/excel")
result = response.json()
print(f"Excel file generated: {result['filename']}")
```

#### Upload Data
```python
# Upload CSV file
with open('insurance_data.csv', 'rb') as f:
    files = {'file': f}
    response = requests.post("http://localhost:8000/upload-data", files=files)
    print(response.json())
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/test_data_pipeline.py
```

## 📊 Monitoring and Logging

- **Health Checks**: `/health` endpoint for service monitoring
- **Structured Logging**: JSON-formatted logs with Loguru
- **Metrics**: Application performance and business metrics
- **Error Tracking**: Comprehensive error handling and reporting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for troubleshooting

## 🎯 Recent Improvements

### Frontend Enhancements
- ✅ **Modern Web Interface**: Beautiful, responsive design with Bootstrap 5
- ✅ **Interactive Charts**: Real-time charts using Chart.js
- ✅ **Drag & Drop Upload**: Easy file upload with progress tracking
- ✅ **Error Handling**: Comprehensive error messages and user feedback
- ✅ **Mobile Responsive**: Works perfectly on all device sizes

### Backend Improvements
- ✅ **FastAPI Integration**: Modern, fast API with automatic documentation
- ✅ **SQLite Database**: Lightweight, file-based database (no setup required)
- ✅ **CORS Support**: Proper cross-origin resource sharing
- ✅ **Health Checks**: Built-in health monitoring endpoints
- ✅ **Structured Logging**: Professional logging with Loguru

### Excel Report Features
- ✅ **Multi-Sheet Reports**: Executive Summary, Data Analysis, Reserve Calculations, Trend Analysis, Raw Data
- ✅ **Professional Charts**: Pie charts, bar charts with proper data references
- ✅ **Auto-formatting**: Professional Excel styling and formatting
- ✅ **One-click Generation**: Instant report generation and download

### User Experience
- ✅ **No Loading Screens**: Removed unnecessary processing modals
- ✅ **Instant Feedback**: Real-time updates and error messages
- ✅ **Fallback Data**: Sample data when backend is unavailable
- ✅ **Timeout Protection**: Automatic error handling for slow responses

## 🔮 Future Enhancements

- [ ] Real-time streaming data processing
- [ ] Advanced machine learning models
- [ ] User authentication and authorization
- [ ] Integration with external data sources
- [ ] Automated report scheduling
- [ ] Multi-tenant support
- [ ] Advanced security features
- [ ] Real-time notifications
- [ ] Data export in multiple formats (PDF, CSV)

---

**Built with ❤️ for Insurance Data Automation**

