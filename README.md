# Echelon Pricing MVP

This is a demo prototype of a low-integration pricing automation tool for small and mid-market 3PLs and freight brokers.

## What is included

- Next.js + TypeScript + Tailwind CSS frontend
- Seeded local persistence via Prisma + SQLite
- API route to generate and save quotes
- Core workflow: landing page → create quote → save → history → shipper profile
- Rules-based quote engine with lane history, distance estimate, shipper bias, and confidence scoring

## Key pages

- `/` — Landing page with demo positioning
- `/login` — Mock login page for demo flow
- `/dashboard` — Business metrics and recent quote snapshot
- `/quote/new` — Create a new quote and generate pricing recommendation
- `/quotes` — View saved quote history
- `/shippers/[id]` — Customer profile and recent pricing history
- `/settings` — Simple admin/settings overview

## Setup

1. Install dependencies

   ```bash
   npm install
   ```

2. Seed the local database

   ```bash
   npm run seed
   ```

3. Start the app

   ```bash
   npm run dev
   ```

4. Open `http://localhost:3000`

## Demo flow

1. Open the dashboard to orient judges to saved quote volume, average margin, and top lanes.
2. Click **Create quote**.
3. Enter origin/destination, pickup date, equipment, weight, and shipper.
4. Click **Generate quote** to see the recommended sell rate, carrier cost, margin, and confidence score.
5. Save the quote and verify it appears in **Quote history**.
6. Open a shipper profile to show pricing rationale and common lanes.

## Prototype notes

- The engine is intentionally simple and explainable.
- The product is built for demo clarity and rapid pricing decisions.
- No external TMS or enterprise auth is required.
