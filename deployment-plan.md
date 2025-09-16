Local Build from Dev Branch

  Step 1: Ensure You're on Dev Branch

  # Check current branch
  git branch

  # Switch to dev branch if needed
  git checkout dev

  # Or switch to your specific dev branch name
  git checkout your-dev-branch-name

  Step 2: Set Up GitHub Token (if not already 
  done)

  # Export your GitHub token for pushing to 
  ghcr.io
  export GITHUB_TOKEN=ghp_your_token_here

  Step 3: Build and Push from Dev Branch

  # Build Docker image from dev branch and push to
   ghcr.io
  ./scripts/build-and-push.sh

  This will:
  - Extract version from pyproject.toml (currently
   0.2.33)
  - Build Docker image locally (~3 minutes)
  - Tag with both version and latest
  - Push to ghcr.io/gahoccode/finance-bro:0.2.33
  and ghcr.io/gahoccode/finance-bro:latest

  Step 4: Deploy to Render (Optional)

  # If you have Render credentials set up
  ./scripts/deploy-to-render.sh

  # Or run complete pipeline
  ./scripts/build-deploy.sh

  Benefits of Local Dev Branch Build

  - ⚡ Fast - 3 minutes vs 8 minutes on GitHub
  Actions
  - 🔧 Full Control - Build exactly what's in your
   dev branch
  - 🚀 Immediate - No waiting for CI/CD queues
  - 🧪 Testing - Perfect for development
  iterations

  Note on Tagging

  The local script will use your current version
  (0.2.33) and tag as latest. Your dev branch
  changes will overwrite the latest tag in
  ghcr.io, which is perfect for development
  testing.

  Go ahead and run ./scripts/build-and-push.sh
  from your dev branch! 🚀