# Bee Productivity Analyzer

A real-time bee productivity and foraging analysis system using AI to help beekeepers optimize their hive management.

## Features

- **Text-Based Analysis**: Query the system about bee productivity and receive AI-powered responses
- **Media Analysis**: Upload images or videos of beehives for instant analysis
- **Real-Time Processing**: Get immediate feedback and analysis results
- **Data Visualization**: View trends and patterns through interactive charts
- **Historical Analysis**: Track changes and patterns over time
- **Camera Integration**: Capture and analyze hive conditions in real-time

## Prerequisites

- Python 3.8 or higher
- Node.js 14.x or higher
- pip (Python package manager)
- npm (Node.js package manager)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/bee-productivity-analyzer.git
   cd bee-productivity-analyzer
   ```

2. **Create and Activate Virtual Environment**

   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**

   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Install Node.js dependencies
   npm install
   ```

4. **Configure Environment Variables**

   Create a `.env` file in the root directory with the following content:

   ```env
   GEMINI_API_KEY=your_gemini_api_key
   SECRET_KEY=your_secret_key
   DEBUG=True
   PORT=8080
   ```

   Replace `your_gemini_api_key` with your actual Gemini API key.

## Running the Application

1. **Start the Flask Server**

   ```bash
   python app/main.py
   ```

2. **Access the Application**
   - Open your web browser
   - Navigate to `http://localhost:8080`

## Usage Guide

### Chat Interface

- Use the chat interface to ask questions about bee productivity
- Get real-time responses based on the latest research and data

### Media Analysis

1. Click the "Analyze" tab
2. Choose one of the following options:
   - Upload an existing image/video
   - Take a new photo using your device camera
   - Record a video of your hive
3. Click "Analyze" to process the media
4. View detailed analysis results including:
   - Bee activity levels
   - Foraging patterns
   - Environmental conditions
   - Recommendations

### Data Visualization

- View historical trends
- Track productivity metrics
- Monitor environmental impacts
- Analyze seasonal patterns

## Testing

To test the main features:

1. **Chat Testing**
   - Ask about optimal hive conditions
   - Query about foraging patterns
   - Request productivity improvement tips

2. **Media Analysis Testing**
   - Upload sample hive images
   - Test camera integration
   - Analyze video footage

3. **Data Visualization Testing**
   - Check historical data display
   - Verify trend analysis
   - Test interactive features

## Troubleshooting

Common issues and solutions:

1. **Connection Issues**
   - Verify the server is running
   - Check port availability
   - Confirm network connectivity

2. **Analysis Errors**
   - Ensure media files are supported formats
   - Check file size limits
   - Verify API key configuration

3. **Visualization Problems**
   - Clear browser cache
   - Update browser to latest version
   - Check console for JavaScript errors

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

Your Name - <your.email@example.com>
Project Link: <https://github.com/yourusername/bee-productivity-analyzer>
