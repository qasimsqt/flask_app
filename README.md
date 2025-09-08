# 🛒 Mini Shop - Flask E-commerce with AI Monitoring

A modern e-commerce application built with Flask, featuring real-time AI-powered anomaly detection for transaction monitoring and fraud prevention.

## 🌟 Features

- **Modern E-commerce Interface**: Clean, responsive design with product catalog and shopping cart
- **AI-Powered Security**: Real-time anomaly detection using machine learning
- **Transaction Monitoring**: Comprehensive logging and analysis of all user activities
- **Kubernetes Ready**: Production-ready containerization and orchestration
- **Real-time Dashboard**: Live monitoring interface for security teams
- **Scalable Architecture**: Microservices design with horizontal scaling support

## 🏗️ Architecture

The application consists of three main components:

1. **Flask Web App** (`app.py`) - Main e-commerce interface
2. **Log Generator** (`log_generator.py`) - Simulates realistic transaction data
3. **AI Monitor** (`log_ai_monitor.py`) - Real-time anomaly detection engine

## 🚀 Quick Start

### Local Development

```bash
# Clone and setup
git clone <repository>
cd mini-shop

# Run locally
chmod +x scripts/local-run.sh
./scripts/local-run.sh
```

### Docker Deployment

```bash
# Build image
chmod +x scripts/build.sh
./scripts/build.sh

# Run with Docker Compose
docker-compose up -d
```

### Kubernetes Deployment

```bash
# Deploy to Kubernetes
chmod +x scripts/deploy.sh
./scripts/deploy.sh

# With ingress (optional)
./scripts/deploy.sh --with-ingress
```

## 📊 Monitoring & AI Features

### Anomaly Detection

The AI system automatically detects:
- **Unusual Transaction Amounts**: Extremely high or low values
- **Security Threats**: SQL injection attempts, unauthorized access
- **Fraud Patterns**: Suspicious payment behaviors
- **System Anomalies**: Unusual application behavior

### Real-time Dashboard

Access the monitoring dashboard at `http://localhost:9000` to view:
- Live transaction logs
- Anomaly alerts and classifications
- System statistics and health metrics
- ML model training status

## 🛠️ Technology Stack

- **Backend**: Flask, Python 3.11
- **AI/ML**: scikit-learn, pandas, numpy
- **Frontend**: HTML5, CSS3, JavaScript, jQuery
- **Containerization**: Docker, Docker Compose
- **Orchestration**: Kubernetes
- **Monitoring**: Custom real-time dashboard

## 📁 Project Structure

```
mini-shop/
├── app.py                 # Main Flask application
├── log_generator.py       # Transaction log simulator
├── log_ai_monitor.py      # AI anomaly detection
├── run_all.py            # Multi-process runner
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Local container orchestration
├── k8s/                  # Kubernetes manifests
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   ├── secret.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── templates/            # HTML templates
│   ├── base.html
│   ├── index.html
│   ├── cart.html
│   ├── result.html
│   ├── monitor.html
│   └── error.html
├── static/               # Static assets
│   └── css/
│       └── style.css
├── scripts/              # Deployment scripts
│   ├── build.sh
│   ├── deploy.sh
│   └── local-run.sh
└── logs/                 # Application logs
```

## 🔧 Configuration

### Environment Variables

- `SECRET_KEY`: Flask secret key for sessions
- `PORT`: Main application port (default: 5000)
- `AI_MONITOR_PORT`: AI monitor port (default: 9000)
- `FLASK_ENV`: Environment mode (development/production)

### Kubernetes Configuration

The application includes comprehensive Kubernetes manifests:
- **Namespace**: Isolated environment
- **ConfigMap**: Environment configuration
- **Secret**: Sensitive data management
- **Deployment**: Application pods with health checks
- **Service**: Load balancing and service discovery
- **HPA**: Horizontal Pod Autoscaler for scaling
- **Ingress**: External access routing

## 📈 Scaling & Performance

- **Horizontal Scaling**: Automatic pod scaling based on CPU/memory usage
- **Load Balancing**: Built-in Kubernetes service load balancing
- **Health Checks**: Comprehensive liveness and readiness probes
- **Resource Management**: Defined CPU and memory limits
- **Persistent Logging**: Shared log storage across pods

## 🔒 Security Features

- **Anomaly Detection**: ML-based fraud detection
- **Input Validation**: Secure form handling
- **Session Management**: Secure session handling
- **Container Security**: Non-root user execution
- **Network Policies**: Kubernetes network isolation (configurable)

## 🚦 Health Monitoring

Health check endpoints:
- `GET /health` - Application health status
- `GET /stats` - AI monitoring statistics

## 📝 API Endpoints

### Main Application
- `GET /` - Product catalog
- `GET /cart` - Shopping cart
- `GET /add/<product_id>` - Add to cart
- `GET /checkout` - Process payment
- `GET /monitor` - Monitoring dashboard

### AI Monitor
- `GET /logs` - Real-time log data (JSON)
- `GET /stats` - System statistics (JSON)
- `GET /health` - Monitor health status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the logs: `kubectl logs -f deployment/mini-shop-deployment -n mini-shop`
- Monitor health: `curl http://localhost:5000/health`
- View AI stats: `curl http://localhost:9000/stats`

## 🎯 Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] User authentication and authorization
- [ ] Payment gateway integration
- [ ] Advanced ML models for anomaly detection
- [ ] Prometheus metrics integration
- [ ] Grafana dashboards
- [ ] CI/CD pipeline setup
- [ ] Multi-region deployment support
