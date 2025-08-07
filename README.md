# Finance Bro - AI Stock Analysis

🚀 **Natural language interface for Vietnamese stock market analysis** Interact with your financial statements in natural language. Get answers to your questions about any financial statement of listed stocks in Vietnam with a friendly finance bro. He's an introvert so please make your questions short and to the point. 

## Features

- 📊 **Vietnamese Stock Data** - Load financial data using Vnstock (VCI/TCBS sources)
- 🤖 **AI Chat Interface** - Natural language queries about financial metrics
- 💬 **Interactive Analysis** - Real-time conversation with AI analyst
- 📈 **Financial Metrics** - ROIC, debt ratios, dividend yields, cash flow analysis
- 🏢 **Company Analysis** - Ownership structure, management team, subsidiaries, and foreign transaction analysis
- 🔐 **Secure API Key Management** - Environment variables or secure UI input

## Quick Start

### Prerequisites

- Python >= 3.10.11
- OpenAI API key
- Google Cloud Console account (for OAuth setup)

### Google OAuth Setup (Required)

Before running the app, you need to set up Google OAuth authentication:

1. **Create Google OAuth Credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google+ API
   - Go to Credentials → Create Credentials → OAuth 2.0 Client IDs
   - Configure OAuth consent screen
   - Add authorized redirect URI: `http://localhost:8501/oauth2callback` or 'https://your-app-domain.com/oauth2callback' if you are deploying to production with a custom domain
   - Download credentials JSON file

2. **Configure authentication:**
   ```bash
   # Copy the example secrets file
   cp .streamlit/secrets.example.toml .streamlit/secrets.toml
   
   # Edit .streamlit/secrets.toml and add your Google OAuth credentials
   # Replace the placeholder values with your actual credentials
   ```

3. **Update secrets.toml with your credentials:**
   ```toml
   [auth]
   redirect_uri = "http://localhost:8501/oauth2callback"
   cookie_secret = "your-random-secret-string-here"
   client_id = "your-google-client-id.apps.googleusercontent.com"
   client_secret = "your-google-client-secret"
   server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
   ```

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/finance-bro.git
cd finance-bro
```

2. **Install dependencies using uv (recommended):**
```bash
uv sync
```

Or using pip:
```bash
pip install -r requirements.txt
```

3. **Set your OpenAI API key:**
```bash
export OPENAI_API_KEY="your-openai-api-key"
```

4. **Run the application:**
```bash
uv run streamlit run app.py
```

Or:
```bash
streamlit run app.py
```

5. **Open your browser** and navigate to `http://localhost:8501`

## User Flow

### Optimal User Experience Flow

**Finance Bro** is designed with a specific user flow for the best experience. Follow these steps to get the most out of the application:

### Step 1: Authentication & Homepage
1. **🔐 Google Login**: Start by logging in with your Google account on the authentication page
2. **🏠 Homepage Navigation**: After login, you'll be directed to the Finance Bro homepage
3. **📊 Stock Symbol Selection**: On the homepage, use the searchable dropdown to select a Vietnamese stock symbol
   - **Critical Step**: This stock symbol selection is essential - it will be shared across all analysis pages
   - **Search Feature**: Type to search through all available Vietnamese stock symbols
   - **Persistence**: Your selected symbol will be available throughout your session

### Step 2: Stock Analysis Page (Essential First Stop)
4. **📈 Navigate to Stock Analysis**: From the homepage, click the "📊 Stock Analysis" quick navigation button
   - **Why This Matters**: The Stock Analysis page loads and caches essential data for optimal performance
   - **Data Loading**: This page loads all stock symbols and company information for the entire app
   - **Performance**: Visiting this page first ensures faster loading on all other pages

5. **⚙️ Configure Analysis Settings**: In the Stock Analysis page:
   - Select period (year/quarter)
   - Choose data source (VCI/TCBS)
   - Click "Analyze Stock" to load financial data

6. **💬 AI Interaction**: Once data is loaded:
   - Use the chat interface to ask financial questions
   - Try sample questions from the sidebar
   - Explore AI-generated insights and charts

### Step 3: Explore Other Analysis Tools
7. **🚀 Navigate to Other Pages**: Now you can efficiently use other analysis tools:
   - **📈 Price Analysis**: Interactive price charts and technical analysis
   - **🏢 Company Overview**: Company profile with ownership structure, management team, subsidiaries, and foreign transaction analysis
   - **💼 Portfolio Optimization**: Modern Portfolio Theory-based optimization

