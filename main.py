from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from asteval import Interpreter, make_symbol_table
from datetime import datetime, timedelta
from typing import Any, Dict

app = FastAPI()

# Crear symbol table segura, sin bucles ni operaciones peligrosas
safe_symbols = make_symbol_table(
    to_date=lambda s, fmt="%Y-%m-%d %H:%M:%S": datetime.strptime(s, fmt),
    substring=lambda s, i, j: s[i:j],
    upper=lambda s: s.upper(),
    lower=lambda s: s.lower(),
    len=len,
    isinstance=isinstance,
    int=int,
    float=float,
    str=str,
    bool=bool,
    timedelta=timedelta
)

# Instanciar el intérprete con símbolos seguros
interpreter = Interpreter(symtable=safe_symbols, use_numpy=False)

class EvalRequest(BaseModel):
    context: Dict[str, Any]
    rule: str

@app.post("/evaluate")
def evaluate_rule(req: EvalRequest):
    try:
        # Limpiar y actualizar el contexto del intérprete
        interpreter.symtable.update(req.context)
        result = interpreter(req.rule)

        # Validar que el resultado sea un valor primitivo
        if not isinstance(result, (bool, int, float, str)):
            raise ValueError("La regla no devolvió un resultado válido.")

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error evaluando la regla: {str(e)}")
