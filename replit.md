# TradingView Webhook Service

## Overview

This is a Flask-based webhook service that bridges TradingView alerts with Telegram notifications. The application receives webhook calls from TradingView, processes trading alerts, and forwards them to configured Telegram channels. It includes a web dashboard for monitoring webhook activity, tracking message delivery status, and viewing historical logs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Flask**: Lightweight Python web framework chosen for rapid development and simplicity
- **SQLAlchemy**: ORM for database operations with declarative base model structure
- **Modular Design**: Application split into logical modules (app, models, routes, telegram_service) for maintainability

### Database Design
- **SQLite**: Default database for development with configurable DATABASE_URL for production deployments
- **Two-table schema**:
  - `WebhookLog`: Main table tracking webhook events, sources, content, and delivery status
  - `TelegramMessage`: Child table for tracking specific Telegram message details and retry attempts
- **Connection pooling**: Configured with pool recycling and pre-ping for reliability

### Web Interface
- **Bootstrap 5**: Dark theme UI framework for responsive dashboard
- **Template inheritance**: Base template with consistent navigation and styling
- **Real-time statistics**: Dashboard showing webhook counts, success rates, and recent activity
- **Logging interface**: Dedicated page for viewing all webhook history

### External Service Integration
- **Telegram Bot API**: Direct HTTP requests to Telegram's REST API for message delivery
- **Environment-based configuration**: Bot tokens and channel IDs managed via environment variables
- **Error handling**: Comprehensive error tracking and retry mechanisms

### Request Processing
- **Webhook endpoint**: `/webhook/tradingview` accepts POST requests with JSON payloads
- **Logging system**: Python's built-in logging with DEBUG level for development
- **Proxy handling**: ProxyFix middleware for deployment behind reverse proxies

### Security Considerations
- **Session management**: Secret key configuration for Flask sessions
- **Input validation**: JSON payload processing with error handling
- **Environment isolation**: Sensitive credentials managed through environment variables

## External Dependencies

### Core Python Packages
- **Flask**: Web framework and request handling
- **Flask-SQLAlchemy**: Database ORM integration
- **Werkzeug**: WSGI utilities and middleware
- **Requests**: HTTP client for Telegram API calls

### External APIs
- **Telegram Bot API**: Primary integration for message delivery
- **TradingView Webhooks**: Incoming webhook source for trading alerts

### Frontend Libraries (CDN)
- **Bootstrap 5**: UI framework with dark theme support
- **Font Awesome 6**: Icon library for dashboard interface

### Database
- **SQLite**: Default local database (configurable to PostgreSQL or other SQL databases via DATABASE_URL)

### Runtime Environment
- **Python 3.x**: Required runtime environment
- **Environment Variables**: 
  - `TELEGRAM_BOT_TOKEN`: Bot authentication token
  - `TELEGRAM_CHANNEL_ID`: Target channel for notifications
  - `DATABASE_URL`: Database connection string
  - `SESSION_SECRET`: Flask session encryption key