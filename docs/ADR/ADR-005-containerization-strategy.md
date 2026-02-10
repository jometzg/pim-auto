# ADR-005: Containerization Strategy

**Status**: Proposed  
**Date**: 2026-02-10  
**Decision Makers**: Modernization Agent (pending human approval)

## Context

The PIM Auto application needs a deployment model that provides:
- Consistency across development, staging, and production environments
- Portability between different hosting platforms
- Isolation from host system dependencies
- Efficient resource utilization
- Operational simplicity

The application is specified to run in two modes (interactive CLI and batch processing), which influences deployment choices.

## Decision

Adopt **container-based deployment using Docker** with the following strategy:

### Container Specification

1. **Base Image**: `python:3.11-slim`
   - Official Python image with security maintenance
   - Slim variant for smaller image size
   - Contains only essential runtime dependencies

2. **Single Container for Both Modes**:
   - Same container image supports interactive and batch modes
   - Mode selection via command-line flag (`--mode batch`)
   - Reduces maintenance burden (only one artifact to build/test/deploy)

3. **Deployment Targets** (phased approach):
   - **Development**: Docker locally or Azure Container Instances (ACI)
   - **Production**: Azure Container Apps (ACA) - recommended
   - **Alternative**: Azure Kubernetes Service (AKS) - only if organization already operates AKS

### Container Configuration

- **Non-root user**: Container runs as UID 1000 (security best practice)
- **Configuration**: Environment variables (12-factor app pattern)
- **Secrets**: Azure managed identity (no secrets in container)
- **Health checks**: HTTP endpoint `/health` for liveness probes
- **Logging**: Stdout/stderr (captured by container platform)

### Image Build and Distribution

- **Build**: GitHub Actions CI/CD pipeline
- **Registry**: Azure Container Registry (ACR)
- **Tagging**: Semantic versioning + Git SHA for traceability
- **Scanning**: Automated vulnerability scanning before deployment

## Rationale

### Advantages

1. **Environment Consistency**:
   - "Works on my machine" problems eliminated
   - Identical runtime across dev, staging, production
   - Predictable behavior regardless of host OS

2. **Portability**:
   - Can run on any container platform (Docker, ACI, ACA, AKS)
   - Not locked into specific hosting provider (within Azure ecosystem)
   - Easy to replicate across multiple Azure regions

3. **Operational Simplicity**:
   - Single artifact (container image) to manage
   - Versioned and immutable deployments
   - Simple rollback (redeploy previous image tag)

4. **Security**:
   - Isolated from host system
   - Non-root user execution
   - Minimal attack surface (slim base image)
   - Automated vulnerability scanning

5. **Resource Efficiency**:
   - Fast startup times (Python app, not complex runtime)
   - Efficient scaling (especially with ACA)
   - Pay-per-use pricing models available

6. **Development Experience**:
   - Easy local testing (`docker run`)
   - Consistent with modern DevOps practices
   - Good tooling support (Docker, Kubernetes, Azure)

### Trade-offs

1. **Additional Complexity**:
   - Developers need Docker knowledge
   - Dockerfile and `.dockerignore` to maintain
   - Container image size considerations

2. **Build Time**:
   - Container builds add ~1-2 minutes to CI/CD pipeline
   - Mitigated by layer caching and optimized Dockerfile

3. **Debugging Challenges**:
   - Debugging inside containers slightly harder than native
   - Mitigated by good logging and local Docker development

4. **Startup Overhead**:
   - Small overhead to start container vs. native process
   - Negligible for this application (~2-3 seconds)

## Consequences

### Positive

- Consistent deployment model across all environments
- Easy to test locally (exact production environment)
- Azure Container Apps provides excellent fit:
  - Built-in HTTPS ingress (for future web UI)
  - Managed scaling (including scale-to-zero for cost savings)
  - Native Azure Monitor integration
  - Dapr support (if service extraction happens in future)
  - Job scheduling for batch mode

### Negative

- All developers must install and understand Docker
- Container image must be built and pushed for each deployment
- Adds infrastructure complexity (container registry, hosting platform)

### Neutral

- Container platform choice (ACI vs ACA vs AKS) can evolve
- Image size optimization is ongoing concern (but manageable)

