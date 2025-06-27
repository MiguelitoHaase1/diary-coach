# Dojo Session 1.2: Modern Python Project Architecture

**Context:** Setting up a professional Python project with modern tooling and TDD infrastructure for a multi-agent coaching system.

**Challenge:** Establishing a robust foundation that supports async operations, event-driven architecture, and comprehensive testing while following contemporary Python best practices.

**Concept:** Modern Python project structure combines packaging standards, dependency management, containerization, and test-driven development into a cohesive development workflow.

## Docker 101: Containerization Fundamentals

### What is Docker?
Docker is a containerization platform that packages applications and their dependencies into lightweight, portable containers. Think of it as a "shipping container" for software that runs consistently across different environments.

### Key Docker Concepts
- **Container:** A running instance of an image
- **Image:** A blueprint for creating containers (like a class vs instance)
- **Dockerfile:** Instructions for building an image
- **Docker Compose:** Tool for defining multi-container applications

### Essential Docker Commands
```bash
# Build an image
docker build -t my-app .

# Run a container
docker run -p 8080:80 my-app

# List running containers
docker ps

# Stop a container
docker stop <container-id>

# View logs
docker logs <container-id>
```

### Docker Compose Basics
```yaml
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

```bash
# Start all services
docker-compose up

# Start in background
docker-compose up -d

# Stop all services
docker-compose down
```

## Socratic Exploration

### Project Structure & Packaging
1. **Why did we choose `pyproject.toml` over `setup.py`?** 
   - What advantages does this newer standard provide?
   - How does it relate to PEP 517 and PEP 518?
   - What other configuration can be centralized in this file?

2. **What's the significance of the `src/` layout pattern?**
   - How does it prevent common import issues during development?
   - What problems does it solve compared to flat project structures?
   - Why is this particularly important for packages that will be installed?

### Virtual Environment Management
3. **Why did MacOS block our system-wide pip installation?**
   - What is PEP 668 and why was it implemented?
   - How do virtual environments solve the "dependency hell" problem?
   - What are the trade-offs between different virtual environment tools (venv, virtualenv, conda, poetry)?

### Test-Driven Development Philosophy
4. **What made our simple import test valuable despite its simplicity?**
   - How does starting with passing tests affect development psychology?
   - Why is immediate feedback crucial in TDD cycles?
   - What would happen if we had started coding before writing tests?

5. **How does TDD support the "incremental complexity" principle?**
   - Why is it better to have 10 simple tests than 1 complex test?
   - How do micro-tests help with debugging and maintenance?
   - What's the relationship between test granularity and confidence?

### Async-First Architecture Preparation
6. **Why did we include `pytest-asyncio` from the beginning?**
   - What challenges does testing async code present?
   - How will this support our future event-driven architecture?
   - What patterns will we need for testing async message passing?

### Docker & Containerization Strategy
7. **What role will Docker play in our development workflow?**
   - Why start with Redis in a container vs. local installation?
   - How does containerization support both development and production consistency?
   - What are the implications for testing strategies (unit vs integration)?

8. **How does Docker solve the "works on my machine" problem?**
   - What environment inconsistencies does containerization eliminate?
   - How do containers compare to virtual machines?
   - What are the security implications of containerized applications?

## Real-World Application

### Enterprise Development Patterns
This setup mirrors production-grade Python projects:
- **Configuration Management:** Single source of truth in `pyproject.toml`
- **Dependency Isolation:** Virtual environments prevent conflicts
- **Container Orchestration:** Docker Compose for service dependencies
- **Quality Gates:** Test-first development ensures robust code

### Scaling Considerations
The architecture decisions made here support:
- **Team Collaboration:** Consistent development environments
- **CI/CD Integration:** Standard testing and packaging workflows  
- **Service Architecture:** Event-driven design with Redis pub/sub
- **Monitoring & Observability:** Structured logging and async operations

### Learning Transfer Opportunities
1. **Apply this pattern to other Python projects** - Use this as a template
2. **Experiment with different testing frameworks** - Compare pytest vs unittest vs nose2
3. **Explore alternative dependency managers** - Try Poetry or Pipenv
4. **Practice Docker orchestration** - Add databases, message queues, or other services

## Deep Dive Challenges

### Beginner Level (Docker Focus)
- Create a simple Dockerfile for a Python application
- Use Docker volumes to persist Redis data
- Set up a different service in Docker Compose (PostgreSQL, MongoDB)
- Practice basic Docker commands and container lifecycle management

### Intermediate Level  
- Implement a more sophisticated test that verifies async functionality
- Create a pre-commit hook configuration for code quality
- Build a multi-stage Dockerfile for the Python application
- Set up Docker networking between multiple services

### Advanced Level
- Design a plugin architecture that can be tested with this framework
- Implement distributed testing across multiple containers
- Create a development workflow that automatically manages virtual environments
- Build a complete CI/CD pipeline using Docker containers

## Connection to Next Increment
The foundation we've built enables us to:
1. **Write async tests** for conversation quality metrics
2. **Mock external services** (Anthropic API) reliably  
3. **Test event publishing/subscribing** with Redis
4. **Validate data schemas** with Pydantic models

Each of these capabilities directly supports the multi-agent coaching system's architecture while maintaining the TDD discipline that ensures quality at every step.

## Reflection Questions for Your Learning Journal
1. What surprised you most about modern Python project setup?
2. How might you apply the "test-first, implement-minimally" pattern to other areas of development?
3. What questions do you have about async programming that we'll encounter in the next increment?
4. How does this project structure compare to other languages or frameworks you've used?
5. What are the main benefits you see from containerizing development dependencies like Redis?
6. How might Docker change your approach to setting up new development projects?