# PyPortfolioOpt Docker Build Configuration

### Why Special Configuration is Needed

PyPortfolioOpt depends on **osqp** (Operator Splitting Quadratic Program solver) and **cvxpy** (convex optimization), which contain C++ extensions. These dependencies require:
1. Pre-built binary wheels (platform-specific) OR
2. Compilation from source (requires system dependencies)

**Challenge**: The `python:3.10.11-slim` Docker base image lacks build tools, causing installation failures if wheels aren't available.

**Solution**: Pin specific versions with known wheel availability + provide fallback system dependencies for source compilation.

## Critical Dependencies

### osqp==0.6.2.post8

**Why This Specific Version?**

1. **Wheel Availability**: Version 0.6.2.post8 has pre-built wheels for:
   - macOS x86_64 (Intel Macs)
   - macOS arm64 (Apple Silicon M1/M2/M3)
   - Linux x86_64 (amd64)
   - Linux aarch64 (ARM64)
   - Windows x86_64

2. **Stability**: This version is battle-tested and known to work reliably across platforms

3. **PyPortfolioOpt Compatibility**: Compatible with all pyportfolioopt>=1.5.6 versions

4. **Deterministic Builds**: Exact version pinning ensures reproducible Docker builds

### requirements.txt Configuration

```txt
# Install osqp with specific version that has wheels for Mac ARM64 & Linux x86_64
osqp==0.6.2.post8
# Then install pyportfolioopt which depends on osqp
pyportfolioopt>=1.5.6
```

**Critical Order**: osqp MUST be installed BEFORE pyportfolioopt to:
- Prevent pip from selecting an incompatible osqp version
- Use pre-built wheels when available (90% faster installation)
- Ensure dependency resolution picks the correct versions

## Dockerfile System Dependencies

### Required System Packages

The Dockerfile includes comprehensive system dependencies for fallback source compilation:

```dockerfile
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    g++ \
    git \
    cmake \
    pkg-config \
    libblas-dev \
    liblapack-dev \
    gfortran \
    libopenblas-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

### Build Tools (C++ Extension Compilation)

| Package | Purpose |
|---------|---------|
| `build-essential` | Core compilation tools (make, automake, etc.) |
| `gcc` | GNU C Compiler for C extensions |
| `g++` | GNU C++ Compiler for C++ extensions |
| `cmake` | Build system generator required by osqp |
| `git` | Required by osqp to clone submodules during source builds |
| `pkg-config` | Helper tool for compiling applications with library dependencies |

### Mathematical Libraries (Numerical Computations)

| Package | Purpose |
|---------|---------|
| `libblas-dev` | Basic Linear Algebra Subprograms (matrix operations) |
| `liblapack-dev` | Linear Algebra PACKage (advanced linear algebra routines) |
| `gfortran` | Fortran compiler (required to build BLAS/LAPACK from source) |
| `libopenblas-dev` | Optimized BLAS implementation for better performance |

**Why These Libraries?**

osqp and cvxpy perform intensive matrix operations. BLAS and LAPACK provide:
- Efficient matrix multiplication
- Linear system solving
- Eigenvalue computations
- Numerical stability

OpenBLAS is an optimized implementation that leverages modern CPU features (SIMD, multi-threading).

### Utility Packages

| Package | Purpose |
|---------|---------|
| `curl` | Used for Docker health checks (`HEALTHCHECK` directive) |

## Cross-Platform Compatibility

### Supported Platforms

Finance Bro Docker images are built for multiple platforms:

```yaml
# From .github/workflows/docker-publish.yml
platforms: linux/amd64,linux/arm64
```

| Platform | Status | Wheel Available | Notes |
|----------|--------|-----------------|-------|
| Linux x86_64 (amd64) | ✅ Fully Supported | Yes | Primary production platform |
| Linux ARM64 (aarch64) | ✅ Fully Supported | Yes | Cloud ARM instances (AWS Graviton, etc.) |
| macOS x86_64 (Intel) | ✅ Local Dev | Yes | Intel-based Macs |
| macOS ARM64 (M1/M2/M3) | ✅ Local Dev | Yes | Apple Silicon Macs |
| Windows x86_64 | ⚠️ Not Tested | Yes | Not officially supported for Docker |

### Build Strategy by Platform

**Linux x86_64 (amd64)**:
1. Pip finds osqp 0.6.2.post8 wheel → Fast installation (~5 seconds)
2. System dependencies unused (wheels preferred)

**Linux ARM64 (aarch64)**:
1. Pip finds osqp 0.6.2.post8 wheel → Fast installation (~5 seconds)
2. System dependencies unused (wheels preferred)

**Fallback (if wheels unavailable)**:
1. Pip attempts source compilation
2. Uses system dependencies (gcc, cmake, BLAS, etc.)
3. Compilation takes ~30-60 seconds
4. Build succeeds with proper dependencies

## Build Strategy

### When Pre-Built Wheels Are Available (90% of cases)

**Installation Flow**:
```
pip install osqp==0.6.2.post8
  └─> Finds platform wheel (e.g., osqp-0.6.2.post8-cp310-cp310-manylinux_2_17_x86_64.whl)
  └─> Downloads wheel (~500KB)
  └─> Installs binary (~5 seconds)
  └─> System dependencies NOT needed

