# Thickness Uniformity Analysis App

A comprehensive web application for analyzing thickness uniformity in manufacturing processes, built with Streamlit. This app provides detailed analysis of Pre-OL and Post-OL measurements with advanced scoring algorithms.

## 🚀 **Live Demo**

**Access the app here**: [Your Deployed App URL]

## ✨ **Features**

### 📊 **Analysis Capabilities**
- **Pre-OL Analysis**: Analyze thickness uniformity before OL processing
- **Post-OL Analysis**: Analyze thickness uniformity after OL processing  
- **TUS (Targeted Uniformity Score)**: Measures proximity to target thickness and uniformity
- **RUS (Relative Uniformity Score)**: Measures intrinsic uniformity regardless of target

### 🔍 **Advanced Filtering & Search**
- Search by sensor ID
- Filter by score ranges (TUS/RUS)
- Filter by thickness ranges
- Sort by any metric
- Color-coded results

### 📈 **Visualizations**
- Score distribution charts
- Thickness profile plots grouped by performance
- Interactive plots with zoom and pan
- Export plots as PNG/SVG

### 📥 **Export Options**
- Download analysis results as CSV
- Export individual plots
- Generate comprehensive HTML reports
- Filtered data export

## 🛠️ **Usage**

### 1. **Data Upload**
- Upload CSV files with required columns:
  - `sensor_id`: Unique identifier for each sensor
  - `position_mm`: Position along measurement axis (mm)
  - `thickness_mm`: Measured thickness (for Post-OL data)
  - `condition`: Either 'Pre' or 'Post'
  - `measurement_mm`: Thickness measurement (for Pre-OL data)

### 2. **Configure Analysis**
- Set target mean thickness for Pre-OL analysis (default: 120.0 μm)
- Set target mean thickness for Post-OL analysis (default: 17.5 μm)

### 3. **Explore Results**
- View dashboard with summary metrics
- Analyze score distributions
- Examine individual sensor profiles
- Filter and search through data
- Export results and visualizations

## 📋 **Data Requirements**

### **CSV Format**
```csv
sensor_id,position_mm,thickness_mm,condition,measurement_mm
S001,0.1,15.2,Post,
S001,0.2,15.5,Post,
S001,0.3,15.1,Post,
S001,0.1,,Pre,118.5
S001,0.2,,Pre,119.2
S001,0.3,,Pre,118.8
```

### **Column Specifications**
- **sensor_id**: String identifier for each sensor
- **position_mm**: Numeric, measurement position (0.0-1.0 recommended)
- **thickness_mm**: Numeric, thickness for Post-OL data
- **condition**: String, either 'Pre' or 'Post'
- **measurement_mm**: Numeric, thickness for Pre-OL data

## 🏗️ **Installation & Local Development**

### **Prerequisites**
- Python 3.8+
- pip package manager

### **Setup**
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/thickness-uniformity-app.git
cd thickness-uniformity-app

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### **Dependencies**
- streamlit>=1.28.0
- pandas>=1.5.0
- numpy>=1.24.0
- plotly>=5.15.0
- scikit-learn>=1.3.0
- kaleido
- openpyxl>=3.1.0
- streamlit-option-menu

## 📊 **Scoring Algorithms**

### **TUS (Targeted Uniformity Score)**
Evaluates both proximity to target thickness and uniformity:
- **Mean Penalty**: Gaussian penalty for deviation from target
- **Smoothness Penalty**: Rewards lower standard deviation
- **Range Penalty**: Penalizes large thickness variations
- **Straightness Score**: R² from linear regression
- **Symmetry Bonus**: Rewards symmetric profiles

### **RUS (Relative Uniformity Score)**
Focuses purely on uniformity characteristics:
- **Smoothness**: Based on standard deviation
- **Range**: Normalized thickness range
- **Straightness**: Linear regression R²
- **Symmetry**: Left-right balance

## 🚀 **Deployment**

### **Streamlit Community Cloud**
1. Push code to GitHub (public repository)
2. Go to https://share.streamlit.io/
3. Connect your GitHub repository
4. Deploy with `app.py` as main file

### **Other Platforms**
- **Render**: Use provided `requirements.txt`
- **Heroku**: Use provided `Procfile`
- **Docker**: Create dockerfile based on Python 3.8+ image

## 📝 **Configuration**

The app includes a `.streamlit/config.toml` file with optimized settings:
- Maximum upload size: 200MB
- Custom theme colors
- Disabled CORS for better performance
- Privacy-focused settings

## 🤝 **Contributing**

Contributions are welcome! Please feel free to submit issues and enhancement requests.

## 📄 **License**

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 **Support**

For questions or support, please open an issue in the GitHub repository.

---

**Built with ❤️ using Streamlit** 