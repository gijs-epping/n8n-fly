# n8n on Fly.io

This repository provides instructions and configuration for hosting n8n on Fly.io. n8n is a workflow automation tool that allows you to connect various services and automate tasks.

![N8N Setup Process](assets/n8n-setup.png)

## Prerequisites

- A Fly.io account
- Fly CLI installed on your machine
- Basic knowledge of command line operations

## Installation

### 1. Install Fly.io CLI

For Windows, open PowerShell and run:

```powershell
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

For other operating systems, visit [Fly.io's installation guide](https://fly.io/docs/hands-on/install-flyctl/).

### 2. Launch Your n8n Instance

1. Clone this repository:
```bash
git clone https://github.com/gijs-epping/n8n-fly.git
cd n8n-fly
```

2. Launch your app with Fly.io:
```bash
fly launch
```

### 3. Configure Your Application

During the launch process, you'll need to configure several settings:

1. **App Name**: Choose a unique name for your application (e.g., "n8ntestonfly")
   - This will be used in your app's URL: `https://[app-name].fly.dev`

2. **Region**: Select your preferred region (e.g., "Amsterdam, Netherlands")
   - Choose a region close to your location for better performance

3. **Resources**: Default configuration includes:
   - Shared CPU (1x)
   - 1GB RAM
   - No additional services (Postgres, Redis, etc.)

4. **Environment Variables**: Make sure to set these in your `fly.toml`:
   - `N8N_HOST`: Must match your app URL
   - `WEBHOOK_URL`: Must match your app URL

### 4. Important Notes

- The application will automatically stop when idling to save resources
- Your app will be accessible at `https://[app-name].fly.dev`
- First-time access will require setting up an owner account

## Configuration Reference

### fly.toml Example

```toml
app = "n8ntestonfly"  # Your unique app name
primary_region = "ams" # Your chosen region
```

### Access Your Application

After deployment, you can access your n8n instance at:
```
https://[app-name].fly.dev/
```

## First-Time Setup

1. Visit your newly deployed app URL
2. Complete the owner account setup:
   - Enter your email
   - Create a secure password (8+ characters, including numbers and capital letters)
   - Fill in your first and last name

## Troubleshooting

If you encounter issues:

1. Check your fly.toml configuration
2. Verify your environment variables
3. Ensure your app name and URLs match in all configurations
4. Check Fly.io's status page for any ongoing issues

## Support

For support, please:

- Check the [n8n documentation](https://docs.n8n.io/)
- Visit the [Fly.io documentation](https://fly.io/docs/)
- Open an issue in this repository

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

[MIT License](LICENSE)