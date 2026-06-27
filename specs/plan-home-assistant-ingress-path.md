# Home Assistant Ingress Path Plan

## Goal

Fix the Home Assistant sidebar blank screen while preserving direct root-based access such as `familymenu.kmcleod.com`.

## Diagnosis

The Angular build currently emits `<base href="/">`, root-relative script/style URLs, absolute router links, and API calls to `/api/v1`. This works when the app is mounted at the domain root, but Home Assistant ingress serves add-ons under a generated subpath. Root-relative URLs can escape that subpath and load the wrong scripts, styles, favicon, routes, or API endpoints, producing a blank sidebar page.

## Scope

- Make the frontend safe to serve from either `/` or a Home Assistant ingress subpath.
- Keep direct reverse-proxy access at `familymenu.kmcleod.com` working.
- Keep the existing API route names under `/api/v1` for root access.
- Do not add Home Assistant-specific authentication logic in the app.

## Backend Tasks

1. Add prefixed API aliases for ingress-style paths.
   - Existing `/api/v1/...` routes remain unchanged.
   - Requests under an arbitrary prefix ending in `/api/v1/...` should route to the same API behavior.
   - SPA fallback should still return `index.html` for frontend routes under either root or an ingress prefix.
   - Static files such as JS, CSS, favicon, and assets should be served when requested under root or an ingress prefix.

2. Add backend tests.
   - Root `/api/v1/...` still works.
   - Prefixed `/some/ingress/path/api/v1/...` works.
   - Prefixed `/some/ingress/path/weekly-plan` returns the Angular `index.html`.
   - Prefixed static bundle requests return files when the file exists.

## Frontend Tasks

1. Build Angular with relative document base.
   - Change `<base href="/">` to a relative base so browser-loaded chunks and styles stay under the current ingress path.

2. Keep Angular router links base-aware.
   - Keep app-root router links where appropriate because Angular resolves them against the document base.
   - Avoid plain relative links that could nest under the current route, such as `/meal-catalog/history`.

3. Resolve API and export URLs relative to the current document base.
   - Replace hardcoded `/api/v1` calls with a helper that resolves `api/v1` relative to `document.baseURI`.
   - Replace export URL `/api/v1/export` with the same base-aware resolution.

## Verification

- `npm run build`.
- Full backend test suite.
- Browser smoke test for root access.
- Browser smoke test for a simulated ingress prefix path such as `/local_ingress/family_menu/`.
- Confirm the simulated prefixed app loads, renders the Weekly Plan screen, and calls the prefixed API without console errors.

## Risks

- Angular relative routing can be sensitive to trailing slashes. Tests and browser smoke checks should include a prefix ending in `/`.
- Home Assistant's actual ingress path may include generated tokens; the implementation should avoid hardcoding a known prefix.
- Direct root access should continue to use `/api/v1` through relative resolution from `/`.
