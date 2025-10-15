# Tailwind setup for Consignify (Indie Teal & Coral)

## 1) Install toolchain
```bash
# in your Django project root
npm install
```

## 2) Build CSS
Development (watch):  
```bash
npm run dev:css
```
One‑off/minified build:  
```bash
npm run build:css
```

The compiled CSS will be written to `static/css/tailwind.css`.

## 3) Wire into Django
In `templates/base.html`, remove the Tailwind CDN script and add:
```django
{% load static %}
<link rel="stylesheet" href="{% static 'css/tailwind.css' %}">
```

## 4) Use the new tokens
- Primary button: `<button class="btn">Save</button>`
- Outline button: `<button class="btn-outline">Cancel</button>`
- Card: `<div class="card">...</div>`
- Alerts: `alert-success | alert-warn | alert-error`
- Background/text handled globally via `@layer base`

## Notes
- Colors available as utilities: `bg-background`, `bg-surface`, `text-text`, `border-muted`, `bg-primary`, `hover:bg-primary-700`, `text-accent`, etc.
- Content globs include `templates/**/*.html` and `**/templates/**/*.html` to cover app templates.
- For production: run `npm run build:css` and ensure static files are collected for Whitenoise or your web server.