### Recommended Setup for Best Experience

**🎨 Custom Theme for Best Appearance**: This app is designed with a custom color scheme for optimal visual experience.

**How to enable custom theme:**
1. Click the hamburger menu (☰) in the top-right corner
2. Select "Settings"
3. Under "Theme", choose "Custom"
4. The app will display with the optimized color scheme and chart styling

**Alternative**: Light mode is also supported if you prefer standard Streamlit styling.

### Why This Flow Matters

**🎯 Performance Optimization**: 
- Stock Analysis page loads and caches symbols data once for the entire session
- All other pages benefit from this cached data for faster loading
- Company names display properly across all pages

**📊 Data Consistency**: 
- Your selected stock symbol persists across all pages
- Financial data is loaded once and shared across analysis tools
- Seamless navigation between different analysis perspectives

**🚀 Best User Experience**:
- No need to re-enter stock symbols on each page
- Faster page loads after initial data caching
- Professional company name display instead of just stock symbols

## Example Questions

- "What is the return on invested capital (ROIC) trend?"
- "Analyze the dividend yield and payout ratio trends"
- "What is the company's debt-to-equity ratio?"
- "Compare revenue growth across years"
- "What are the key financial strengths and weaknesses?"

## ⚠️ Critical: Package Compatibility

**IMPORTANT:** This project uses specific versions of pandas and pandasai that are carefully matched for compatibility. **DO NOT** upgrade these packages independently without testing.

### Why Version Compatibility Matters

- **pandasai v2.3.0** requires **pandas v1.5.3** (not v2.x)
- **pandasai v3.x** (beta) has breaking changes and schema issues
- Mismatched versions cause:
  - `TypeError: sequence item 0: expected str instance, tuple found`
  - `'DataFrame' object has no attribute 'schema'`
  - Agent initialization failures

### Tested Compatible Versions

✅ **WORKING COMBINATION:**
- `pandasai==2.3.0` (stable)
- `pandas>=1.5.3,<2.0.0` (compatible range)
- Built-in OpenAI LLM (no separate extension needed)

❌ **AVOID:**
- `pandasai>=3.0.0` (beta, unstable)
- `pandas>=2.0.0` (incompatible with pandasai 2.3.0)
- `pandasai-openai` extension (not needed in v2.3.0)

### If You Need to Upgrade

1. **Test in a separate environment first**
2. **Check pandasai release notes** for breaking changes
3. **Update both packages together**, not individually
4. **Run the app thoroughly** before deploying

## Technology Stack

- **Frontend:** Streamlit
- **AI Engine:** PandasAI v2.3.0 (stable)
- **Stock Data:** Vnstock v3.2.5
- **LLM:** OpenAI GPT models
- **Data Processing:** Pandas v1.5.3 (compatible with pandasai 2.3.0)

## Future Refactor: PandasAI 3.x Migration

### Target Dependencies (PandasAI 3.x)
For future migration to PandasAI 3.x, the following dependencies will be required:

```toml
dependencies = [
    "numpy>=1.26.4",
    "pandasai>=3.0.0b2",
    "pandasai-openai>=0.1.6",
    "streamlit>=1.47.1",
    "vnstock>=3.2.6",
]
```

### Migration Considerations
- **Breaking Changes**: PandasAI 3.x has significant API changes from 2.x
- **Schema Changes**: New dataframe schema handling required
- **Extension System**: Separate pandasai-openai package needed
- **Testing Required**: Full regression testing needed before migration
- **Compatibility**: Verify vnstock integration with new pandas versions

## Project Structure

```
finance-bro/
├── app.py              # Main Streamlit application entry point
├── requirements.txt    # Python dependencies
├── pyproject.toml     # Project configuration
├── README.md          # Project documentation
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── .env.example       # Environment variables template
├── .dockerignore      # Docker ignore rules
└── .gitignore         # Git ignore rules
```

## Docker Deployment

### Using Pre-built Image from GitHub Container Registry

**Pull and run the latest image:**

**macOS/Linux:**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/cache:/app/cache \
  -v $(pwd)/.streamlit:/app/.streamlit \
  ghcr.io/gahoccode/finance-bro:latest
