## Jivo Chat wrapper for Chatlync

### Before start
Make sure to create .env file (use .env_example as a template)

Set JIVO_URL and JIVO_KEY

### For development:
```bash
docker-compose build
```
```bash
./start-dev.sh
```

### For production
```bash
docker-compose -f docker-compose-prod.yml build
```
```bash
./start-prod.sh
```