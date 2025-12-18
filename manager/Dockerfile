# ============================================================================
# Multi-stage Dockerfile for Spring Boot Application
# ============================================================================

# ============================================================================
# Stage 1: Build Stage
# ============================================================================
FROM maven:3.9-eclipse-temurin-17-alpine AS builder

WORKDIR /build

# Copy Maven files for dependency caching
COPY pom.xml .
COPY .mvn .mvn
COPY mvnw .

# Download dependencies (cached layer if pom.xml unchanged)
RUN ./mvnw dependency:go-offline -B

# Copy source code
COPY src ./src

# Build application (skip tests for faster build)
RUN ./mvnw clean package -DskipTests -B

# ============================================================================
# Stage 2: Runtime Stage
# ============================================================================
FROM eclipse-temurin:17-jre-alpine

# Install Python and required packages
RUN apk add --no-cache \
    python3 \
    py3-pip \
    curl \
    && ln -sf python3 /usr/bin/python

# Create app user for security
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy built JAR from builder stage
COPY --from=builder /build/target/*.jar app.jar

# Create directories
RUN mkdir -p /app/logs /app/mcdm

# # Install Python dependencies
# COPY requirements.txt /tmp/
# RUN pip3 install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Change ownership
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8080/api/analysis/health || exit 1

# JVM configuration for optimal performance
ENV JAVA_OPTS="-Xms512m -Xmx1024m -XX:+UseG1GC -XX:MaxGCPauseMillis=200"

# Run application
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]