## Implementation Details

### Dockerfile Structure

```dockerfile
# Base image with Python 3.11
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
# (separate layer for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "print('alive')" || exit 1

# Default to interactive mode (can be overridden)
CMD ["python", "-m", "src.pim_auto.main"]
```

### Container Platform Comparison

| Feature | ACI | ACA | AKS |
|---------|-----|-----|-----|
| **Complexity** | Low | Medium | High |
| **Cost (low volume)** | Low | Low | Medium-High |
| **Scaling** | Manual | Automatic | Automatic |
| **HTTPS Ingress** | No | Yes | Yes (requires ingress controller) |
| **Batch Jobs** | Manual trigger | Native support | Native (CronJobs) |
| **Monitoring** | Basic | Azure Monitor | Full observability |
| **Recommended For** | Dev/test | Production | Multi-service architectures |

**Recommendation**: Start with ACI for simplicity, migrate to ACA when ready for production.

## Alternatives Considered

### Alternative 1: Native Python Deployment (No Containers)

Deploy Python application directly to Azure App Service or VM.

**Rejected because**:
- Environment inconsistency (Python version, OS dependencies)
- Harder to replicate across environments
- Does not support CLI interactive mode well
- No clear deployment model for batch mode
- Misses modern DevOps best practices

### Alternative 2: Function-as-a-Service (Azure Functions)

Use Azure Functions for batch mode, separate solution for interactive mode.

**Rejected because**:
- Splits application into two deployment models
- Azure Functions not suitable for long-running interactive sessions
- Dual-mode operation (ADR-004) requires unified deployment
- State management (conversation context) doesn't fit serverless model

### Alternative 3: Virtual Machine Deployment

Deploy to Azure VM with Python installed.

**Rejected because**:
- Operational overhead (OS patching, security, scaling)
- Manual environment setup (not repeatable)
- Higher cost than container platforms
- Does not align with cloud-native best practices

## Alignment with Existing ADRs

- **ADR-001 (Agent-Based Governance)**: Containerization supports automated CI/CD agents
- **ADR-002 (Specification-First)**: Container approach implements specified dual-mode operation
- **ADR-003 (Azure-Native)**: Container deployment on Azure platforms maintains Azure integration
- **ADR-004 (Dual-Mode Operation)**: Single container supports both modes via configuration

## Migration Impact

### Slice 0 (Foundation)

- Create Dockerfile and `.dockerignore`
- Update CI/CD pipeline to build container images
- Document Docker setup in Developer Guide
- Test local container execution

### Slice 1-2 (Implementation)

- Validate application works correctly in container
- Test both interactive and batch modes in containerized environment
- No significant changes needed (application is container-agnostic)

### Slice 3 (Production Readiness)

- Deploy container to Azure Container Apps
- Configure container registry (ACR)
- Set up image scanning and security policies
- Document deployment procedures

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Container image too large | Multi-stage builds, slim base image, minimal dependencies |
| Slow container builds | Layer caching, optimized Dockerfile order, CI/CD caching |
| Security vulnerabilities in base image | Automated scanning, regular base image updates |
| Developers unfamiliar with Docker | Documentation, training, simple Dockerfile design |
| Container platform issues | Use managed Azure services (ACA), comprehensive monitoring |

## Success Criteria

This ADR is successfully implemented when:

✅ Dockerfile builds successfully  
✅ Container image runs both interactive and batch modes  
✅ Container passes security scans  
✅ CI/CD pipeline builds and pushes images automatically  
✅ Developers can run application locally via Docker  
✅ Application deploys to Azure container platform successfully  

## References

- `/docs/Target-Architecture.md`: Container deployment model section
- `/docs/Migration-Plan.md`: Slice 0 and Slice 3 implementation details
- [Docker Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Azure Container Apps Documentation](https://learn.microsoft.com/en-us/azure/container-apps/)
- [Azure Container Instances Documentation](https://learn.microsoft.com/en-us/azure/container-instances/)

## Review and Approval

- **Proposed by**: Modernization Agent
- **Review Status**: Pending human review
- **Approval Date**: TBD
- **Implementation Status**: Not yet started (will begin in Slice 0)
