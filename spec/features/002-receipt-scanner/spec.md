# 002 · Receipt Scanner

**Status:** proposed

## What it does

The user uploads a photo of a supermarket receipt. The app sends the image 
to Gemini 2.5 Flash Vision, which extracts every item with its name, quantity, 
unit price, total price, and category. The extracted data is saved to the 
database as a Receipt with its associated Items and returned to the frontend.

## Why

This is the core feature of Canasta — without it, nothing else works. 
Every other feature (history, dashboard, trends) depends on data 
that only exists if receipts can be scanned and saved.

## Acceptance Criteria

- [ ] `POST /api/receipts/scan` accepts a receipt image as multipart/form-data.
- [ ] The image is sent to Gemini 2.5 Flash Vision with a structured prompt.
- [ ] Gemini returns at minimum: store name, date, list of items 
      (name, quantity, unit price, total price, category).
- [ ] Each item's category is one of the 14 valid Category enum values.
- [ ] The Receipt and all Items are saved to the database in a single transaction.
- [ ] The endpoint returns the created Receipt with its Items as JSON.
- [ ] If Gemini cannot read the receipt, the endpoint returns a clear 
      user-friendly error: "Could not read the receipt. Please upload a clearer photo."
- [ ] If the image is not a valid image file, the endpoint returns 400 
      with a clear message.
- [ ] The image is never saved to disk — only processed in memory.
- [ ] `POST /api/receipts/scan` has at least one integration test.

## Out of Scope

- Manual correction of extracted items (feature idea for v2).
- Support for non-supermarket receipts.
- Batch scanning of multiple receipts at once (v2).
- Frontend upload UI (feature 003).