```

**Windows Command Prompt:**
```cmd
docker run -p 8501:8501 -e OPENAI_API_KEY=your_openai_api_key -v %cd%/exports:/app/exports -v %cd%/cache:/app/cache -v %cd%/.streamlit:/app/.streamlit ghcr.io/gahoccode/finance-bro:latest
```

**Windows PowerShell:**
```powershell
docker run -p 8501:8501 `
  -e OPENAI_API_KEY=your_openai_api_key `
  -v ${PWD}/exports:/app/exports `
  -v ${PWD}/cache:/app/cache `
  -v ${PWD}/.streamlit:/app/.streamlit `
  ghcr.io/gahoccode/finance-bro:latest
```

**Note:** The `$(pwd)`, `%cd%`, and `${PWD}` commands automatically get your current working directory. For example, if you're in `/home/user/finance-bro`, these resolve to that path.

**Or use with docker-compose:**
```yaml
services:
  finance-bro:
    image: ghcr.io/gahoccode/finance-bro:latest
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./exports:/app/exports
      - ./cache:/app/cache
    env_file:
      - .env
```

### Quick Start with Docker

#### Using Docker Compose (Recommended)

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/finance-bro.git
cd finance-bro
```

2. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. **Build and run with Docker Compose:**
```bash
docker-compose up --build
```

4. **Access the application:**
Open your browser and navigate to `http://localhost:8501`

#### Using Docker CLI

1. **Build the Docker image:**
```bash
docker build -t finance-bro .
```

2. **Run the container:**
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/cache:/app/cache \
  finance-bro
```

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Copy the template
cp .env.example .env

# Edit .env and add your OpenAI API key
# Required - Get from https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# Optional - Usually not needed for local development
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
LOG_LEVEL=INFO
```

**Important:** You must set your `OPENAI_API_KEY` in the `.env` file before running Docker. The application won't work without it.

### Docker Commands Reference

```bash
# Build the image
docker build -t finance-bro .

# Run in development mode
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Volume Mounting

The Docker setup includes volume mounting for:
- `./exports:/app/exports` - Persistent storage for generated charts and exports
- `./cache:/app/cache` - Persistent cache for faster data loading

### Production Considerations

For production deployment:

1. **Use a reverse proxy** (nginx, traefik) for SSL termination
2. **Set resource limits** in docker-compose.yml
3. **Use environment-specific configurations**
4. **Monitor container health** with the built-in health check

Example production docker-compose.yml additions:
```yaml
# Add to services.finance-bro in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 1G
      cpus: "1.0"
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
```

### Automated Publishing with GitHub Actions

This project includes automated Docker image publishing to GitHub Container Registry (GHCR) via GitHub Actions.

#### How It Works

- **On push to main/master**: Builds and publishes `latest` tag
- **On version tags** (e.g., `v1.0.0`): Builds and publishes versioned tags
- **On pull requests**: Builds image for testing (doesn't publish)
- **Multi-platform**: Builds for both `linux/amd64` and `linux/arm64`

#### Available Image Tags

- `ghcr.io/gahoccode/finance-bro:latest` - Latest stable version
- `ghcr.io/gahoccode/finance-bro:main` - Latest from main branch
- `ghcr.io/gahoccode/finance-bro:v1.0.0` - Specific version tags

#### Manual Publishing

To manually publish a new version:

```bash
# Create and push a version tag
git tag v1.0.0
git push origin v1.0.0

# GitHub Actions will automatically build and publish
```

#### Local Development vs Production

**For local development:**
```bash
# Build locally
docker-compose up --build
```

**For production deployment:**
```bash
# Use pre-built image
docker run -p 8501:8501 -e OPENAI_API_KEY=your_key ghcr.io/gahoccode/finance-bro:latest
```

## Dependencies

- `pandasai==2.3.0` - AI-powered data analysis
- `pandas>=1.5.3,<2.0.0` - Data manipulation
- `vnstock==3.2.5` - Vietnamese stock data
- `openai>=1.61.0` - OpenAI API client
- `streamlit==1.47.0` - Web application framework
- `python-dotenv==1.0.1` - Environment variable management

## Contributing

We welcome contributions! Here are ways you can help improve Finance Bro:

### Theme Contributions
**🎨 Custom Themes Wanted**: We're looking for contributors to help create custom themes for the app. If you have design skills and want to contribute:
- Create custom CSS themes (light/dark variants)
- Design responsive layouts
- Improve accessibility features
- Submit theme proposals via pull requests

### General Contributions
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Contribution Guidelines
- Follow PEP8 style guidelines
- Add appropriate documentation
- Test your changes thoroughly
- Include screenshots for UI changes
- Update README if adding new features

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Built with ❤️ using Streamlit, PandasAI, and Vnstock**
