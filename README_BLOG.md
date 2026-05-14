# Blog Sistema su Tortoise ORM ir Aerich

## Sukurti failai:
- `models.py` - BlogPost modelis
- `database.py` - DB konfigūracija
- `routers.py` - Blog CRUD endpoints
- `requirements.txt` - Python priklausomybės
- `pyproject.toml` - Aerich konfigūracija
- `docker-compose.yml` - Pridėtas PostgreSQL

## Kaip paleisti:

### 1. Paleisti Docker konteinerius:
```bash
docker-compose up -d
```

### 2. Įeiti į backend konteinerį:
```bash
docker exec -it fastapi-backend bash
```

### 3. Įdiegti priklausomybes:
```bash
pip install -r requirements.txt
```

### 4. Inicializuoti Aerich (tik pirmą kartą):
```bash
aerich init-db
```

### 5. Kurti naujas migracijas (po modelių pakeitimų):
```bash
aerich migrate --name "migration_name"
```

### 6. Pritaikyti migracijas:
```bash
aerich upgrade
```

## Deployment with Nginx

The project is configured to use Nginx as a reverse proxy for production deployment.

1.  **Build and Run:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Accessing the app:**
    - Frontend: `http://localhost` (served by Nginx)
    - Backend API: `http://localhost/api/` (proxied by Nginx)

3.  **Environment Variables:**
    - Update `STRIPE_SUCCESS_URL` and `STRIPE_CANCEL_URL` in `.env` to point to your production domain instead of `localhost`.

## E-Shop with Stripe

To enable the e-shop features on the home page:

1.  **Install dependencies:**
    - Backend: `pip install stripe`
    - Frontend: `npm install @stripe/stripe-js` (Optional, direct redirect used)

2.  **Configure Stripe:**
    - Add `STRIPE_SECRET_KEY` to your `.env` file.
    - Create products in your Stripe Dashboard and get their `Price ID`.

3.  **Seed Products:**
    - Run the seed endpoint: `POST /shop/seed-products` to add initial products to your database (update the `stripe_price_id` in `backend/shop_router.py` first).

4.  **Checkout Flow:**
    - Clicking "Buy Now" redirects users to a Stripe-hosted checkout page.
    - Success and Cancel URLs are configured in `.env`.

## API Endpoints:

- `GET /blog/` - Gauti visus blog įrašus
- `GET /blog/{post_id}` - Gauti vieną įrašą
- `POST /blog/` - Sukurti naują įrašą
- `PUT /blog/{post_id}` - Atnaujinti įrašą
- `DELETE /blog/{post_id}` - Ištrinti įrašą

## Pavyzdžiai:

### Sukurti blog įrašą:
```bash
curl -X POST "http://localhost:8000/blog/" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Mano pirmas įrašas",
    "content": "Tai yra turinys",
    "author": "Jonas",
    "published": true
  }'
```

### Gauti visus įrašus:
```bash
curl http://localhost:8000/blog/
```

## Dokumentacija:
- FastAPI Swagger UI: http://localhost:8000/docs
- Frontend: http://localhost:5173
