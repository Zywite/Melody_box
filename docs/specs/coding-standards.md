# Spec: coding-standards

Scope: feature

# Estándares de Código — MelodyBox

## Propósito
Definir estándares consistentes para todo el código nuevo y refactorizado del proyecto, asegurando que se mantengan los principios Clean Code después de la refactorización.

---

## Backend (Python / FastAPI)

### PEP 8 obligatorio
- `snake_case` para variables, funciones, métodos
- `PascalCase` para clases
- `UPPER_CASE` para constantes de módulo
- 4 espacios para indentación (nunca tabs)
- Máximo 88 caracteres por línea (Black default)
- Dos líneas en blanco entre clases; una entre funciones

### Type hints
- Toda función pública debe tener tipo de retorno
- Todo parámetro debe tener type hint
- Usar `Optional[T]` o `T | None` consistentemente (elegir uno)
- Usar `list[T]` en vez de `List[T]` (Python 3.9+)

### Estructura de archivos
```
app/
  routes/       → Solo manejo HTTP (validación, respuestas)
  services/     → Lógica de negocio pura (sin dependencia HTTP)
  models/       → Modelos SQLAlchemy
  core/         → Config, DB, seguridad, utilidades
```

### Reglas
- **NUNCA** duplicar lógica de negocio entre routes y services
- **NUNCA** queries DB directas en routes (usar services)
- **NUNCA** `except Exception: pass` sin al menos `logger.exception()`
- **NUNCA** imports dentro de funciones (salvo circular dependency inevitable)
- **SIEMPRE** usar logger en vez de print
- **SIEMPRE** constantes con nombre (sin magic numbers/strings)
- **SIEMPRE** docstring en funciones públicas no-triviales

### Servicios
- Cada entidad de negocio tiene su propio service class
- Los services no conocen HTTP (no reciben Request/Response)
- Inyectar `db: Session` como primer parámetro

---

## Frontend (Vue 3 / JavaScript)

### Convenciones de nombres
- Componentes: `PascalCase.vue`
- Archivos de composables: `useNombre.js` (camelCase)
- Stores: `useNombreStore.js` en `stores/`
- Utilidades: `nombre.js` en `utils/`

### Estructura de componentes
```
componentes < 400 líneas
  template  < 100 líneas
  script    < 200 líneas
  style     < 100 líneas
```

### Reglas
- **NUNCA** mutar store desde fuera del store (usar acciones siempre)
- **NUNCA** `console.log` en producción (usar logger o debug flag)
- **NUNCA** `confirm()` nativo (usar modal component)
- **NUNCA** colores hardcodeados en JS/CSS (usar variables CSS del tema)
- **SIEMPRE** lógica reutilizable en composables
- **SIEMPRE** props/emits en componentes presentacionales (no acceder store directo)
- **SIEMPRE** `toast.error()` para errores de usuario (no solo `console.error`)
- **SIEMPRE** import con alias `@/` en vez de rutas relativas (`../`)

### Composición vs Opciones API
- Usar `<script setup>` en todos los componentes nuevos
- Usar Composition API + Pinia para estado

### CSS
- Estilos globales en `main.css` (nunca duplicados en scoped)
- `@keyframes` comunes en `main.css`
- No duplicar `.empty-state`, `.spinner`, `.section-title` en cada componente
- Preferir clases utilitarias Tailwind; CSS propio solo cuando Tailwind no alcanza

---

## Tests (pytest)

### Estructura
```
tests/
  unit/         → Sin DB, sin HTTP (services puros)
  integration/  → API vía TestClient
  e2e/          → Flujos completos multi-paso
  helpers.py    → Funciones compartidas (mocks, fixtures, engine setup)
```

### Reglas
- **NUNCA** tests que pasan sin ejecutar assertions (quitar `if result:` guard)
- **NUNCA** `pytest.raises(Exception)` sin especificar excepción
- **NUNCA** assertions bilingües (elegir un idioma o asertar solo status code)
- **NUNCA** imports inline (`__import__` o `import` dentro de función)
- **NUNCA** `conftest.py` con efectos secundarios al importarse
- **SIEMPRE** fixtures para datos repetidos (mock dicts, credenciales, IDs)
- **SIEMPRE** nombres descriptivos: `test_<metodo>_<escenario>`
- **SIEMPRE** mock a nivel de fixture, no global

---

## Proceso de revisión

### Checklist antes de mergear
- [ ] Sin código duplicado
- [ ] Type hints completos
- [ ] Sin console.logs / prints
- [ ] Sin `except Exception: pass`
- [ ] Sin mutaciones directas de store
- [ ] Componentes < 400 líneas
- [ ] Tests pasan con assertions reales
- [ ] Sin imports sin usar
- [ ] Sin números mágicos
- [ ] Sin colores hardcodeados

### Linters y formateadores
- Backend: `ruff check`, `ruff format`, `mypy --strict`
- Frontend: `eslint`, `prettier`
- Ejecutar antes de cada commit (git hook pre-commit)