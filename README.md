# Finance Bro - AI Stock Analysis

🚀 **Natural language interface for Vietnamese stock market analysis** Interact with your financial statements in natural language. Get answers to your questions about any financial statement of listed stocks in Vietnam with a friendly finance bro. He's an introvert so please make your questions short and to the point. 

## Features

- 📊 **Vietnamese Stock Data** - Load financial data using Vnstock (VCI/TCBS sources)
- 🤖 **AI Chat Interface** - Natural language queries about financial metrics
- 💬 **Interactive Analysis** - Real-time conversation with AI analyst
- 📈 **Financial Metrics** - ROIC, debt ratios, dividend yields, cash flow analysis
- 🔐 **Secure API Key Management** - Environment variables or secure UI input

## Quick Start

### Prerequisites

- Python >= 3.10.11
- OpenAI API key

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

### Recommended Setup for Best Experience

**🌞 Light Mode Required**: This app is designed for optimal readability in light mode. Please enable light mode in Streamlit settings before use.

**How to enable light mode:**
1. Click the hamburger menu (☰) in the top-right corner
2. Select "Settings"
3. Under "Theme", choose "Light"
4. The app will immediately switch to light mode for better visibility

### Step-by-Step Usage

1. **Initial Setup:**
   - Enable light mode for optimal readability (see above)
   - Enter your OpenAI API key when prompted

2. **Configure Stock Settings:**
   - Enter Vietnamese stock symbol (e.g., "REE", "VIC", "HPG")
   - Select period (year/quarter)
   - Choose data source (VCI/TCBS)

3. **Load Data:**
   - Click "Analyze Stock" to fetch financial data
   - Wait for data to load (progress indicator will show)

4. **Chat with AI:**
   - Use the chat interface to ask questions about the stock
   - Try sample questions for quick insights
   - Ask follow-up questions for deeper analysis

5. **Explore Results:**
   - View financial data tables
   - Analyze AI-generated charts and insights
   - Use sample questions from the sidebar for inspiration

## Example Questions

- "What is the return on invested capital (ROIC) trend?"
- "Analyze the dividend yield and payout ratio trends"
- "What is the company's debt-to-equity ratio?"
- "Compare revenue growth across years"
- "What are the key financial strengths and weaknesses?"

## ⚠️ Critical: Package Compatibility

**IMPORTANT:** This project uses specific versions of pandas and pandasai that are carefully matched for compatibility. **DO NOT** upgrade these packages independently without testing.

### Why Version Compatibility Matters

- **pandasai v2.4.2** requires **pandas v1.5.3** (not v2.x)
- **pandasai v3.x** (beta) has breaking changes and schema issues
- Mismatched versions cause:
  - `TypeError: sequence item 0: expected str instance, tuple found`
  - `'DataFrame' object has no attribute 'schema'`
  - Agent initialization failures

### Tested Compatible Versions

✅ **WORKING COMBINATION:**
- `pandasai==2.4.2` (stable)
- `pandas>=1.5.3,<2.0.0` (compatible range)
- Built-in OpenAI LLM (no separate extension needed)

❌ **AVOID:**
- `pandasai>=3.0.0` (beta, unstable)
- `pandas>=2.0.0` (incompatible with pandasai 2.4.2)
- `pandasai-openai` extension (not needed in v2.4.2)

### If You Need to Upgrade

1. **Test in a separate environment first**
2. **Check pandasai release notes** for breaking changes
3. **Update both packages together**, not individually
4. **Run the app thoroughly** before deploying

## Technology Stack

- **Frontend:** Streamlit
- **AI Engine:** PandasAI v2.4.2 (stable)
- **Stock Data:** Vnstock v3.2.5
- **LLM:** OpenAI GPT models
- **Data Processing:** Pandas v1.5.3 (compatible with pandasai 2.4.2)

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
├── app.py              # Main Streamlit application
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
```bash
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_openai_api_key \
  -v $(pwd)/exports:/app/exports \
  -v $(pwd)/cache:/app/cache \
  ghcr.io/gahoccode/finance-bro:latest
```

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

- `pandasai==2.4.2` - AI-powered data analysis
- `pandas>=1.5.3,<2.0.0` - Data manipulation
- `vnstock==3.2.5` - Vietnamese stock data
- `openai>=1.61.0` - OpenAI API client
- `streamlit==1.37.1` - Web application framework
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
