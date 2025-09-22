import re

# Leer el archivo
with open('src-alpespartner/campanias/modulos/dominio/eventos.py', 'r') as f:
    content = f.read()

# Patrones para corregir dataclasses que heredan de EventoDominio
patterns = [
    (r'(\w+): str(?!\s*=)', r'\1: str = ""'),
    (r'(\w+): float(?!\s*=)', r'\1: float = 0.0'),
    (r'(\w+): int(?!\s*=)', r'\1: int = 0'),
    (r'(\w+): datetime(?!\s*=)', r'\1: datetime = None'),
    (r'(\w+): bool(?!\s*=)', r'\1: bool = False'),
]

# Aplicar las correcciones
for pattern, replacement in patterns:
    content = re.sub(pattern, replacement, content)

# Escribir el archivo corregido
with open('src-alpespartner/campanias/modulos/dominio/eventos.py', 'w') as f:
    f.write(content)

print('Eventos corregidos')