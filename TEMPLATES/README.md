# 🌐 Market Manifold — TEMPLATES

Boilerplate for common Market Manifold configurations.

| Template | Description | Use Case |
|----------|-------------|----------|
| `stock-room/` | Full stock room directory structure | New room setup |
| `custom-map/` | Custom ternary map implementation | Signal encoding |

### Using a Template

```bash
cp -r TEMPLATES/stock-room/ rooms/AAPL
cd rooms/AAPL
# Edit identity.toml with your ticker
./bin/build-maps --room AAPL
```
