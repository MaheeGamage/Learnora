# README.md

# Nginx Reverse Proxy Setup for API

This project includes a script to automatically install and configure **Nginx** as a reverse proxy for an API running on `127.0.0.1:8000`.

The default configuration:

* Routes all traffic through Nginx
* Blocks the `/register` endpoint to prevent public account creation
* Keeps all other API endpoints accessible
* Creates a clean Nginx config under `/etc/nginx/sites-available/api`

## 1. Running the Setup Script

The script installs Nginx, creates the reverse proxy config, enables it, and reloads Nginx safely.

### Usage

1. Save the script as `nginx_setup.sh`.
2. Make it executable:

```bash
chmod +x nginx_setup.sh
```

3. Run it:

```bash
./nginx_setup.sh
```

After running, Nginx will route requests to your API, and `/register` will be blocked.

## 2. Nginx Config Location

Configuration file:

```
/etc/nginx/sites-available/api
```

Enabled via symlink:

```
/etc/nginx/sites-enabled/api
```

The default Nginx site is removed automatically.

## 3. Blocking an Endpoint

The `/register` endpoint is blocked by default:

```nginx
location /register {
    return 403;
}
```

To block additional endpoints:

1. Open the config:

```bash
sudo nano /etc/nginx/sites-available/api
```

2. Add a new block:

```nginx
location /new-endpoint {
    return 403;
}
```

3. Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Blocking Multiple Endpoints

To block multiple endpoints at once, add multiple location blocks in the config:

```nginx
location /register {
    return 403;
}

location /admin {
    return 403;
}

location /delete-account {
    return 403;
}
```

You can also use regex to block patterns:

```nginx
location ~ ^/(register|admin|delete-account) {
    return 403;
}
```

This blocks all three endpoints with a single rule.

## 4. Unblocking an Endpoint

To unblock `/register` or any blocked route:

1. Open the config:

```bash
sudo nano /etc/nginx/sites-available/api
```

2. Comment out or remove the block:

```nginx
# location /register {
#     return 403;
# }
```

3. Reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

The endpoint will be accessible immediately.

## 5. Reloading Nginx Safely

Always test config changes before reloading:

```bash
sudo nginx -t
```

Expected output:

```
syntax is ok
test is successful
```

Reload Nginx:

```bash
sudo systemctl reload nginx
```

## 6. Resetting Nginx (Optional)

If needed, remove and reinstall Nginx:

```bash
sudo apt remove nginx nginx-common -y
sudo apt purge nginx nginx-common -y
sudo rm -rf /etc/nginx
sudo apt install nginx -y
```

Then rerun the setup script.

## Summary

| Feature                      | Supported |
| ---------------------------- | --------- |
| Install Nginx automatically  | ✔️        |
| Create reverse proxy config  | ✔️        |
| Block `/register` by default | ✔️        |
| Easy manual unblock          | ✔️        |
| Safe reload without downtime | ✔️        |