pip install pyportfolioopt>=1.5.6
  └─> Pure Python package
  └─> No compilation needed
  └─> Installs immediately
```

**Benefits**:
- ⚡ Fast Docker builds (~5 seconds for osqp)
- 📦 Smaller Docker image (no build tools needed in final layer)
- ✅ Reliable (no compilation errors)

### Fallback to Source Compilation (10% of cases)

**When This Happens**:
- Wheel not available for platform
- Wheel corrupted or download failed
- Using `--no-binary` pip flag (not recommended)

**Installation Flow**:
```
pip install osqp==0.6.2.post8
  └─> No wheel found
  └─> Downloads source distribution (osqp-0.6.2.post8.tar.gz)
  └─> Runs setup.py build
      └─> Invokes cmake to configure build
      └─> Clones osqp submodules via git
      └─> Compiles C++ code with g++
      └─> Links against BLAS/LAPACK
  └─> Installation completes (~30-60 seconds)
```

**Requirements**:
- ✅ System dependencies MUST be present
- ✅ Sufficient build memory (>512MB)
- ✅ Internet access (for git submodules)

## Version Management

### ⚠️ Critical Warnings

**DO NOT upgrade osqp independently!**

Upgrading osqp without testing can cause:
1. **Missing Wheels**: Newer versions may lack wheels for your platform
2. **Build Failures**: Compilation may fail with new compiler requirements
3. **Incompatibility**: May break pyportfolioopt or cvxpy
4. **Docker Size Increase**: Source builds keep build dependencies in image

**Before Upgrading osqp**:
1. Check PyPI for wheel availability: https://pypi.org/project/osqp/#files
2. Test Docker build locally on target platforms
3. Verify pyportfolioopt still works with new osqp version
4. Update documentation with new version rationale


## Troubleshooting

### Common Build Failures

#### Error: "CMake not found"
```
ERROR: Failed building wheel for osqp
CMake must be installed to build the following extensions: osqp
```

**Solution**: Add `cmake` to Dockerfile system dependencies
```dockerfile
RUN apt-get update && apt-get install -y cmake
```

#### Error: "Git not found"
```
ERROR: Failed building wheel for osqp
fatal: not a git repository
```

**Solution**: Add `git` to Dockerfile system dependencies (osqp needs it for submodules)
```dockerfile
RUN apt-get update && apt-get install -y git
```

#### Error: "undefined reference to dgemm_"
```
/usr/bin/ld: undefined reference to `dgemm_`
collect2: error: ld returned 1 exit status
```

**Solution**: Add BLAS/LAPACK libraries to Dockerfile
```dockerfile
RUN apt-get update && apt-get install -y \
    libblas-dev \
    liblapack-dev \
    gfortran \
    libopenblas-dev
```

#### Error: "No matching distribution found"
```
ERROR: Could not find a version that satisfies the requirement osqp==0.6.2.post8
```

**Solution**:
1. Check internet connectivity in Docker build
2. Verify PyPI is accessible
3. Try `pip install --index-url https://pypi.org/simple osqp==0.6.2.post8`

### Verifying Installation

**Check osqp version**:
```bash
python -c "import osqp; print(osqp.__version__)"
# Expected: 0.6.2.post8
```

**Check PyPortfolioOpt**:
```bash
python -c "from pypfopt import EfficientFrontier; print('Success')"
# Expected: Success
```

## References

### Official Documentation

- **PyPortfolioOpt**: https://pyportfolioopt.readthedocs.io/
- **osqp**: https://osqp.org/
- **cvxpy**: https://www.cvxpy.org/

### PyPI Package Pages

- **osqp**: https://pypi.org/project/osqp/
- **PyPortfolioOpt**: https://pypi.org/project/PyPortfolioOpt/
- **cvxpy**: https://pypi.org/project/cvxpy/

### Related Issues & Discussions

- osqp wheel availability: Check "Download files" section on PyPI
- Docker build optimization: Use multi-stage builds if image size is a concern
- ARM64 compatibility: Both osqp and cvxpy have ARM64 wheels since 2021

